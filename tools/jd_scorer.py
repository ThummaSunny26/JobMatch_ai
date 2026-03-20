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
    You are an elite technical recruiter specialized in high-stakes hiring. 
    Analyze the following candidate info against the job description.
    
    Candidate Info (Aggregated from Web Search): 
    {candidate_info}
    
    Job Description: 
    {job_description}
    
    Instructions:
    1. Identify the candidate's core technical stack and experience level.
    2. Cross-reference their LinkedIn/GitHub/Portfolio data if available in the Info.
    3. Look for evidence of specific achievements or projects relevant to the JD.
    4. Provide a quantitative score (0-100) and qualitative feedback.
    
    Output JSON format:
    - score: integer
    - strengths: top 3 specific professional matches
    - gaps: top 3 missing or unverified critical skills
    - recommendation: concise professional judgment
    
    Scoring Scale:
    - 90+: Perfect match with verified high-impact experience.
    - 75-89: Strong match, minimal training needed.
    - 50-74: Partial match or unverified data (mention "Needs Profile Verification").
    - <50: Unsuitable or unrelated background.
    """)
    
    chain = prompt | llm
    
    try:
        response = chain.invoke({
            "candidate_info": candidate_info[:4000], # Prevent context window overflow
            "job_description": job_description[:2000],
            "context_hints": context_hints or "None"
        })
        
        # Extract content and parse JSON
        content = response.content.strip()
        # Handle cases where the model might wrap JSON in markdown blocks
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        result = json.loads(content)
        # Ensure numeric score
        result["score"] = int(result.get("score", 0))
        return result
    except Exception as e:
        return {
            "score": 0,
            "strengths": "N/A",
            "gaps": f"Error: {str(e)}",
            "recommendation": "Error during evaluation"
        }
