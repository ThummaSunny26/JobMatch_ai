# JobMatch AI: Autonomous Candidate Evaluation Agent

JobMatch AI is a production-ready, autonomous recruitment assistant designed to streamline the candidate evaluation process. Leveraging **LangGraph** and **LangChain**, the agent follows a **ReAct** (Reasoning and Action) pattern to discover, score, and manage candidate data through a single, natural-language interface.

## 🚀 Key Features

- **Autonomous Decision Making**: Follows a robust `Thought → Action → Observation` loop to handle complex recruitment requests end-to-end.
- **Intelligent Web Discovery**: Integrated with **Tavily Search API** to automatically locate professional profiles across LinkedIn, GitHub, and personal portfolios.
- **Precision AI Scoring**: Uses LLMs to evaluate candidate profiles against job descriptions, providing a 0-100 score, identified strengths, and key skill gaps.
- **Interactive Dashboard**: A modern **Streamlit** front-end featuring:
  - **Live Evaluation Tracking**: Watch the agent's reasoning process in real-time.
  - **Candidate Database**: Full history of evaluations with searchable and filterable records.
  - **Performance Analytics**: Visual score charts and top-performer rankings.
- **Robust Data Management**: Built-in **SQLite** database with automated schema migrations and timestamped record tracking.

## 🧠 Technical Deep Dive (Submission Review)

During the submission review, the following core concepts are key to understanding the agent's behavior:

### 1. Prompting Techniques & ReAct Pattern
The system prompt in [prompts.py](file:///c:/Users/Admin/Desktop/Job_Match_AI/agent/prompts.py) uses the **ReAct framework** to guide the agent:
- **Identity**: Sets the persona as "JobMatch AI", an autonomous recruiter.
- **Workflow**: Provides a step-by-step logic (Search → Score → Save → Verify) to minimize hallucinations.
- **Constraint-Based Scoring**: Defines specific numeric ranges for edge cases (e.g., 40-55 for missing profiles) to ensure consistent evaluation.

### 2. How the Prompt Guides Tools
The agent uses **LLM tool binding** (function calling). The model decides which tool to call based on the docstrings and argument schemas defined in [agent.py](file:///c:/Users/Admin/Desktop/Job_Match_AI/agent/agent.py). For example, if the agent's "Thought" determines it needs to find a LinkedIn profile, it automatically identifies the `search_candidate` tool as the matching action.

### 3. Agentic Flow (LangGraph)
The flow is orchestrated in [agent.py](file:///c:/Users/Admin/Desktop/Job_Match_AI/agent/agent.py) using a `StateGraph`:
- **State**: A `TypedDict` that tracks the message history, iteration count, and evaluation data.
- **Nodes**: 
    - `agent_node`: Responsible for reasoning and generating tool calls or final responses.
    - `tool_node`: Executes the requested tools and returns observations to the agent.
- **Conditional Edge**: The `router` function checks if the LLM generated `tool_calls`. If yes, it routes to `tools`; if no, it routes to `END`.
- **The Loop**: The cycle between `agent` and `tools` continues until the agent provides a final recommendation or hits the 8-iteration limit.

## 🛠️ Tech Stack

- **Orchestration**: LangGraph, LangChain
- **LLM**: OpenAI GPT-4o-mini (or compatible via OpenRouter)
- **Search Engine**: Tavily Advanced Search
- **Frontend**: Streamlit, Plotly, Pandas
- **Storage**: SQLite
- **Environment**: Python 3.10+

## 📂 Project Structure

- [app.py](file:///c:/Users/Admin/Desktop/Job_Match_AI/app.py): The main Streamlit dashboard and UI logic.
- [agent/](file:///c:/Users/Admin/Desktop/Job_Match_AI/agent/):
  - [agent.py](file:///c:/Users/Admin/Desktop/Job_Match_AI/agent/agent.py): Core LangGraph workflow and node definitions.
  - [prompts.py](file:///c:/Users/Admin/Desktop/Job_Match_AI/agent/prompts.py): System prompts and ReAct instructions.
- [tools/](file:///c:/Users/Admin/Desktop/Job_Match_AI/tools/):
  - [web_search.py](file:///c:/Users/Admin/Desktop/Job_Match_AI/tools/web_search.py): Interface for Tavily API discovery.
  - [jd_scorer.py](file:///c:/Users/Admin/Desktop/Job_Match_AI/tools/jd_scorer.py): LLM-based evaluation logic.
  - [db_tool.py](file:///c:/Users/Admin/Desktop/Job_Match_AI/tools/db_tool.py): SQLite database operations.
- [migrate_db.py](file:///c:/Users/Admin/Desktop/Job_Match_AI/migrate_db.py): Utility for database schema updates.

## 🏁 Getting Started

### Prerequisites

- Python 3.10 or higher.
- API keys for **OpenAI** (or OpenRouter) and **Tavily**.

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Job_Match_AI
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**:
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=your_openai_key
   TAVILY_API_KEY=your_tavily_key
   OPENAI_MODEL=gpt-4o-mini
   OPENAI_TEMPERATURE=0
   ```

4. **Initialize Database**:
   ```bash
   python migrate_db.py
   ```

### Running the Application

Launch the Streamlit dashboard:
```bash
streamlit run app.py
```

## ⚖️ Scoring Guidelines

The agent follows strict evaluation criteria:
- **Good Match**: Score 70+ with clear alignment of skills and experience.
- **Insufficient Info**: Score 40-55 if no online profile is discovered (requests resume).
- **Poor Match**: Score <30 for candidates in unrelated fields.

---
Developed for JobMatch AI Submission
