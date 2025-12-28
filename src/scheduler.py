# src/scheduler.py
import asyncio
import json
import logging
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

from db import Database
from main import NewsAgent

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def run_schedular():
    load_dotenv()
    db = Database()
    
    # Config for NewsAgent
    config = {
        'google_api_key': os.getenv('GOOGLE_API_KEY'),
        'sender_email': os.getenv('SENDER_EMAIL'),
        # Recipient email is dynamic
    }
    
    agent = NewsAgent(config)
    
    users = db.get_verified_users()
    logger.info(f"Found {len(users)} verified users.")
    
    for user_row in users:
        email, topics_json, last_sent_at = user_row
        
        # Check if sent in last 24 hours
        if last_sent_at:
            last_sent = datetime.strptime(last_sent_at, '%Y-%m-%d %H:%M:%S.%f')
            if datetime.now() - last_sent < timedelta(hours=24):
                logger.info(f"Skipping {email}, sent recently at {last_sent_at}")
                continue
        
        try:
            topics = json.loads(topics_json)
            logger.info(f"Processing for {email} with topics: {topics}")
            
            # Run Pipeline
            summaries = await agent.run_daily_pipeline(topics=topics)
            
            # Send Email
            await agent.send_digest(summaries, len(topics), to_email=email)
            
            # Update DB
            db.update_last_sent(email)
            logger.info(f"Successfully sent digest to {email}")
            
        except Exception as e:
            logger.error(f"Failed to process for user {email}: {e}")

if __name__ == "__main__":
    asyncio.run(run_schedular())
