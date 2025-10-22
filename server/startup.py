#!/usr/bin/env python3
"""
Startup script for Reddit Lead Finder API
Ensures database is ready before starting the API server
"""

import os
import sys
import time
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def wait_for_database():
    """Wait for PostgreSQL database to be ready"""
    try:
        from database import Database
        
        max_retries = 60  # 2 minutes max wait
        retry_count = 0
        
        logger.info("🔍 Waiting for database to be ready...")
        
        while retry_count < max_retries:
            try:
                logger.info(f"📡 Database connection attempt {retry_count + 1}/{max_retries}")
                
                db = Database()
                conn = db.get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.close()
                conn.close()
                
                logger.info("✅ Database is ready!")
                return True
                
            except Exception as e:
                logger.warning(f"⚠️ Database not ready: {e}")
                retry_count += 1
                
                if retry_count < max_retries:
                    logger.info("⏳ Waiting 2 seconds before retry...")
                    time.sleep(2)
                else:
                    logger.error("❌ Database connection timeout!")
                    return False
                    
    except Exception as e:
        logger.error(f"❌ Database setup failed: {e}")
        return False

def start_api_server():
    """Start the FastAPI server"""
    try:
        import uvicorn
        from api_server import app
        
        port = int(os.getenv("BACKEND_PORT", 8001))
        logger.info(f"🚀 Starting Reddit Lead Finder API on port {port}")
        
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=port,
            log_level="info"
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to start API server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    logger.info("🚀 Reddit Lead Finder - Starting up...")
    
    # Wait for database
    if wait_for_database():
        # Start API server
        start_api_server()
    else:
        logger.error("❌ Startup failed - database not available")
        sys.exit(1)