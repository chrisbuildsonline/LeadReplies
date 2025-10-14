#!/usr/bin/env python3
"""
Migration script to move from SQLite to PostgreSQL
"""

import sqlite3
import psycopg2
import json
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# PostgreSQL connection
def get_postgres_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'reddit_leads'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'password'),
        port=os.getenv('DB_PORT', '5432')
    )

def create_postgres_tables():
    """Create PostgreSQL tables with proper schema"""
    conn = get_postgres_connection()
    cursor = conn.cursor()
    
    # Drop existing tables if they exist (in correct order due to foreign keys)
    drop_tables = [
        "DROP TABLE IF EXISTS business_leads CASCADE;",
        "DROP TABLE IF EXISTS global_leads CASCADE;",
        "DROP TABLE IF EXISTS subreddits CASCADE;",
        "DROP TABLE IF EXISTS keywords CASCADE;",
        "DROP TABLE IF EXISTS businesses CASCADE;",
        "DROP TABLE IF EXISTS users CASCADE;"
    ]
    
    for drop_sql in drop_tables:
        cursor.execute(drop_sql)
    
    # Create tables
    tables = [
        """
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE businesses (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            name VARCHAR(255) NOT NULL,
            website TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE keywords (
            id SERIAL PRIMARY KEY,
            business_id INTEGER NOT NULL,
            keyword VARCHAR(255) NOT NULL,
            source VARCHAR(50) DEFAULT 'manual',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (business_id) REFERENCES businesses (id) ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE subreddits (
            id SERIAL PRIMARY KEY,
            business_id INTEGER NOT NULL,
            subreddit VARCHAR(255) NOT NULL,
            source VARCHAR(50) DEFAULT 'manual',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (business_id) REFERENCES businesses (id) ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE global_leads (
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
        );
        """,
        """
        CREATE TABLE business_leads (
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
        );
        """
    ]
    
    for table_sql in tables:
        cursor.execute(table_sql)
    
    # Create indexes for better performance
    indexes = [
        "CREATE INDEX idx_businesses_user_id ON businesses(user_id);",
        "CREATE INDEX idx_keywords_business_id ON keywords(business_id);",
        "CREATE INDEX idx_subreddits_business_id ON subreddits(business_id);",
        "CREATE INDEX idx_global_leads_platform ON global_leads(platform, platform_id);",
        "CREATE INDEX idx_business_leads_business_id ON business_leads(business_id);",
        "CREATE INDEX idx_business_leads_processed_at ON business_leads(processed_at);",
        "CREATE INDEX idx_business_leads_ai_score ON business_leads(ai_score);"
    ]
    
    for index_sql in indexes:
        cursor.execute(index_sql)
    
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ PostgreSQL tables created successfully!")

