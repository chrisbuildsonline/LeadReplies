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
    print(f"📁 Working directory: {os.getcwd()}")
    print(f"📁 Server directory: {server_dir}")
    print(f"🐍 Python path: {sys.path[:3]}...")  # Show first 3 entries
    
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
    
    # Import and configure Gunicorn directly
    from gunicorn.app.base import BaseApplication
    import multiprocessing
    
    class StandaloneApplication(BaseApplication):
        def __init__(self, app, options=None):
            self.options = options or {}
            self.application = app
            super().__init__()

        def load_config(self):
            config = {key: value for key, value in self.options.items()
                     if key in self.cfg.settings and value is not None}
            for key, value in config.items():
                self.cfg.set(key.lower(), value)

        def load(self):
            return self.application
    
    # Import the FastAPI app
    from api_server import app
    
    # Gunicorn configuration
    port = int(os.getenv('BACKEND_PORT', '6070'))
    options = {
        'bind': f'0.0.0.0:{port}',
        'workers': multiprocessing.cpu_count() * 2 + 1,
        'worker_class': 'uvicorn.workers.UvicornWorker',
        'worker_connections': 1000,
        'timeout': 30,
        'keepalive': 2,
        'max_requests': 1000,
        'max_requests_jitter': 50,
        'preload_app': True,
        'accesslog': '-',
        'errorlog': '-',
        'loglevel': 'info',
        'proc_name': 'reddit-lead-finder-api'
    }
    
    # Start Gunicorn
    try:
        print("🚀 Starting with Gunicorn...")
        StandaloneApplication(app, options).run()
    except Exception as e:
        print(f"❌ Gunicorn failed to start: {e}")
        print("🔄 Falling back to Uvicorn...")
        
        # Fallback to Uvicorn
        import uvicorn
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info",
            access_log=True
        )

if __name__ == "__main__":
    main()