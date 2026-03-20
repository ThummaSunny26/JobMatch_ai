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
        # Enhancing the search query to focus on professional profiles
        professional_query = f"{query} professional profile LinkedIn GitHub portfolio resume"
        
        # Using search_depth='advanced' for more comprehensive results
        response = client.search(
            query=professional_query, 
            search_depth="advanced",
            max_results=5
        )
        
        results = response.get('results', [])
        
        # Structure the observation for better LLM parsing
        formatted_results = []
        for res in results:
            formatted_results.append({
                "title": res.get("title"),
                "url": res.get("url"),
                "content": res.get("content")[:1000] # Snippet for context
            })
            
        return {
            "results": formatted_results,
            "urls": [res.get('url') for res in results]
        }
    except Exception as e:
        return {"results": [], "urls": [], "error": f"Search failed: {str(e)}"}
