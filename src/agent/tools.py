from langchain_core.tools import tool
from trafilatura import extract
import requests
from typing import List

import os
try:
    from serpapi import GoogleSearch
except ImportError:
    GoogleSearch = None

@tool
def search_web(query: str) -> List[str]:
    """Search the web for a query using SerpApi."""
    if not GoogleSearch:
        return ["Error: serpapi package not installed. Run `pip install google-search-results`."]
    
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        return ["Error: SERPAPI_API_KEY not found in .env"]

    try:
        params = {
            "q": query,
            "api_key": api_key,
            "engine": "google",
            "tbs": "qdr:d" # Past 24 hours
        }
        search = GoogleSearch(params)
        results = search.get_dict().get("organic_results", [])
        
        return [f"Title: {r.get('title')}\nLink: {r.get('link')}\nSnippet: {r.get('snippet')}" for r in results[:5]]
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
