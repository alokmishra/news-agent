# src/main.py
import asyncio
import logging
import os
from datetime import datetime
from typing import Dict, List
import yaml

from mailer import EmailSender
from agent.graph import app as search_graph

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsAgent:
    def __init__(self, config: Dict):
        self.config = config
        self.mailer = EmailSender(config)
    
    async def run_daily_pipeline(self, topics: List[str] = None):
        """Execute the complete pipeline using LangGraph"""
        logger.info("Starting daily news pipeline (Agentic Mode)...")
        
        # 1. Load Topics
        if not topics:
            try:
                with open('src/topics.yaml') as f:
                    topic_config = yaml.safe_load(f)
                    topics = topic_config.get('topics', [])
            except Exception as e:
                logger.error(f"Failed to load topics.yaml: {e}")
                return

        summaries = {}
        
        # 2. Run Graph for each topic
        for topic in topics:
            logger.info(f"Agent researching topic: {topic}")
            try:
                # Invoke the graph
                inputs = {
                    "topic": topic,
                    "messages": [],
                    "research_results": [],
                    "summary": ""
                }
                result = await search_graph.ainvoke(inputs)
                summaries[topic] = result.get("summary", "No summary generated.")
                
                # Log sources
                sources = result.get("sources", [])
                if sources:
                    with open("data/sources_log.md", "a") as f:
                        f.write(f"\n## Topic: {topic} ({datetime.now().strftime('%Y-%m-%d %H:%M')})\n")
                        for s in sources:
                            f.write(f"- {s}\n")
                
            except Exception as e:
                logger.error(f"Agent failed on topic {topic}: {e}")
                summaries[topic] = f"## Error\nAgent failed: {str(e)}"
        
        return summaries
    
    async def send_digest(self, summaries: Dict[str, str], article_count: int, to_email: str = None):
        """Generate and send email digest"""
        email_html = self.mailer.render_template(
            summaries=summaries,
            date=datetime.now().strftime("%B %d, %Y"),
            article_count=f"{article_count} Topics"
        )
        
        await self.mailer.send_email(
            subject=f"Your Daily Agent Briefing: {datetime.now().strftime('%Y-%m-%d')}",
            html_content=email_html,
            to_email=to_email
        )

if __name__ == "__main__":
    from dotenv import load_dotenv
    
    load_dotenv()
    
    config = {
        'google_api_key': os.getenv('GOOGLE_API_KEY'),
        'sender_email': os.getenv('SENDER_EMAIL'),
        'recipient_email': os.getenv('RECIPIENT_EMAIL')
    }
    
    agent = NewsAgent(config)
    asyncio.run(agent.run_daily_pipeline())
