#!/usr/bin/env python3
"""
Migration script to update the users table for Supabase authentication
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def migrate_users_table():
    """Add Supabase support to users table"""
    
    # Database connection
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'reddit_leads'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'password'),
        port=os.getenv('DB_PORT', '5432')
    )
    
    cursor = conn.cursor()
    
    try:
        print("🔄 Migrating users table for Supabase authentication...")
        
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
        
        conn.commit()
        print("✅ Users table migration completed successfully!")
        
        # Show updated table structure
        cursor.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print("\n📋 Updated users table structure:")
        for col_name, data_type, nullable in columns:
            print(f"  - {col_name}: {data_type} ({'NULL' if nullable == 'YES' else 'NOT NULL'})")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        raise
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    migrate_users_table()