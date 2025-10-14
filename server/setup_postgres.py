#!/usr/bin/env python3
"""
PostgreSQL setup script for Reddit Lead Finder
"""

import os
import sys
import subprocess
from dotenv import load_dotenv

load_dotenv()

def check_postgresql_installed():
    """Check if PostgreSQL is installed and running."""
    try:
        result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ PostgreSQL found: {result.stdout.strip()}")
            return True
        else:
            print("❌ PostgreSQL not found")
            return False
    except FileNotFoundError:
        print("❌ PostgreSQL not installed")
        return False

def check_postgresql_running():
    """Check if PostgreSQL service is running."""
    try:
        # Try to connect to PostgreSQL
        result = subprocess.run(['pg_isready'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ PostgreSQL service is running")
            return True
        else:
            print("❌ PostgreSQL service is not running")
            return False
    except FileNotFoundError:
        print("❌ pg_isready command not found")
        return False

def create_database():
    """Create the Reddit leads database."""
    db_name = os.getenv('DB_NAME', 'reddit_leads')
    db_user = os.getenv('DB_USER', 'postgres')
    
    print(f"🔧 Creating database '{db_name}'...")
    
    try:
        # Try to create database
        result = subprocess.run([
            'createdb', 
            '-h', os.getenv('DB_HOST', 'localhost'),
            '-p', os.getenv('DB_PORT', '5432'),
            '-U', db_user,
            db_name
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Database '{db_name}' created successfully")
            return True
        elif 'already exists' in result.stderr:
            print(f"ℹ️  Database '{db_name}' already exists")
            return True
        else:
            print(f"❌ Failed to create database: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ createdb command not found")
        return False

def test_database_connection():
    """Test connection to the database."""
    print("🔍 Testing database connection...")
    
    try:
        from database import Database
        db = Database()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

def run_migration():
    """Run the migration from SQLite to PostgreSQL."""
    print("🚀 Running migration from SQLite to PostgreSQL...")
    
    try:
        from migrate_to_postgres import create_postgres_tables, migrate_data, verify_migration
        
        print("1. Creating PostgreSQL tables...")
        create_postgres_tables()
        
        print("2. Migrating data...")
        migrate_data()
        
        print("3. Verifying migration...")
        verify_migration()
        
        print("✅ Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main setup function."""
    print("🐘 POSTGRESQL SETUP FOR REDDIT LEAD FINDER")
    print("=" * 50)
    
    # Check if PostgreSQL is installed
    if not check_postgresql_installed():
        print("\n📝 To install PostgreSQL:")
        print("  macOS: brew install postgresql")
        print("  Ubuntu: sudo apt-get install postgresql postgresql-contrib")
        print("  Windows: Download from https://www.postgresql.org/download/")
        return False
    
    # Check if PostgreSQL is running
    if not check_postgresql_running():
        print("\n📝 To start PostgreSQL:")
        print("  macOS: brew services start postgresql")
        print("  Ubuntu: sudo systemctl start postgresql")
        print("  Windows: Start PostgreSQL service from Services")
        return False
    
    # Create database
    if not create_database():
        return False
    
    # Test database connection
    if not test_database_connection():
        return False
    
    # Ask user if they want to migrate from SQLite
    if os.path.exists('reddit_leads_v2.db'):
        print(f"\n📊 SQLite database found: reddit_leads_v2.db")
        migrate = input("Do you want to migrate data from SQLite to PostgreSQL? (y/n): ").lower().strip()
        
        if migrate == 'y':
            if not run_migration():
                return False
        else:
            print("ℹ️  Skipping migration. You can run it later with: python migrate_to_postgres.py")
    else:
        print("ℹ️  No SQLite database found. Starting with fresh PostgreSQL database.")
    
    print(f"\n🎉 PostgreSQL setup completed successfully!")
    print(f"\n📝 Configuration:")
    print(f"  Database: {os.getenv('DB_NAME', 'reddit_leads')}")
    print(f"  Host: {os.getenv('DB_HOST', 'localhost')}")
    print(f"  Port: {os.getenv('DB_PORT', '5432')}")
    print(f"  User: {os.getenv('DB_USER', 'postgres')}")
    
    print(f"\n🚀 Next steps:")
    print(f"  1. Start the application: ./start-app.sh")
    print(f"  2. Visit: http://localhost:3050")
    print(f"  3. Login with: test@example.com / test@example.com")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)