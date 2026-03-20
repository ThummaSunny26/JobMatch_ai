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

## 🧠 Agentic Flow & Architecture

The agent's intelligence is built on a structured **StateGraph** that orchestrates the following flow:

1.  **State Management**: Uses `AgentState` to track message history, iteration counts, and candidate metadata.
2.  **The Graph**:
    - **Agent Node**: Processes the current state using a sophisticated system prompt and the ReAct pattern.
    - **Tool Node**: Executes requested actions (Search, Score, Database operations) and returns observations.
    - **Conditional Routing**: A router determines if the agent needs more information (loop to tools) or has reached a final recommendation.
3.  **Prompting Strategy**:
    - **Instructional Guidance**: The system prompt provides a clear 6-step workflow for the agent to follow.
    - **Constraint Handling**: Includes explicit rules for scoring when data is missing or mismatched.
    - **Safety Loops**: Implements a maximum iteration limit (8) to ensure predictable termination.

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
