# src/db.py
import sqlite3
from datetime import datetime
from typing import Optional

class Database:
    def __init__(self, db_path="data/history.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
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

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                email TEXT PRIMARY KEY,
                topics TEXT, -- JSON encoded list
                otp TEXT,
                otp_created_at TIMESTAMP,
                is_verified BOOLEAN DEFAULT 0,
                last_sent_at TIMESTAMP
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

    def upsert_user(self, email: str, topics: str, otp: str):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO users (email, topics, otp, otp_created_at, is_verified)
            VALUES (?, ?, ?, ?, 0)
            ON CONFLICT(email) DO UPDATE SET
                topics=excluded.topics,
                otp=excluded.otp,
                otp_created_at=excluded.otp_created_at,
                is_verified=0
        ''', (email, topics, otp, datetime.now()))
        self.conn.commit()

    def verify_user(self, email: str) -> bool:
        cursor = self.conn.cursor()
        cursor.execute("UPDATE users SET is_verified = 1 WHERE email = ?", (email,))
        self.conn.commit()
        return cursor.rowcount > 0

    def get_user_otp(self, email: str) -> Optional[tuple]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT otp, otp_created_at FROM users WHERE email = ?", (email,))
        return cursor.fetchone()

    def get_verified_users(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT email, topics, last_sent_at FROM users WHERE is_verified = 1")
        return cursor.fetchall()

    def update_last_sent(self, email: str):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE users SET last_sent_at = ? WHERE email = ?", (datetime.now(), email))
        self.conn.commit()
