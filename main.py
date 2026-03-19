import sys
import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from agent.agent import compiled_graph

load_dotenv()

def run_agent(user_input: str):
    """Entry point to run the JobMatch AI agent."""
    initial_state = {
        "messages": [HumanMessage(content=user_input)],
        "iteration_count": 0,
        "candidate_name": "",
        "job_description": "",
        "final_recommendation": ""
    }
    
    # Process the graph
    final_response = None
    for event in compiled_graph.stream(initial_state):
        for node, values in event.items():
            print(f"\n--- Node: {node} ---")
            for msg in values.get("messages", []):
                if hasattr(msg, 'content'):
                    # Truncate long content for display
                    content = msg.content
                    if len(content) > 200:
                        content = content[:200] + "..."
                    print(f"Message: {content}")
                    if node == "agent" and not hasattr(msg, 'tool_calls'):
                        final_response = msg.content
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    for tool_call in msg.tool_calls:
                        print(f"Tool Call: {tool_call['name']}({tool_call['args']})")
                        
    if final_response:
        print("\n--- Final Recommendation ---")
        print(final_response)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
    else:
        user_input = input("Enter your command for JobMatch AI: ")
    
    run_agent(user_input)
