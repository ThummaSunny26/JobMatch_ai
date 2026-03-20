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
    You are an expert technical recruiter. Evaluate the following candidate against the job description.
    
    Candidate Info: {candidate_info}
    Job Description: {job_description}
    Context Hints: {context_hints}
    
    Output a JSON object with:
    1. score: (integer 0-100)
    2. strengths: (concise list of top 3 matches)
    3. gaps: (concise list of top 3 missing skills or experiences)
    4. recommendation: (One sentence summary: "Highly Recommend", "Recommend", "Consider", or "Do Not Recommend" with reason)
    
    Scoring Rubric:
    - 90-100: Exceptional match in all key areas.
    - 70-89: Strong match with minor gaps.
    - 40-69: Partial match or insufficient profile data found online.
    - <40: Mismatched role or severe skill gaps.
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