def migrate_data():
    """Migrate data from SQLite to PostgreSQL"""
    # Connect to SQLite
    sqlite_conn = sqlite3.connect('reddit_leads_v2.db')
    sqlite_cursor = sqlite_conn.cursor()
    
    # Connect to PostgreSQL
    pg_conn = get_postgres_connection()
    pg_cursor = pg_conn.cursor()
    
    # Migrate users
    print("Migrating users...")
    sqlite_cursor.execute("SELECT id, email, password_hash, created_at FROM users")
    users = sqlite_cursor.fetchall()
    
    for user in users:
        pg_cursor.execute(
            "INSERT INTO users (id, email, password_hash, created_at) VALUES (%s, %s, %s, %s)",
            user
        )
    
    # Update sequence
    if users:
        max_id = max(user[0] for user in users)
        pg_cursor.execute(f"SELECT setval('users_id_seq', {max_id});")
    
    print(f"✅ Migrated {len(users)} users")
    
    # Migrate businesses
    print("Migrating businesses...")
    sqlite_cursor.execute("SELECT id, user_id, name, website, description, created_at FROM businesses")
    businesses = sqlite_cursor.fetchall()
    
    for business in businesses:
        pg_cursor.execute(
            "INSERT INTO businesses (id, user_id, name, website, description, created_at) VALUES (%s, %s, %s, %s, %s, %s)",
            business
        )
    
    if businesses:
        max_id = max(business[0] for business in businesses)
        pg_cursor.execute(f"SELECT setval('businesses_id_seq', {max_id});")
    
    print(f"✅ Migrated {len(businesses)} businesses")
    
    # Migrate keywords
    print("Migrating keywords...")
    sqlite_cursor.execute("SELECT id, business_id, keyword, source, created_at FROM keywords")
    keywords = sqlite_cursor.fetchall()
    
    for keyword in keywords:
        pg_cursor.execute(
            "INSERT INTO keywords (id, business_id, keyword, source, created_at) VALUES (%s, %s, %s, %s, %s)",
            keyword
        )
    
    if keywords:
        max_id = max(keyword[0] for keyword in keywords)
        pg_cursor.execute(f"SELECT setval('keywords_id_seq', {max_id});")
    
    print(f"✅ Migrated {len(keywords)} keywords")
    
    # Migrate subreddits
    print("Migrating subreddits...")
    sqlite_cursor.execute("SELECT id, business_id, subreddit, source, created_at FROM subreddits")
    subreddits = sqlite_cursor.fetchall()
    
    for subreddit in subreddits:
        pg_cursor.execute(
            "INSERT INTO subreddits (id, business_id, subreddit, source, created_at) VALUES (%s, %s, %s, %s, %s)",
            subreddit
        )
    
    if subreddits:
        max_id = max(subreddit[0] for subreddit in subreddits)
        pg_cursor.execute(f"SELECT setval('subreddits_id_seq', {max_id});")
    
    print(f"✅ Migrated {len(subreddits)} subreddits")
    
    # Migrate global_leads
    print("Migrating global leads...")
    sqlite_cursor.execute("SELECT id, platform, platform_id, title, content, author, url, subreddit, score, created_at, scraped_at FROM global_leads")
    global_leads = sqlite_cursor.fetchall()
    
    for lead in global_leads:
        pg_cursor.execute(
            "INSERT INTO global_leads (id, platform, platform_id, title, content, author, url, subreddit, score, created_at, scraped_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            lead
        )
    
    if global_leads:
        max_id = max(lead[0] for lead in global_leads)
        pg_cursor.execute(f"SELECT setval('global_leads_id_seq', {max_id});")
    
    print(f"✅ Migrated {len(global_leads)} global leads")
    
    # Migrate business_leads
    print("Migrating business leads...")
    sqlite_cursor.execute("SELECT id, business_id, global_lead_id, ai_score, ai_reasoning, matched_keywords, processed_at FROM business_leads")
    business_leads = sqlite_cursor.fetchall()
    
    for lead in business_leads:
        pg_cursor.execute(
            "INSERT INTO business_leads (id, business_id, global_lead_id, ai_score, ai_reasoning, matched_keywords, processed_at) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            lead
        )
    
    if business_leads:
        max_id = max(lead[0] for lead in business_leads)
        pg_cursor.execute(f"SELECT setval('business_leads_id_seq', {max_id});")
    
    print(f"✅ Migrated {len(business_leads)} business leads")
    
    # Commit all changes
    pg_conn.commit()
    
    # Close connections
    sqlite_cursor.close()
    sqlite_conn.close()
    pg_cursor.close()
    pg_conn.close()
    
    print("🎉 Data migration completed successfully!")

def verify_migration():
    """Verify the migration was successful"""
    pg_conn = get_postgres_connection()
    pg_cursor = pg_conn.cursor()
    
    tables = ['users', 'businesses', 'keywords', 'subreddits', 'global_leads', 'business_leads']
    
    print("\n📊 Migration Verification:")
    for table in tables:
        pg_cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = pg_cursor.fetchone()[0]
        print(f"  {table}: {count} records")
    
    pg_cursor.close()
    pg_conn.close()

if __name__ == "__main__":
    print("🚀 Starting PostgreSQL migration...")
    
    try:
        print("1. Creating PostgreSQL tables...")
        create_postgres_tables()
        
        print("2. Migrating data...")
        migrate_data()
        
        print("3. Verifying migration...")
        verify_migration()
        
        print("\n✅ Migration completed successfully!")
        print("📝 Next steps:")
        print("   1. Update your .env file with PostgreSQL settings")
        print("   2. Update database.py to use PostgreSQL")
        print("   3. Install psycopg2: pip install psycopg2-binary")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()