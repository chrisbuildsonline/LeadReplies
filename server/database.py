import psycopg2
import psycopg2.extras
from datetime import datetime
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.connection_params = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'database': os.getenv('DB_NAME', 'reddit_leads'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'password'),
            'port': os.getenv('DB_PORT', '5432')
        }
    
    def get_connection(self):
        return psycopg2.connect(**self.connection_params)
    
    def init_database(self):
        """Initialize database tables"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                # Keywords table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS keywords (
                        id SERIAL PRIMARY KEY,
                        keyword VARCHAR(255) NOT NULL UNIQUE,
                        active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Leads table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS leads (
                        id SERIAL PRIMARY KEY,
                        reddit_id VARCHAR(50) UNIQUE NOT NULL,
                        service VARCHAR(20) DEFAULT 'reddit',
                        title TEXT NOT NULL,
                        content TEXT,
                        url TEXT NOT NULL,
                        author VARCHAR(100),
                        subreddit VARCHAR(100),
                        type VARCHAR(20), -- 'post' or 'comment'
                        keywords_matched TEXT[], -- array of matched keywords
                        ai_probability INTEGER, -- 0-100% probability score
                        ai_analysis TEXT, -- AI analysis text
                        hotness_score INTEGER DEFAULT 0,
                        upvotes INTEGER DEFAULT 0,
                        num_comments INTEGER DEFAULT 0,
                        created_date TIMESTAMP,
                        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        raw_data JSONB
                    )
                """)
                
                # Subreddits table for tracking
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS subreddits (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL UNIQUE,
                        active BOOLEAN DEFAULT TRUE,
                        last_checked TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create indexes for better performance
                cur.execute("CREATE INDEX IF NOT EXISTS idx_leads_service ON leads(service)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_leads_subreddit ON leads(subreddit)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_leads_ai_probability ON leads(ai_probability)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_leads_created_date ON leads(created_date)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_leads_processed_at ON leads(processed_at)")
                
                conn.commit()
                print("✅ Database initialized successfully")
    
    def add_keyword(self, keyword: str) -> bool:
        """Add a keyword to track"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO keywords (keyword) VALUES (%s) ON CONFLICT (keyword) DO NOTHING",
                        (keyword,)
                    )
                    conn.commit()
                    return True
        except Exception as e:
            print(f"Error adding keyword: {e}")
            return False
    
    def get_active_keywords(self) -> List[str]:
        """Get all active keywords"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT keyword FROM keywords WHERE active = TRUE")
                return [row[0] for row in cur.fetchall()]
    
    def add_subreddit(self, subreddit: str) -> bool:
        """Add a subreddit to track"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO subreddits (name) VALUES (%s) ON CONFLICT (name) DO NOTHING",
                        (subreddit,)
                    )
                    conn.commit()
                    return True
        except Exception as e:
            print(f"Error adding subreddit: {e}")
            return False
    
    def get_active_subreddits(self) -> List[str]:
        """Get all active subreddits"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT name FROM subreddits WHERE active = TRUE")
                return [row[0] for row in cur.fetchall()]
    
    def save_lead(self, lead_data: Dict) -> bool:
        """Save a lead to the database"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # Convert raw_data to JSON string if it's a dict
                    raw_data = lead_data.get('raw_data')
                    if isinstance(raw_data, dict):
                        import json
                        raw_data = json.dumps(raw_data)
                    
                    # Prepare data with JSON conversion
                    db_data = {**lead_data, 'raw_data': raw_data}
                    
                    cur.execute("""
                        INSERT INTO leads (
                            reddit_id, service, title, content, url, author, subreddit,
                            type, keywords_matched, ai_probability, ai_analysis,
                            hotness_score, upvotes, num_comments, created_date, raw_data
                        ) VALUES (
                            %(reddit_id)s, %(service)s, %(title)s, %(content)s, %(url)s,
                            %(author)s, %(subreddit)s, %(type)s, %(keywords_matched)s,
                            %(ai_probability)s, %(ai_analysis)s, %(hotness_score)s,
                            %(upvotes)s, %(num_comments)s, %(created_date)s, %(raw_data)s
                        ) ON CONFLICT (reddit_id) DO UPDATE SET
                            ai_probability = EXCLUDED.ai_probability,
                            ai_analysis = EXCLUDED.ai_analysis,
                            processed_at = CURRENT_TIMESTAMP
                    """, db_data)
                    conn.commit()
                    return True
        except Exception as e:
            print(f"Error saving lead: {e}")
            return False
    
    def get_leads(self, limit: int = 100, min_probability: int = 0) -> List[Dict]:
        """Get leads from database"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM leads 
                    WHERE ai_probability >= %s 
                    ORDER BY ai_probability DESC, processed_at DESC 
                    LIMIT %s
                """, (min_probability, limit))
                return [dict(row) for row in cur.fetchall()]
    
    def update_subreddit_check_time(self, subreddit: str):
        """Update last checked time for subreddit"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE subreddits SET last_checked = CURRENT_TIMESTAMP WHERE name = %s",
                    (subreddit,)
                )
                conn.commit()