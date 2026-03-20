import os
from tavily import TavilyClient
from dotenv import load_dotenv

# Load environment variables from the project root
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

def web_search(query: str):
    """
    Finds the most relevant professional profile URLs for a candidate.
    Prioritizes LinkedIn, GitHub, and personal portfolios.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return {"urls": [], "error": "TAVILY_API_KEY not found"}

    client = TavilyClient(api_key=api_key)
    try:
        # Fine-tuned query to find homepages and top professional profiles
        professional_query = f'{query} official website OR LinkedIn OR GitHub OR portfolio'
        
        response = client.search(
            query=professional_query, 
            search_depth="advanced",
            max_results=8
        )
        
        results = response.get('results', [])
        
        # Rank URLs by professional relevance
        def rank_url(url):
            if 'linkedin.com/in' in url.lower(): return 1
            if 'github.com/' in url.lower(): return 2
            if 'portfolio' in url.lower() or 'resume' in url.lower(): return 3
            return 4

        sorted_urls = sorted([res.get('url') for res in results], key=rank_url)
        
        # Return only the top 3-4 most relevant URLs
        return {"urls": sorted_urls[:4]}
    except Exception as e:
        return {"urls": [], "error": f"URL search failed: {str(e)}"}
