import streamlit as st
import pandas as pd
import plotly.express as px
import os
import time
from dotenv import load_dotenv

# Load environment variables before importing other modules that depend on them
load_dotenv()

from langchain_core.messages import HumanMessage
from agent.agent import compiled_graph
from tools.db_tool import db_list, db_top, db_delete

# Page configuration
st.set_page_config(
    page_title="JobMatch AI | Candidate Evaluator",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for a more professional look
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #007bff;
        color: white;
    }
    .stExpander {
        background-color: white;
        border-radius: 5px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 10px;
    }
    .candidate-card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: white;
        color: #1f1f1f; /* Force dark text for visibility on white background */
        border-left: 5px solid #007bff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    .candidate-card h3, .candidate-card p, .candidate-card strong {
        color: #1f1f1f !important;
    }
    .candidate-card a {
        color: #007bff !important;
        text-decoration: none;
    }
    .candidate-card a:hover {
        text-decoration: underline;
    }
    .score-badge {
        font-size: 1.5rem;
        font-weight: bold;
        color: #007bff;
    }
    /* Ensure text visibility in status and expanders */
    [data-testid="stStatusWidget"], [data-testid="stExpander"] {
        color: #1f1f1f !important;
    }
    [data-testid="stStatusWidget"] p, [data-testid="stExpander"] p, [data-testid="stExpander"] span {
        color: #1f1f1f !important;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to refresh candidate data
def get_candidate_data():
    candidates = db_list()
    if not candidates:
        return pd.DataFrame(columns=["Name", "Score", "Recommendation", "Profile URL", "Date"])
    
    # Map dictionary keys to user-friendly column names
    formatted_data = []
    for c in candidates:
        formatted_data.append({
            "Name": c.get("name"),
            "Score": c.get("score"),
            "Strengths": c.get("strengths"),
            "Gaps": c.get("gaps"),
            "Recommendation": c.get("recommendation"),
            "Profile URL": c.get("profile_url"),
            "Date": c.get("created_at")
        })
    return pd.DataFrame(formatted_data)

# Sidebar
with st.sidebar:
    st.title("💼 JobMatch AI")
    st.markdown("---")
    
    menu = st.radio("Navigation", ["Evaluate Candidate", "Candidate Database", "Top Candidates"])
    
    st.markdown("---")
    st.subheader("Quick Stats")
    candidates_df = get_candidate_data()
    if not candidates_df.empty:
        st.metric("Total Candidates", len(candidates_df))
        st.metric("Avg Score", f"{candidates_df['Score'].mean():.1f}")
    else:
        st.info("No candidates evaluated yet.")

# Main Content
if menu == "Evaluate Candidate":
    st.title("🚀 Evaluate New Candidate")
    st.markdown("Provide a candidate name and a brief description of the role to start the AI-powered evaluation.")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        with st.form("evaluation_form"):
            user_query = st.text_area("Candidate & Role Description", placeholder="e.g. Evaluate John Doe for a Python Developer role with focus on Django", height=150)
            submit_button = st.form_submit_button("Start Evaluation")
    
    with col2:
        if submit_button:
            if not user_query:
                st.error("Please provide a request for the agent.")
            else:
                st.subheader(f"Processing Request")
                
                # Placeholder for agent thoughts
                thought_container = st.container()
                status_placeholder = st.empty()
                
                initial_state = {
                    "messages": [HumanMessage(content=user_query)],
                    "iteration_count": 0,
                    "candidate_name": "",
                    "job_description": "",
                    "final_recommendation": ""
                }
                
                final_response = None
                try:
                    with st.status("Agent is working...", expanded=True) as status:
                        for event in compiled_graph.stream(initial_state):
                            for node, values in event.items():
                                for msg in values.get("messages", []):
                                    if hasattr(msg, 'content') and msg.content:
                                        content = msg.content
                                        
                                        # Only show content inside the status box for thoughts or tool results
                                        if node == "agent":
                                            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                                                # Agent is calling tools
                                                for tool_call in msg.tool_calls:
                                                    status.write(f"🤔 **Thought:** Seeking more info...")
                                                    status.write(f"🛠️ **Calling Tool:** `{tool_call['name']}`")
                                            else:
                                                # Agent's final message or a simple thought
                                                final_response = content
                                                status.write("✅ **Finalizing recommendation...**")
                                        
                                        elif node == "tools":
                                             # Tool results - show briefly or collapsed
                                             with status:
                                                 with st.expander("🔍 Tool Result Detail"):
                                                     st.write(content)
                        status.update(label="Evaluation Complete!", state="complete", expanded=False)
                except Exception as e:
                    st.error(f"An error occurred during evaluation: {str(e)}")
                    st.exception(e)
                
                if final_response:
                    st.success("### Final Recommendation")
                    st.markdown(final_response)
                    
                    # Try to fetch the newly saved record for visualization
                    latest_df = get_candidate_data()
                    candidate_record = latest_df.iloc[-1] if not latest_df.empty else None
                    
                    if candidate_record is not None:
                        st.markdown("---")
                        c1, c2 = st.columns(2)
                        with c1:
                            st.metric("Overall Score", f"{candidate_record['Score']}/100")
                            # Simple Gauge-like chart
                            fig = px.pie(values=[candidate_record['Score'], 100-candidate_record['Score']], 
                                        names=['Score', 'Remaining'],
                                        hole=0.7,
                                        color_discrete_sequence=['#007bff', '#e9ecef'])
                            fig.update_traces(textinfo='none')
                            fig.update_layout(showlegend=False, height=200, margin=dict(t=0, b=0, l=0, r=0))
                            st.plotly_chart(fig, on_select="ignore")
                        with c2:
                            st.markdown(f"**Strengths:**\n{candidate_record['Strengths']}")
                            st.markdown(f"**Gaps:**\n{candidate_record['Gaps']}")

elif menu == "Candidate Database":
    st.title("📂 Candidate Database")
    df = get_candidate_data()
    
    if df.empty:
        st.warning("The database is currently empty. Evaluate some candidates first!")
    else:
        # Search and Filter
        search_query = st.text_input("Search Candidates", placeholder="Type a name...")
        if search_query:
            df = df[df['Name'].str.contains(search_query, case=False)]
        
        # Display Table
        st.dataframe(df, width='stretch', hide_index=True)
        
        # Delete functionality
        with st.expander("Manage Records"):
            name_to_delete = st.selectbox("Select Candidate to Delete", [""] + list(df['Name'].unique()))
            if st.button("Delete Record") and name_to_delete:
                db_delete(name_to_delete)
                st.success(f"Deleted record for {name_to_delete}")
                st.rerun()

elif menu == "Top Candidates":
    st.title("🏆 Top Performers")
    top_n = st.slider("Show Top", 3, 10, 5)
    top_candidates = db_top(top_n)
    
    if not top_candidates:
        st.info("No candidates found in the database.")
    else:
        for i, cand in enumerate(top_candidates):
            with st.container():
                st.markdown(f"""
                <div class="candidate-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h3 style="margin: 0;">#{i+1} {cand['name']}</h3>
                        <span class="score-badge">{cand['score']}/100</span>
                    </div>
                    <p style="margin-top: 10px;"><strong>Recommendation:</strong> {cand['recommendation']}</p>
                    <p><strong>Strengths:</strong> {cand['strengths']}</p>
                    <a href="{cand['profile_url']}" target="_blank">View Profile</a>
                </div>
                """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("Built with ❤️ by JobMatch AI Team")
