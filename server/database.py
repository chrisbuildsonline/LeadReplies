import sqlite3
import hashlib
from datetime import datetime
import json
import bcrypt

class Database:
    def __init__(self, db_path="reddit_leads_v2.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Businesses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS businesses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                website TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Keywords table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS keywords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_id INTEGER NOT NULL,
                keyword TEXT NOT NULL,
                source TEXT DEFAULT 'manual',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (business_id) REFERENCES businesses (id)
            )
        ''')
        
        # Subreddits table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subreddits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_id INTEGER NOT NULL,
                subreddit TEXT NOT NULL,
                source TEXT DEFAULT 'manual',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (business_id) REFERENCES businesses (id)
            )
        ''')
        
        # Global leads table (all scraped leads)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS global_leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                platform_id TEXT NOT NULL,
                title TEXT,
                content TEXT,
                author TEXT,
                url TEXT,
                subreddit TEXT,
                score INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(platform, platform_id)
            )
        ''')
        
        # Business-specific processed leads
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS business_leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_id INTEGER NOT NULL,
                global_lead_id INTEGER NOT NULL,
                ai_score REAL,
                ai_reasoning TEXT,
                matched_keywords TEXT,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (business_id) REFERENCES businesses (id),
                FOREIGN KEY (global_lead_id) REFERENCES global_leads (id),
                UNIQUE(business_id, global_lead_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # User management
    def create_user(self, email, password):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        try:
            cursor.execute('INSERT INTO users (email, password_hash) VALUES (?, ?)', 
                         (email, password_hash))
            user_id = cursor.lastrowid
            conn.commit()
            return user_id
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    def verify_user(self, email, password):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, password_hash FROM users WHERE email = ?', (email,))
        result = cursor.fetchone()
        conn.close()
        
        if result and bcrypt.checkpw(password.encode('utf-8'), result[1].encode('utf-8')):
            return result[0]
        return None
    
    def get_user(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, email, created_at FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'email': result[1],
                'created_at': result[2]
            }
        return None
    
    # Business management
    def create_business(self, user_id, name, website=None, description=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO businesses (user_id, name, website, description) 
            VALUES (?, ?, ?, ?)
        ''', (user_id, name, website, description))
        
        business_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return business_id
    
    def get_user_businesses(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, website, description, created_at 
            FROM businesses WHERE user_id = ?
        ''', (user_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [{
            'id': row[0],
            'name': row[1],
            'website': row[2],
            'description': row[3],
            'created_at': row[4]
        } for row in results]
    
    def get_business(self, business_id, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, website, description, created_at 
            FROM businesses WHERE id = ? AND user_id = ?
        ''', (business_id, user_id))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'name': result[1],
                'website': result[2],
                'description': result[3],
                'created_at': result[4]
            }
        return None
    
    def update_business(self, business_id, name, website=None, description=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE businesses 
                SET name = ?, website = ?, description = ?
                WHERE id = ?
            ''', (name, website, description, business_id))
            
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating business: {e}")
            return False
        finally:
            conn.close()
    
    # Keywords management
    def add_keyword(self, business_id, keyword, source='manual'):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('INSERT INTO keywords (business_id, keyword, source) VALUES (?, ?, ?)', 
                      (business_id, keyword, source))
        conn.commit()
        conn.close()
    
    def get_business_keywords(self, business_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, keyword, source FROM keywords WHERE business_id = ?', (business_id,))
        results = cursor.fetchall()
        conn.close()
        
        return [{'id': row[0], 'keyword': row[1], 'source': row[2]} for row in results]
    
    def remove_keyword(self, keyword_id, business_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM keywords WHERE id = ? AND business_id = ?', 
                      (keyword_id, business_id))
        conn.commit()
        conn.close()
    
    # Subreddits management
    def add_subreddit(self, business_id, subreddit, source='manual'):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('INSERT INTO subreddits (business_id, subreddit, source) VALUES (?, ?, ?)', 
                      (business_id, subreddit, source))
        conn.commit()
        conn.close()
    
    def get_business_subreddits(self, business_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, subreddit, source FROM subreddits WHERE business_id = ?', (business_id,))
        results = cursor.fetchall()
        conn.close()
        
        return [{'id': row[0], 'subreddit': row[1], 'source': row[2]} for row in results]
    
    def remove_subreddit(self, subreddit_id, business_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM subreddits WHERE id = ? AND business_id = ?', 
                      (subreddit_id, business_id))
        conn.commit()
        conn.close()
    
    def get_all_subreddits(self):
        """Get all unique subreddits for scraping"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT DISTINCT subreddit FROM subreddits')
        results = cursor.fetchall()
        conn.close()
        
        return [row[0] for row in results]
    
    def get_all_keywords(self):
        """Get all unique keywords for scraping"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT DISTINCT keyword FROM keywords')
        results = cursor.fetchall()
        conn.close()
        
        return [row[0] for row in results]
    
    # Global leads management
    def add_global_lead(self, platform, platform_id, title, content, author, url, subreddit=None, score=0):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO global_leads (platform, platform_id, title, content, author, url, subreddit, score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (platform, platform_id, title, content, author, url, subreddit, score))
            
            lead_id = cursor.lastrowid
            conn.commit()
            return lead_id
        except sqlite3.IntegrityError:
            # Lead already exists
            return None
        finally:
            conn.close()
    
    def get_unprocessed_leads_for_business(self, business_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT gl.* FROM global_leads gl
            WHERE gl.id NOT IN (
                SELECT global_lead_id FROM business_leads WHERE business_id = ?
            )
            ORDER BY gl.created_at DESC
        ''', (business_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [{
            'id': row[0],
            'platform': row[1],
            'platform_id': row[2],
            'title': row[3],
            'content': row[4],
            'author': row[5],
            'url': row[6],
            'subreddit': row[7],
            'score': row[8],
            'created_at': row[9],
            'scraped_at': row[10]
        } for row in results]
    
    # Business leads management
    def add_business_lead(self, business_id, global_lead_id, ai_score, ai_reasoning, matched_keywords):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO business_leads (business_id, global_lead_id, ai_score, ai_reasoning, matched_keywords)
                VALUES (?, ?, ?, ?, ?)
            ''', (business_id, global_lead_id, ai_score, ai_reasoning, json.dumps(matched_keywords)))
            
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def get_business_leads(self, business_id, limit=50):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT bl.*, gl.platform, gl.platform_id, gl.title, gl.content, gl.author, 
                   gl.url, gl.subreddit, gl.score, gl.created_at
            FROM business_leads bl
            JOIN global_leads gl ON bl.global_lead_id = gl.id
            WHERE bl.business_id = ?
            ORDER BY bl.ai_score DESC, bl.processed_at DESC
            LIMIT ?
        ''', (business_id, limit))
        
        results = cursor.fetchall()
        conn.close()
        
        return [{
            'id': row[0],
            'business_id': row[1],
            'global_lead_id': row[2],
            'ai_score': row[3],
            'ai_reasoning': row[4],
            'matched_keywords': json.loads(row[5]) if row[5] else [],
            'processed_at': row[6],
            'platform': row[7],
            'platform_id': row[8],
            'title': row[9],
            'content': row[10],
            'author': row[11],
            'url': row[12],
            'subreddit': row[13],
            'score': row[14],
            'created_at': row[15]
        } for row in results]