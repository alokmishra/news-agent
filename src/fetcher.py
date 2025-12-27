# src/fetcher.py
import asyncio
import aiohttp
import feedparser
from trafilatura import extract
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class ContentFetcher:
    def __init__(self, max_concurrent=5):
        self.max_concurrent = max_concurrent
    
    async def fetch_rss_feed(self, feed_url: str) -> List[Dict]:
        """Parse RSS feed asynchronously"""
        loop = asyncio.get_event_loop()
        feed = await loop.run_in_executor(None, feedparser.parse, feed_url)
        
        articles = []
        for entry in feed.entries[:10]:  # Limit to 10 per feed
            article = {
                'id': entry.get('id', entry.link),
                'title': entry.get('title', ''),
                'link': entry.link,
                'summary': entry.get('summary', ''),
                'published': entry.get('published_parsed'),
                'source_name': feed.feed.get('title', 'Unknown')
            }
            articles.append(article)
        return articles
    
    async def fetch_full_content(self, url: str) -> str:
        """Fetch and extract main content from URL"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10, 
                                     headers={'User-Agent': 'Mozilla/5.0'}) as response:
                    html = await response.text()
            
            # Use trafilatura for better content extraction
            text = extract(html, include_comments=False, 
                          include_tables=False, output_format='text')
            
            if not text or len(text) < 100:
                # Fallback to basic extraction
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html, 'html.parser')
                
                # Remove unwanted elements
                for element in soup(['script', 'style', 'nav', 'footer', 'aside']):
                    element.decompose()
                
                # Try to find main content
                article = soup.find('article') or soup.find('main') or soup.body
                text = article.get_text(separator='\n', strip=True)
            
            return text[:5000]  # Limit length for token management
            
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return ""
