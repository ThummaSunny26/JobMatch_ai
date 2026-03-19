import os
from tavily import TavilyClient
from dotenv import load_dotenv

# Load environment variables from the project root
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

def web_search(query: str):
    """
    Responsible for discovering candidate information online.
    It queries external sources, prioritizing platforms like LinkedIn and GitHub.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return {"results": [], "urls": [], "error": "TAVILY_API_KEY not found"}

    client = TavilyClient(api_key=api_key)
    try:
        # Using search_depth='advanced' as per PRD
        response = client.search(query=query, search_depth="advanced")
        
        results = response.get('results', [])
        urls = [res.get('url') for res in results]
        
        return {
            "results": results,
            "urls": urls
        }
    except Exception as e:
        return {"results": [], "urls": [], "error": str(e)}
