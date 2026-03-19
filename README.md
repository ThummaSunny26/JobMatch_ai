# JobMatch AI - Professional Candidate Evaluator

JobMatch AI is an autonomous recruitment assistant that evaluates candidates against job descriptions using AI-powered search, scoring, and database management.

## 🚀 Features

- **Autonomous Agent**: Uses LangGraph and LangChain with a ReAct (Thought → Action → Observation) reasoning loop.
- **Web Search**: Automatically discovers candidate profiles on LinkedIn, GitHub, and portfolios using Tavily API.
- **AI Scoring**: Evaluates candidates based on skills, experience, and role fit with detailed strengths and gaps analysis.
- **Modern UI**: Professional Streamlit dashboard for real-time evaluation tracking and data visualization.
- **Candidate Database**: Built-in SQLite storage to track evaluation history and top performers.

## 🛠️ Tech Stack

- **Orchestration**: LangGraph, LangChain
- **LLM**: OpenAI GPT-4o-mini (via LangChain-OpenAI)
- **Search**: Tavily API
- **Database**: SQLite
- **Front-end**: Streamlit, Pandas, Plotly
- **Language**: Python 3.10+

## 🏁 Getting Started

### Prerequisites

- Python 3.10 or higher
- API Keys: OpenAI API Key and Tavily API Key

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd life_frontend
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=your_openai_key
   TAVILY_API_KEY=your_tavily_key
   OPENAI_MODEL=gpt-4o-mini
   OPENAI_TEMPERATURE=0
   ```

4. **Initialize the database**:
   The app will automatically create the database on first run, but you can run the migration script if updating from an older version:
   ```bash
   python migrate_db.py
   ```

### Running the App

Start the Streamlit dashboard:
```bash
streamlit run app.py
```

## 📂 Project Structure

- `app.py`: Main Streamlit application.
- `agent/`: Core agent logic and prompts.
- `tools/`: Individual tool implementations (Search, Scorer, DB).
- `data/`: SQLite database storage.
- `migrate_db.py`: Database schema migration utility.

---
Built with ❤️ by JobMatch AI Team
