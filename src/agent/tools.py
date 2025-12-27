from langchain_core.tools import tool
from trafilatura import extract
import requests
from typing import List

# Direct implementation to avoid LangChain import issues
try:
    from duckduckgo_search import DDGS
except ImportError:
    try:
        from ddgs import DDGS
    except ImportError:
        DDGS = None

@tool
def search_web(query: str) -> List[str]:
    """Search the web for a query and return top results."""
    if not DDGS:
        return ["Error: duckduckgo-search package not correctly installed."]
    
    try:
        with DDGS() as ddgs:
            # Fetch 5 results
            results = list(ddgs.text(query, max_results=5))
            # Format as strings
            return [f"Title: {r.get('title')}\nLink: {r.get('href')}\nSnippet: {r.get('body')}" for r in results]
    except Exception as e:
        return [f"Search failed: {str(e)}"]

@tool
def scrape_article(url: str) -> str:
    """Scrape the content of a specific URL."""
    try:
        response = requests.get(url, timeout=10, headers={'User-Agent': 'NewsAgent/1.0'})
        text = extract(response.text)
        if text:
            return text[:10000] # Limit content length
        return "Failed to extract content."
    except Exception as e:
        return f"Error scraping {url}: {str(e)}"
