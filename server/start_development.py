#!/usr/bin/env python3
"""
Development startup script for Reddit Lead Finder API
Uses Uvicorn with hot reload for development
"""
import os
import sys
from pathlib import Path

# Add the server directory to Python path
server_dir = Path(__file__).parent
sys.path.insert(0, str(server_dir))

def main():
    """Main startup function for development"""
    print("🚀 Starting Reddit Lead Finder API v2 (Development)")
    print("=" * 60)
    
    # Set environment variables for development
    os.environ.setdefault("PYTHONPATH", str(server_dir))
    
    # Import and run the API server directly
    from api_server import app
    import uvicorn
    
    # Get port from environment or use default
    port = int(os.getenv("BACKEND_PORT", 6070))
    
    print(f"🌐 Starting development server on 0.0.0.0:{port}")
    print("🔄 Hot reload enabled")
    print("=" * 60)
    
    # Start Uvicorn with hot reload
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        reload_dirs=[str(server_dir)],
        log_level="info"
    )

if __name__ == "__main__":
    main()