import os
import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

# Load environment variables from the project root
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

def jd_scorer(candidate_info: str, job_description: str):
    """
    Evaluates aggregated profile content against a given job description.
    Provides a quantitative score (0-100) along with qualitative feedback.
    """
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    temperature = float(os.getenv("OPENAI_TEMPERATURE", 0))
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = None
    if api_key and api_key.startswith("sk-or-v1"):
        base_url = "https://openrouter.ai/api/v1"
        if "/" not in model_name:
            model_name = f"openai/{model_name}"
    
    llm = ChatOpenAI(
        model=model_name, 
        temperature=temperature,
        openai_api_key=api_key,
        base_url=base_url
    )
    
    prompt = ChatPromptTemplate.from_template("""
    You are an elite technical recruiter. Synthesize and evaluate the aggregated profile content against the job description.

    Aggregated Profile Content (from LinkedIn, GitHub, etc.):
    {candidate_info}
    
    Job Description:
    {job_description}
    
    Instructions:
    1. Cross-reference all provided profile content to build a holistic view of the candidate.
    2. Identify core technical skills, experience level, and specific project achievements.
    3. Provide a score (0-100) based on the rubric below and detailed qualitative feedback.
    
    Output JSON format:
    - score: integer
    - strengths: top 3-4 specific professional matches
    - gaps: top 3-4 missing or unverified critical skills
    - recommendation: concise professional judgment (e.g., "Strongly Recommend for Backend Roles")
    
    Scoring Rubric:
    - 90+: Exceptional match with verified, high-impact experience across multiple profiles.
    - 75-89: Strong match, minimal training needed. Evidence present in at least one primary profile.
    - 50-74: Partial match or unverified data. Mention "Needs Deeper Vetting."
    - <50: Unsuitable or unrelated background.
    """)
    
    chain = prompt | llm
    
    try:
        response = chain.invoke({
            "candidate_info": candidate_info[:12000], # Allow larger context for multiple profiles
            "job_description": job_description[:4000],
        })
        
        content = response.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        result = json.loads(content)
        result["score"] = int(result.get("score", 0))
        return result
    except Exception as e:
        return {
            "score": 0,
            "strengths": "N/A",
            "gaps": f"Error: {str(e)}",
            "recommendation": "Error during scoring"
        }
