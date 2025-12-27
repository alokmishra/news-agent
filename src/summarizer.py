# src/summarizer.py
from openai import OpenAI
from typing import List, Dict
import tiktoken
import json

class LLMSummarizer:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.encoder = tiktoken.encoding_for_model("gpt-4")
    
    def count_tokens(self, text: str) -> int:
        return len(self.encoder.encode(text))
    
    def create_batches(self, articles: List[Dict], max_tokens: int = 15000) -> List[List[Dict]]:
        """Group articles by topic and chunk by token count"""
        batches = []
        current_batch = []
        current_tokens = 0
        
        for article in articles:
            content = f"{article['title']}\n{article['full_text'][:2000]}"
            tokens = self.count_tokens(content)
            
            if tokens + current_tokens > max_tokens:
                if current_batch:
                    batches.append(current_batch)
                current_batch = [article]
                current_tokens = tokens
            else:
                current_batch.append(article)
                current_tokens += tokens
        
        if current_batch:
            batches.append(current_batch)
        
        return batches
    
    async def summarize_batch(self, articles: List[Dict], topic: str) -> str:
        """Summarize a batch of related articles"""
        system_prompt = """You are an expert intelligence analyst. Your task is to:
        1. Identify key themes and narratives across the provided articles
        2. Provide a high-level synthesis of the trend
        3. List specific insights with source references
        4. Highlight any contradictions or evolving perspectives
        
        Format your response in Markdown with sections:
        ## Key Takeaways
        ## Detailed Analysis
        ## Source Summaries (with URLs)"""
        
        articles_text = "\n\n---\n\n".join([
            f"Source: {a['source_name']}\n"
            f"URL: {a['link']}\n"
            f"Title: {a['title']}\n"
            f"Content: {a['full_text'][:1500]}"
            for a in articles
        ])
        
        user_prompt = f"""Topic: {topic}

        Here are {len(articles)} recent articles on this topic:

        {articles_text}

        Please provide a comprehensive briefing."""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"## Summarization Error\n\nFailed to summarize: {str(e)}"
# Add to summarizer.py
class CostOptimizer:
    """Monitor and optimize API usage"""
    def __init__(self, budget_daily=1.0):  # $1 per day
        self.budget_daily = budget_daily
        self.costs_today = 0.0
        
    def estimate_cost(self, tokens_in: int, tokens_out: int) -> float:
        # GPT-4o-mini pricing: $0.15/1M tokens in, $0.60/1M tokens out
        return (tokens_in * 0.15 / 1_000_000) + (tokens_out * 0.60 / 1_000_000)
    
    def can_process(self, estimated_cost: float) -> bool:
        return (self.costs_today + estimated_cost) <= self.budget_daily
