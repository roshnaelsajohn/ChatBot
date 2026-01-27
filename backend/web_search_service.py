
from duckduckgo_search import DDGS

class WebSearchService:
    """Service to perform web searches using DuckDuckGo."""
    
    def __init__(self):
        pass

    def search(self, query: str, max_results: int = 3) -> list:
        """
        Search the web for the query.
        Returns a list of dictionaries with 'content', 'source', and 'title'.
        """
        results = []
        try:
            with DDGS() as ddgs:
                # DDGS().text() returns an iterator of results
                search_results = list(ddgs.text(query, max_results=max_results))
                
                for res in search_results:
                    results.append({
                        "content": res.get("body", ""),
                        "source": res.get("href", ""),
                        "title": res.get("title", "")
                    })
            return results
        except Exception as e:
            print(f"Error performing web search: {e}")
            return []
