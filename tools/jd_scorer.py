import os
import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

# Load environment variables from the project root
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

def jd_scorer(candidate_info: str, job_description: str, context_hints: str = None):
    """
    Evaluates a candidate's profile against a given job description.
    Provides a quantitative score (0-100) along with qualitative feedback.
    """
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    temperature = float(os.getenv("OPENAI_TEMPERATURE", 0))
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = None
    if api_key and api_key.startswith("sk-or-v1"):
        base_url = "https://openrouter.ai/api/v1"
        # For OpenRouter, ensure model name is prefixed correctly if it's not already
        if "/" not in model_name:
            model_name = f"openai/{model_name}"
    
    llm = ChatOpenAI(
        model=model_name, 
        temperature=temperature,
        openai_api_key=api_key,
        base_url=base_url
    )
    
    prompt = ChatPromptTemplate.from_template("""
    Evaluate the following candidate based on the job description and context hints.
    
    Candidate Info: {candidate_info}
    Job Description: {job_description}
    Context Hints: {context_hints}
    
    Provide your evaluation in JSON format with the following keys:
    - score: (int, 0-100)
    - strengths: (str)
    - gaps: (str)
    - recommendation: (str)
    
    Scoring Guidelines:
    - No online profile found: 40-55
    - Wrong field candidate: <30
    - Good match: 70+
    """)
    
    chain = prompt | llm
    
    try:
        response = chain.invoke({
            "candidate_info": candidate_info,
            "job_description": job_description,
            "context_hints": context_hints or "None"
        })
        
        # Extract content and parse JSON
        content = response.content.strip()
        # Handle cases where the model might wrap JSON in markdown blocks
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        elif content.startswith("```"):
            content = content.replace("```", "").strip()
            
        return json.loads(content)
    except Exception as e:
        return {
            "score": 0,
            "strengths": "N/A",
            "gaps": f"Error during evaluation: {str(e)}",
            "recommendation": "Manual review required"
        }
