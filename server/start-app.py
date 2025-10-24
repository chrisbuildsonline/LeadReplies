#!/usr/bin/env python3
import uvicorn
from api_server import app

if __name__ == "__main__":
    print("🚀 Starting LeadReplier API server...")
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=6070,
        reload=True,
        log_level="info"
    )