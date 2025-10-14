import psycopg2
import psycopg2.extras
import hashlib
from datetime import datetime
import json
import bcrypt
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
        self.init_database()
    
    def get_connection(self):
        return psycopg2.connect(**self.connection_params)
    
    def init_database(self):
        """Initialize database tables if they don't exist"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Businesses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS businesses (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                name VARCHAR(255) NOT NULL,
                website TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        
        # Keywords table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS keywords (
                id SERIAL PRIMARY KEY,
                business_id INTEGER NOT NULL,
                keyword VARCHAR(255) NOT NULL,
                source VARCHAR(50) DEFAULT 'manual',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (business_id) REFERENCES businesses (id) ON DELETE CASCADE
            )
        ''')
        
        # Subreddits table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subreddits (
                id SERIAL PRIMARY KEY,
                business_id INTEGER NOT NULL,
                subreddit VARCHAR(255) NOT NULL,
                source VARCHAR(50) DEFAULT 'manual',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (business_id) REFERENCES businesses (id) ON DELETE CASCADE
            )
        ''')
        
        # Global leads table (all scraped leads)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS global_leads (
                id SERIAL PRIMARY KEY,
                platform VARCHAR(50) NOT NULL,
                platform_id VARCHAR(255) NOT NULL,
                title TEXT,
                content TEXT,
                author VARCHAR(255),
                url TEXT,
                subreddit VARCHAR(255),
                score INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(platform, platform_id)
            )
        ''')
        
        # Business-specific processed leads
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS business_leads (
                id SERIAL PRIMARY KEY,
                business_id INTEGER NOT NULL,
                global_lead_id INTEGER NOT NULL,
                ai_score REAL,
                ai_reasoning TEXT,
                matched_keywords TEXT,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (business_id) REFERENCES businesses (id) ON DELETE CASCADE,
                FOREIGN KEY (global_lead_id) REFERENCES global_leads (id) ON DELETE CASCADE,
                UNIQUE(business_id, global_lead_id)
            )
        ''')
        
        # Create indexes for better performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_businesses_user_id ON businesses(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_keywords_business_id ON keywords(business_id)",
            "CREATE INDEX IF NOT EXISTS idx_subreddits_business_id ON subreddits(business_id)",
            "CREATE INDEX IF NOT EXISTS idx_global_leads_platform ON global_leads(platform, platform_id)",
            "CREATE INDEX IF NOT EXISTS idx_business_leads_business_id ON business_leads(business_id)",
            "CREATE INDEX IF NOT EXISTS idx_business_leads_processed_at ON business_leads(processed_at)",
            "CREATE INDEX IF NOT EXISTS idx_business_leads_ai_score ON business_leads(ai_score)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        conn.commit()
        cursor.close()
        conn.close()
    
    # User management
    def create_user(self, email, password):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        try:
            cursor.execute('INSERT INTO users (email, password_hash) VALUES (%s, %s) RETURNING id', 
                         (email, password_hash))
            user_id = cursor.fetchone()[0]
            conn.commit()
            return user_id
        except psycopg2.IntegrityError:
            return None
        finally:
            cursor.close()
            conn.close()
    
    def verify_user(self, email, password):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, password_hash FROM users WHERE email = %s', (email,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result and bcrypt.checkpw(password.encode('utf-8'), result[1].encode('utf-8')):
            return result[0]
        return None
    
    def get_user(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute('SELECT id, email, created_at FROM users WHERE id = %s', (user_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            return dict(result)
        return None
    
    # Business management
    def create_business(self, user_id, name, website=None, description=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO businesses (user_id, name, website, description) 
            VALUES (%s, %s, %s, %s) RETURNING id
        ''', (user_id, name, website, description))
        
        business_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        return business_id
    
    def get_user_businesses(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute('''
            SELECT id, name, website, description, created_at 
            FROM businesses WHERE user_id = %s
        ''', (user_id,))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [dict(row) for row in results]
    
    def get_business(self, business_id, user_id):
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute('''
            SELECT id, name, website, description, created_at 
            FROM businesses WHERE id = %s AND user_id = %s
        ''', (business_id, user_id))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            return dict(result)
        return None
    
    def update_business(self, business_id, name, website=None, description=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE businesses 
            SET name = %s, website = %s, description = %s 
            WHERE id = %s
        ''', (name, website, description, business_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        cursor.close()
        conn.close()
        return success
    
    # Keywords management
    def add_business_keyword(self, business_id, keyword, source='manual'):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO keywords (business_id, keyword, source) 
            VALUES (%s, %s, %s) RETURNING id
        ''', (business_id, keyword, source))
        
        keyword_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        return keyword_id
    
    def get_business_keywords(self, business_id):
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute('''
            SELECT id, keyword, source, created_at 
            FROM keywords WHERE business_id = %s
        ''', (business_id,))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [dict(row) for row in results]
    
    def delete_business_keyword(self, keyword_id, business_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM keywords 
            WHERE id = %s AND business_id = %s
        ''', (keyword_id, business_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        cursor.close()
        conn.close()
        return success
    
    # Subreddits management
    def add_business_subreddit(self, business_id, subreddit, source='manual'):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO subreddits (business_id, subreddit, source) 
            VALUES (%s, %s, %s) RETURNING id
        ''', (business_id, subreddit, source))
        
        subreddit_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        return subreddit_id
    
    def get_business_subreddits(self, business_id):
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute('''
            SELECT id, subreddit, source, created_at 
            FROM subreddits WHERE business_id = %s
        ''', (business_id,))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [dict(row) for row in results]
    
    def delete_business_subreddit(self, subreddit_id, business_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM subreddits 
            WHERE id = %s AND business_id = %s
        ''', (subreddit_id, business_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        cursor.close()
        conn.close()
        return success
    
    # Global leads management
    def add_global_lead(self, platform, platform_id, title, content, author, url, subreddit=None, score=0):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO global_leads (platform, platform_id, title, content, author, url, subreddit, score) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
            ''', (platform, platform_id, title, content, author, url, subreddit, score))
            
            lead_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            conn.close()
            return lead_id
        except psycopg2.IntegrityError:
            # Duplicate lead
            cursor.close()
            conn.close()
            return None
    
    def get_unprocessed_leads_for_business(self, business_id):
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute('''
            SELECT gl.* FROM global_leads gl
            WHERE gl.id NOT IN (
                SELECT global_lead_id FROM business_leads WHERE business_id = %s
            )
            ORDER BY gl.created_at DESC
        ''', (business_id,))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [dict(row) for row in results]
    
    # Business leads management
    def add_business_lead(self, business_id, global_lead_id, ai_score, ai_reasoning, matched_keywords):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Convert matched_keywords list to JSON string
            keywords_json = json.dumps(matched_keywords) if isinstance(matched_keywords, list) else matched_keywords
            
            cursor.execute('''
                INSERT INTO business_leads (business_id, global_lead_id, ai_score, ai_reasoning, matched_keywords) 
                VALUES (%s, %s, %s, %s, %s) RETURNING id
            ''', (business_id, global_lead_id, ai_score, ai_reasoning, keywords_json))
            
            lead_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            conn.close()
            return lead_id
        except psycopg2.IntegrityError:
            # Duplicate business lead
            cursor.close()
            conn.close()
            return None
    
    def get_business_leads(self, business_id, limit=50):
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute('''
            SELECT bl.*, gl.platform, gl.platform_id, gl.title, gl.content, gl.author, 
                   gl.url, gl.subreddit, gl.score, gl.created_at
            FROM business_leads bl
            JOIN global_leads gl ON bl.global_lead_id = gl.id
            WHERE bl.business_id = %s
            ORDER BY bl.ai_score DESC, bl.processed_at DESC
            LIMIT %s
        ''', (business_id, limit))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        leads = []
        for row in results:
            lead = dict(row)
            # Parse matched_keywords JSON
            if lead['matched_keywords']:
                try:
                    lead['matched_keywords'] = json.loads(lead['matched_keywords'])
                except:
                    lead['matched_keywords'] = []
            else:
                lead['matched_keywords'] = []
            leads.append(lead)
        
        return leads