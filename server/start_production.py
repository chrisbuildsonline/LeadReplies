#!/usr/bin/env python3
"""
Production startup script for Reddit Lead Finder API
Uses Gunicorn with proper configuration for production deployment
"""
import os
import sys
import time
from pathlib import Path

# Add the server directory to Python path
server_dir = Path(__file__).parent
sys.path.insert(0, str(server_dir))

def wait_for_database():
    """Wait for database to be ready before starting the server"""
    from database import Database
    
    max_retries = 30
    retry_count = 0
    
    print("🔍 Waiting for database to be ready...")
    
    while retry_count < max_retries:
        try:
            print(f"🔍 Attempting to connect to database (attempt {retry_count + 1}/{max_retries})...")
            db = Database()
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            conn.close()
            print("✅ Database connection successful!")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            retry_count += 1
            if retry_count < max_retries:
                print(f"⏳ Waiting 2 seconds before retry...")
                time.sleep(2)
            else:
                print("💥 Max retries reached. Database not available.")
                return False
    
    return False

def main():
    """Main startup function"""
    print("🚀 Starting Reddit Lead Finder API v2 (Production)")
    print("=" * 60)
    
    # Wait for database
    if not wait_for_database():
        print("❌ Failed to connect to database. Exiting.")
        sys.exit(1)
    
    # Set environment variables for production
    os.environ.setdefault("PYTHONPATH", str(server_dir))
    
    # Start Gunicorn
    print("🌐 Starting Gunicorn server...")
    print(f"📍 Server will be available on port {os.getenv('BACKEND_PORT', '6070')}")
    print("=" * 60)
    
    # Import and run Gunicorn
    from gunicorn.app.wsgiapp import WSGIApplication
    
    # Gunicorn arguments
    sys.argv = [
        "gunicorn",
        "--config", "gunicorn.conf.py",
        "api_server:app"
    ]
    
    # Start Gunicorn
    WSGIApplication("%(prog)s [OPTIONS] [APP_MODULE]").run()

if __name__ == "__main__":
    main()