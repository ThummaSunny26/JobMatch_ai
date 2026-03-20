import os
from tavily import TavilyClient
from dotenv import load_dotenv

# Load environment variables from the project root
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

def web_search(query: str):
    """
    Responsible for discovering candidate information online.
    Prioritizes LinkedIn, GitHub, and professional portfolios.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return {"results": [], "urls": [], "error": "TAVILY_API_KEY not found"}

    client = TavilyClient(api_key=api_key)
    try:
        # Heavily prioritizing professional platforms in the query
        professional_query = f"{query} site:linkedin.com OR site:github.com OR site:behance.net OR portfolio resume"
        
        # Advanced search for maximum relevance
        response = client.search(
            query=professional_query, 
            search_depth="advanced",
            max_results=8, # Increased for better coverage
            include_raw_content=False
        )
        
        results = response.get('results', [])
        
        # Prioritize LinkedIn and GitHub URLs in the response
        sorted_results = sorted(results, key=lambda x: (
            'linkedin.com' in x.get('url', '').lower() or 
            'github.com' in x.get('url', '').lower()
        ), reverse=True)
        
        formatted_results = []
        for res in sorted_results:
            formatted_results.append({
                "title": res.get("title"),
                "url": res.get("url"),
                "content": res.get("content")[:1500] # Increased context
            })
            
        return {
            "results": formatted_results,
            "urls": [res.get('url') for res in sorted_results]
        }
    except Exception as e:
        return {"results": [], "urls": [], "error": f"Professional search failed: {str(e)}"}
