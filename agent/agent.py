import operator
from typing import Annotated, TypedDict, Union, List, Dict
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from tools.web_search import web_search
from tools.jd_scorer import jd_scorer
from tools.db_tool import db_insert, db_select, db_list, db_top, db_delete
from agent.prompts import SYSTEM_PROMPT
import os
import json
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from the project root
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    iteration_count: int
    candidate_name: str
    job_description: str
    final_recommendation: str

# Define Tools for the agent
@tool
def search_candidate(query: str):
    """Search for candidate information online (LinkedIn, GitHub, etc.)."""
    logger.info(f"Tool Call: search_candidate with query: {query}")
    return web_search(query)

@tool
def score_candidate(candidate_info: str, job_description: str, context_hints: Union[str, None] = None):
    """Evaluate candidate profile against a job description. Returns score, strengths, gaps, and recommendation."""
    logger.info("Tool Call: score_candidate")
    return jd_scorer(candidate_info, job_description, context_hints)

@tool
def insert_candidate_record(name: str, score: int, strengths: str, gaps: str, recommendation: str, profile_url: str):
    """Saves candidate evaluation to the database."""
    logger.info(f"Tool Call: insert_candidate_record for {name}")
    return db_insert(name, score, strengths, gaps, recommendation, profile_url)

@tool
def select_candidate_record(name: str):
    """Retrieves candidate record from the database."""
    logger.info(f"Tool Call: select_candidate_record for {name}")
    return db_select(name)

@tool
def list_all_candidates():
    """Lists all evaluated candidates from the database."""
    logger.info("Tool Call: list_all_candidates")
    return db_list()

@tool
def get_top_candidates(limit: int = 3):
    """Fetches the top-scoring candidates from the database."""
    logger.info(f"Tool Call: get_top_candidates with limit: {limit}")
    return db_top(limit)

@tool
def delete_candidate_record(name: str):
    """Deletes a candidate record from the database."""
    logger.info(f"Tool Call: delete_candidate_record for {name}")
    return db_delete(name)

tools = [
    search_candidate,
    score_candidate,
    insert_candidate_record,
    select_candidate_record,
    list_all_candidates,
    get_top_candidates,
    delete_candidate_record
]

api_key = os.getenv("OPENAI_API_KEY")
model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
base_url = None
if api_key and api_key.startswith("sk-or-v1"):
    base_url = "https://openrouter.ai/api/v1"
    # For OpenRouter, ensure model name is prefixed correctly if it's not already
    if "/" not in model_name:
        model_name = f"openai/{model_name}"

model = ChatOpenAI(
    model=model_name, 
    temperature=0,
    openai_api_key=api_key,
    base_url=base_url
).bind_tools(tools)

def agent_node(state: AgentState):
    """The agent node that generates the thought and chooses an action."""
    messages = state["messages"]
    # Add SystemMessage if it's the first turn, including current context
    if not any(isinstance(m, SystemMessage) for m in messages):
        context_prompt = f"{SYSTEM_PROMPT}\n\nCURRENT CONTEXT:\nCandidate: {state.get('candidate_name')}\nJob Description: {state.get('job_description')}"
        messages = [SystemMessage(content=context_prompt)] + messages
        
    response = model.invoke(messages)
    
    # Update iteration count
    return {
        "messages": [response],
        "iteration_count": state.get("iteration_count", 0) + 1
    }

def tool_node(state: AgentState):
    """The node that executes the chosen tool."""
    messages = state["messages"]
    last_message = messages[-1]
    
    tool_messages = []
    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        
        # Mapping tool names to functions
        tool_func = {
            "search_candidate": search_candidate,
            "score_candidate": score_candidate,
            "insert_candidate_record": insert_candidate_record,
            "select_candidate_record": select_candidate_record,
            "list_all_candidates": list_all_candidates,
            "get_top_candidates": get_top_candidates,
            "delete_candidate_record": delete_candidate_record
        }[tool_name]
        
        observation = tool_func.invoke(tool_args)
        tool_messages.append(ToolMessage(
            tool_call_id=tool_call["id"],
            content=json.dumps(observation)
        ))
        
    return {"messages": tool_messages}

def router(state: AgentState):
    """Determines the next step in the graph."""
    messages = state["messages"]
    last_message = messages[-1]
    
    # Check for max iterations
    if state.get("iteration_count", 0) >= 8:
        return END
        
    if last_message.tool_calls:
        return "tools"
    
    return END

# Build the Graph
workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)

workflow.set_entry_point("agent")

workflow.add_conditional_edges(
    "agent",
    router,
    {
        "tools": "tools",
        END: END
    }
)

workflow.add_edge("tools", "agent")

compiled_graph = workflow.compile()
