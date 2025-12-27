# src/db.py
import sqlite3
from datetime import datetime
from typing import Optional

class Database:
    def __init__(self, db_path="data/history.db"):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id TEXT PRIMARY KEY,
                title TEXT,
                link TEXT UNIQUE,
                summary TEXT,
                full_text TEXT,
                source_name TEXT,
                topic TEXT,
                published TIMESTAMP,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_summarized BOOLEAN DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sources (
                url TEXT PRIMARY KEY,
                name TEXT,
                topic TEXT,
                last_fetched TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        self.conn.commit()
    
    def article_exists(self, article_id: str) -> bool:
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM articles WHERE id = ?", (article_id,))
        return cursor.fetchone() is not None
    
    def insert_article(self, article_data: dict):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO articles 
            (id, title, link, summary, full_text, source_name, topic, published)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            article_data['id'],
            article_data['title'],
            article_data['link'],
            article_data.get('summary'),
            article_data.get('full_text'),
            article_data.get('source_name'),
            article_data.get('topic'),
            article_data.get('published')
        ))
        self.conn.commit()
