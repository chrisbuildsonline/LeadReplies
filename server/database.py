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
        
        # Run Supabase migration first
        self._migrate_for_supabase(cursor)
        
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
                buying_intent TEXT,
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
        
        # Social accounts table for storing user credentials
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS social_accounts (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                platform VARCHAR(50) NOT NULL,
                username VARCHAR(255) NOT NULL,
                password_encrypted TEXT NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                is_verified BOOLEAN DEFAULT FALSE,
                last_used TIMESTAMP,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                UNIQUE(user_id, platform, username)
            )
        ''')
        
        # Notifications table for tracking system events
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                type VARCHAR(50) NOT NULL,
                title VARCHAR(255) NOT NULL,
                message TEXT NOT NULL,
                data JSONB,
                is_read BOOLEAN DEFAULT FALSE,
                is_email_sent BOOLEAN DEFAULT FALSE,
                priority VARCHAR(20) DEFAULT 'normal',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                read_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        
        # User notification preferences
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_notification_preferences (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                notification_type VARCHAR(50) NOT NULL,
                email_enabled BOOLEAN DEFAULT TRUE,
                push_enabled BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                UNIQUE(user_id, notification_type)
            )
        ''')
        
        # Business AI reply settings
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS business_ai_settings (
                id SERIAL PRIMARY KEY,
                business_id INTEGER NOT NULL,
                persona TEXT,
                instructions TEXT,
                bad_words TEXT[],
                service_links JSONB,
                tone VARCHAR(50) DEFAULT 'professional',
                max_reply_length INTEGER DEFAULT 500,
                include_links BOOLEAN DEFAULT TRUE,
                auto_reply_enabled BOOLEAN DEFAULT FALSE,
                confidence_threshold REAL DEFAULT 0.8,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (business_id) REFERENCES businesses (id) ON DELETE CASCADE,
                UNIQUE(business_id)
            )
        ''')
        
        # Create indexes for better performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_businesses_user_id ON businesses(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_keywords_business_id ON keywords(business_id)",

            "CREATE INDEX IF NOT EXISTS idx_global_leads_platform ON global_leads(platform, platform_id)",
            "CREATE INDEX IF NOT EXISTS idx_business_leads_business_id ON business_leads(business_id)",
            "CREATE INDEX IF NOT EXISTS idx_business_leads_processed_at ON business_leads(processed_at)",
            "CREATE INDEX IF NOT EXISTS idx_business_leads_ai_score ON business_leads(ai_score)",
            "CREATE INDEX IF NOT EXISTS idx_social_accounts_user_id ON social_accounts(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_social_accounts_platform ON social_accounts(platform)",
            "CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_notifications_type ON notifications(type)",
            "CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read)",
            "CREATE INDEX IF NOT EXISTS idx_user_notification_preferences_user_id ON user_notification_preferences(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_business_ai_settings_business_id ON business_ai_settings(business_id)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        conn.commit()
        cursor.close()
        conn.close()
    
    def _migrate_for_supabase(self, cursor):
        """Migrate database for Supabase authentication and add public IDs"""
        try:
            print("🔄 Running Supabase migration...")
            
            # Add supabase_id column if it doesn't exist
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS supabase_id UUID UNIQUE;
            """)
            
            # Make password_hash nullable (since Supabase handles auth)
            cursor.execute("""
                ALTER TABLE users 
                ALTER COLUMN password_hash DROP NOT NULL;
            """)
            
            # Add last_login column if it doesn't exist
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS last_login TIMESTAMP;
            """)
            
            # Create index on supabase_id for faster lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_users_supabase_id 
                ON users(supabase_id);
            """)
            
            print("✅ Supabase migration completed!")
            
            # Add public_id to businesses table
            print("🔄 Adding public_id to businesses...")
            cursor.execute("""
                ALTER TABLE businesses 
                ADD COLUMN IF NOT EXISTS public_id UUID UNIQUE DEFAULT gen_random_uuid();
            """)
            
            # Create index on public_id for faster lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_businesses_public_id 
                ON businesses(public_id);
            """)
            
            # Update existing businesses that don't have public_id
            cursor.execute("""
                UPDATE businesses 
                SET public_id = gen_random_uuid() 
                WHERE public_id IS NULL;
            """)
            
            # Add buying_intent column if it doesn't exist
            cursor.execute("""
                ALTER TABLE businesses 
                ADD COLUMN IF NOT EXISTS buying_intent TEXT;
            """)
            
            print("✅ Business public_id migration completed!")
            
        except Exception as e:
            print(f"⚠️ Migration error (might be expected): {e}")
            # Don't fail if migration has issues - table might already be migrated
    
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
    def create_business(self, user_id, name, website=None, description=None, buying_intent=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO businesses (user_id, name, website, description, buying_intent, public_id) 
            VALUES (%s, %s, %s, %s, %s, gen_random_uuid()) RETURNING id, public_id
        ''', (user_id, name, website, description, buying_intent))
        
        result = cursor.fetchone()
        business_id = result[0]
        public_id = result[1]
        
        conn.commit()
        cursor.close()
        conn.close()
        return {"id": business_id, "public_id": str(public_id)}
    
    def get_user_businesses(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute('''
            SELECT id, public_id, name, website, description, buying_intent, created_at 
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
            SELECT id, public_id, name, website, description, created_at 
            FROM businesses WHERE id = %s AND user_id = %s
        ''', (business_id, user_id))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            return dict(result)
        return None
    
    def get_business_by_public_id(self, public_id, user_id):
        """Get business by public_id instead of internal ID"""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute('''
            SELECT id, public_id, name, website, description, buying_intent, created_at 
            FROM businesses WHERE public_id = %s AND user_id = %s
        ''', (public_id, user_id))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            return dict(result)
        return None
    
    def update_business(self, business_id, name, website=None, description=None, buying_intent=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE businesses 
            SET name = %s, website = %s, description = %s, buying_intent = %s 
            WHERE id = %s
        ''', (name, website, description, buying_intent, business_id))
        
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
    

    
    # Global leads management
    def add_global_lead(self, platform, platform_id, title, content, author, url, score=0):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO global_leads (platform, platform_id, title, content, author, url, score) 
                VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
            ''', (platform, platform_id, title, content, author, url, score))
            
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
                   gl.url, gl.score, gl.created_at
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

    # Replies management
    def add_reply(self, business_lead_id, user_id, reply_content, status='pending'):
        """Add a new AI reply for a business lead."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO replies (business_lead_id, user_id, reply_content, status) 
                VALUES (%s, %s, %s, %s) RETURNING id
            ''', (business_lead_id, user_id, reply_content, status))
            
            reply_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            conn.close()
            return reply_id
        except psycopg2.IntegrityError:
            # Reply already exists for this lead
            cursor.close()
            conn.close()
            return None
    
    def update_reply_status(self, reply_id, status, platform_reply_id=None):
        """Update reply status (pending -> submitted -> posted)."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        update_fields = ['status = %s', 'updated_at = CURRENT_TIMESTAMP']
        params = [status]
        
        if status == 'submitted' and platform_reply_id:
            update_fields.append('platform_reply_id = %s')
            update_fields.append('submitted_at = CURRENT_TIMESTAMP')
            params.extend([platform_reply_id])
        
        params.append(reply_id)
        
        cursor.execute(f'''
            UPDATE replies 
            SET {', '.join(update_fields)}
            WHERE id = %s
        ''', params)
        
        success = cursor.rowcount > 0
        conn.commit()
        cursor.close()
        conn.close()
        return success
    
    def get_user_replies(self, user_id, status=None, limit=50):
        """Get replies for a user, optionally filtered by status."""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        base_query = '''
            SELECT r.*, bl.ai_score, 
                   gl.title as lead_title, gl.platform as lead_platform, gl.url as lead_url,
                   gl.author as lead_author,
                   b.name as business_name
            FROM replies r
            JOIN business_leads bl ON r.business_lead_id = bl.id
            JOIN global_leads gl ON bl.global_lead_id = gl.id
            JOIN businesses b ON bl.business_id = b.id
            WHERE r.user_id = %s
        '''
        
        params = [user_id]
        
        if status:
            base_query += ' AND r.status = %s'
            params.append(status)
        
        base_query += ' ORDER BY r.created_at DESC LIMIT %s'
        params.append(limit)
        
        cursor.execute(base_query, params)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [dict(row) for row in results]
    
    def get_reply_stats(self, user_id):
        """Get reply statistics for dashboard."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_replies,
                COUNT(CASE WHEN status = 'submitted' THEN 1 END) as submitted_replies,
                COUNT(CASE WHEN DATE(submitted_at) = CURRENT_DATE THEN 1 END) as replies_today,
                COUNT(CASE WHEN submitted_at >= CURRENT_DATE - INTERVAL '7 days' THEN 1 END) as replies_this_week
            FROM replies r
            JOIN business_leads bl ON r.business_lead_id = bl.id
            JOIN businesses b ON bl.business_id = b.id
            WHERE b.user_id = %s
        ''', (user_id,))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return {
            'total_replies': result[0] or 0,
            'submitted_replies': result[1] or 0,
            'replies_today': result[2] or 0,
            'replies_this_week': result[3] or 0
        }  
  # Platform settings management
    def get_user_platform_settings(self, user_id):
        """Get all platform settings for a user."""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute('''
            SELECT platform_id, is_active, auto_reply, confidence_threshold, write_reply_suggestion, updated_at
            FROM platform_settings
            WHERE user_id = %s
            ORDER BY platform_id
        ''', (user_id,))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [dict(row) for row in results]
    
    def get_platform_setting(self, user_id, platform_id):
        """Get specific platform setting for a user."""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute('''
            SELECT platform_id, is_active, auto_reply, confidence_threshold, write_reply_suggestion, updated_at
            FROM platform_settings
            WHERE user_id = %s AND platform_id = %s
        ''', (user_id, platform_id))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return dict(result) if result else None
    
    def update_platform_setting(self, user_id, platform_id, is_active=None, auto_reply=None, confidence_threshold=None, write_reply_suggestion=None):
        """Update platform settings for a user."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Build dynamic update query
        update_fields = ['updated_at = CURRENT_TIMESTAMP']
        params = []
        
        if is_active is not None:
            update_fields.append('is_active = %s')
            params.append(is_active)
        
        if auto_reply is not None:
            update_fields.append('auto_reply = %s')
            params.append(auto_reply)
        
        if confidence_threshold is not None:
            update_fields.append('confidence_threshold = %s')
            params.append(confidence_threshold)
        
        if write_reply_suggestion is not None:
            update_fields.append('write_reply_suggestion = %s')
            params.append(write_reply_suggestion)
        
        params.extend([user_id, platform_id])
        
        # Try to update existing record
        cursor.execute(f'''
            UPDATE platform_settings 
            SET {', '.join(update_fields)}
            WHERE user_id = %s AND platform_id = %s
        ''', params)
        
        # If no record exists, create one
        if cursor.rowcount == 0:
            cursor.execute('''
                INSERT INTO platform_settings (user_id, platform_id, is_active, auto_reply, confidence_threshold, write_reply_suggestion)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (
                user_id, 
                platform_id, 
                is_active if is_active is not None else False,
                auto_reply if auto_reply is not None else False,
                confidence_threshold if confidence_threshold is not None else 80,
                write_reply_suggestion if write_reply_suggestion is not None else False
            ))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
    
    def should_auto_reply(self, user_id, platform_id, ai_score):
        """Check if a lead should trigger an auto-reply based on platform settings."""
        setting = self.get_platform_setting(user_id, platform_id)
        if not setting:
            return False
        
        return (setting['is_active'] and 
                setting['auto_reply'] and 
                ai_score >= setting['confidence_threshold'])
    
    def should_write_reply_suggestion(self, user_id, platform_id):
        """Check if reply suggestions should be generated for this platform."""
        setting = self.get_platform_setting(user_id, platform_id)
        if not setting:
            return False
        
        return (setting['is_active'] and 
                setting['write_reply_suggestion']) 
   
    # Social accounts management
    def add_social_account(self, user_id, platform, username, password, notes=None):
        """Add a new social media account for a user."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Simple encryption for password (in production, use proper encryption)
        import base64
        password_encrypted = base64.b64encode(password.encode()).decode()
        
        try:
            cursor.execute('''
                INSERT INTO social_accounts (user_id, platform, username, password_encrypted, notes)
                VALUES (%s, %s, %s, %s, %s) RETURNING id
            ''', (user_id, platform, username, password_encrypted, notes))
            
            account_id = cursor.fetchone()[0]
            conn.commit()
            return account_id
        except psycopg2.IntegrityError:
            return None
        finally:
            cursor.close()
            conn.close()
    
    def get_user_social_accounts(self, user_id):
        """Get all social accounts for a user."""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute('''
            SELECT id, platform, username, is_active, is_verified, last_used, notes, created_at
            FROM social_accounts 
            WHERE user_id = %s 
            ORDER BY created_at DESC
        ''', (user_id,))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [dict(row) for row in results]
    
    def get_social_account_with_password(self, account_id, user_id):
        """Get social account with decrypted password (for internal use)."""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute('''
            SELECT id, platform, username, password_encrypted, is_active, is_verified, notes
            FROM social_accounts 
            WHERE id = %s AND user_id = %s
        ''', (account_id, user_id))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            account = dict(result)
            # Decrypt password
            import base64
            account['password'] = base64.b64decode(account['password_encrypted']).decode()
            del account['password_encrypted']
            return account
        return None
    
    def update_social_account_status(self, account_id, user_id, is_active):
        """Update the active status of a social account."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE social_accounts 
            SET is_active = %s 
            WHERE id = %s AND user_id = %s
        ''', (is_active, account_id, user_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        cursor.close()
        conn.close()
        
        return success
    
    def delete_social_account(self, account_id, user_id):
        """Delete a social account."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM social_accounts 
            WHERE id = %s AND user_id = %s
        ''', (account_id, user_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        cursor.close()
        conn.close()
        
        return success
    
    def update_social_account_last_used(self, account_id):
        """Update the last_used timestamp for a social account."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE social_accounts 
            SET last_used = CURRENT_TIMESTAMP 
            WHERE id = %s
        ''', (account_id,))
        
        conn.commit()
        cursor.close()
        conn.close()    

    # Notifications management
    def create_notification(self, user_id, notification_type, title, message, data=None, priority='normal'):
        """Create a new notification for a user."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO notifications (user_id, type, title, message, data, priority)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
            ''', (user_id, notification_type, title, message, json.dumps(data) if data else None, priority))
            
            notification_id = cursor.fetchone()[0]
            conn.commit()
            return notification_id
        except Exception as e:
            conn.rollback()
            return None
        finally:
            cursor.close()
            conn.close()
    
    def get_user_notifications(self, user_id, limit=50, unread_only=False):
        """Get notifications for a user."""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        where_clause = "WHERE user_id = %s"
        params = [user_id]
        
        if unread_only:
            where_clause += " AND is_read = FALSE"
        
        cursor.execute(f'''
            SELECT id, type, title, message, data, is_read, priority, created_at, read_at
            FROM notifications 
            {where_clause}
            ORDER BY created_at DESC 
            LIMIT %s
        ''', params + [limit])
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        notifications = []
        for row in results:
            notification = dict(row)
            # JSONB data is already parsed by psycopg2, no need to json.loads
            notifications.append(notification)
        
        return notifications
    
    def mark_notification_read(self, notification_id, user_id):
        """Mark a notification as read."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE notifications 
            SET is_read = TRUE, read_at = CURRENT_TIMESTAMP 
            WHERE id = %s AND user_id = %s
        ''', (notification_id, user_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        cursor.close()
        conn.close()
        
        return success
    
    def mark_all_notifications_read(self, user_id):
        """Mark all notifications as read for a user."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE notifications 
            SET is_read = TRUE, read_at = CURRENT_TIMESTAMP 
            WHERE user_id = %s AND is_read = FALSE
        ''', (user_id,))
        
        count = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()
        
        return count
    
    def get_unread_notification_count(self, user_id):
        """Get count of unread notifications for a user."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM notifications 
            WHERE user_id = %s AND is_read = FALSE
        ''', (user_id,))
        
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        return count
    
    def delete_notification(self, notification_id, user_id):
        """Delete a notification."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM notifications 
            WHERE id = %s AND user_id = %s
        ''', (notification_id, user_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        cursor.close()
        conn.close()
        
        return success
    
    # Notification preferences management
    def get_user_notification_preferences(self, user_id):
        """Get notification preferences for a user."""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute('''
            SELECT notification_type, email_enabled, push_enabled
            FROM user_notification_preferences 
            WHERE user_id = %s
        ''', (user_id,))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [dict(row) for row in results]
    
    def update_notification_preference(self, user_id, notification_type, email_enabled=None, push_enabled=None):
        """Update notification preferences for a user."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Insert or update preference
        cursor.execute('''
            INSERT INTO user_notification_preferences (user_id, notification_type, email_enabled, push_enabled)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (user_id, notification_type)
            DO UPDATE SET 
                email_enabled = COALESCE(%s, user_notification_preferences.email_enabled),
                push_enabled = COALESCE(%s, user_notification_preferences.push_enabled),
                updated_at = CURRENT_TIMESTAMP
        ''', (user_id, notification_type, email_enabled, push_enabled, email_enabled, push_enabled))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True
    
    def should_send_email_notification(self, user_id, notification_type):
        """Check if email notifications are enabled for a user and notification type."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT email_enabled FROM user_notification_preferences 
            WHERE user_id = %s AND notification_type = %s
        ''', (user_id, notification_type))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        # Default to True if no preference is set
        return result[0] if result else True    

    # Business AI settings management
    def get_business_ai_settings(self, business_id):
        """Get AI reply settings for a business."""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute('''
            SELECT * FROM business_ai_settings 
            WHERE business_id = %s
        ''', (business_id,))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            settings = dict(result)
            # Parse JSON fields
            if settings['service_links']:
                settings['service_links'] = settings['service_links']
            return settings
        
        # Return default settings if none exist
        return {
            'business_id': business_id,
            'persona': '',
            'instructions': '',
            'bad_words': [],
            'service_links': {},
            'tone': 'professional',
            'max_reply_length': 500,
            'include_links': True,
            'auto_reply_enabled': False,
            'confidence_threshold': 0.8
        }
    
    def update_business_ai_settings(self, business_id, settings):
        """Update AI reply settings for a business."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO business_ai_settings (
                business_id, persona, instructions, bad_words, service_links,
                tone, max_reply_length, include_links, auto_reply_enabled, confidence_threshold
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (business_id)
            DO UPDATE SET 
                persona = EXCLUDED.persona,
                instructions = EXCLUDED.instructions,
                bad_words = EXCLUDED.bad_words,
                service_links = EXCLUDED.service_links,
                tone = EXCLUDED.tone,
                max_reply_length = EXCLUDED.max_reply_length,
                include_links = EXCLUDED.include_links,
                auto_reply_enabled = EXCLUDED.auto_reply_enabled,
                confidence_threshold = EXCLUDED.confidence_threshold,
                updated_at = CURRENT_TIMESTAMP
        ''', (
            business_id,
            settings.get('persona', ''),
            settings.get('instructions', ''),
            settings.get('bad_words', []),
            json.dumps(settings.get('service_links', {})),
            settings.get('tone', 'professional'),
            settings.get('max_reply_length', 500),
            settings.get('include_links', True),
            settings.get('auto_reply_enabled', False),
            settings.get('confidence_threshold', 0.8)
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True    

    # Additional reply management methods
    def get_reply_by_id(self, reply_id, user_id):
        """Get a specific reply by ID, ensuring user ownership through business"""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute('''
            SELECT r.*, bl.business_id, gl.title as lead_title, gl.url as lead_url, 
                   gl.platform as lead_platform, 
                   gl.author as lead_author, bl.ai_score
            FROM replies r
            JOIN business_leads bl ON r.business_lead_id = bl.id
            JOIN businesses b ON bl.business_id = b.id
            JOIN global_leads gl ON bl.global_lead_id = gl.id
            WHERE r.id = %s AND b.user_id = %s
        ''', (reply_id, user_id))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return dict(result) if result else None
    
    def update_reply_content(self, reply_id, content):
        """Update reply content"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE replies 
            SET reply_content = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s AND status = 'draft'
        ''', (content, reply_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        cursor.close()
        conn.close()
        
        return success
    
    def delete_reply(self, reply_id, user_id):
        """Delete a reply (only drafts and failed)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM replies 
            WHERE id = %s 
            AND status IN ('draft', 'failed')
            AND business_lead_id IN (
                SELECT bl.id FROM business_leads bl
                JOIN businesses b ON bl.business_id = b.id
                WHERE b.user_id = %s
            )
        ''', (reply_id, user_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        cursor.close()
        conn.close()
        
        return success