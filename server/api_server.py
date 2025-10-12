#!/usr/bin/env python3
"""
Multi-tenant FastAPI server for Reddit Lead Finder
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import jwt
import bcrypt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

from database import Database
from deepseek_analyzer import DeepSeekAnalyzer

load_dotenv()

app = FastAPI(title="Reddit Lead Finder API v2")
security = HTTPBearer()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
db = Database()
ai_analyzer = DeepSeekAnalyzer()

# JWT settings
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-this")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Pydantic models
class UserRegister(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class BusinessCreate(BaseModel):
    name: str
    website: Optional[str] = None
    description: Optional[str] = None

class KeywordAdd(BaseModel):
    keyword: str
    source: str = "manual"

class SubredditAdd(BaseModel):
    subreddit: str
    source: str = "manual"

class WebsiteAnalyze(BaseModel):
    website_url: str

# Helper functions
def create_jwt_token(user_id: int) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_jwt_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Routes
@app.get("/")
async def root():
    return {"message": "Reddit Lead Finder API v2", "status": "running"}

# Authentication endpoints
@app.post("/api/auth/register")
async def register(user: UserRegister):
    user_id = db.create_user(user.email, user.password)
    if user_id is None:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    token = create_jwt_token(user_id)
    return {"token": token, "user_id": user_id}

@app.post("/api/auth/login")
async def login(user: UserLogin):
    user_id = db.verify_user(user.email, user.password)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_jwt_token(user_id)
    user_data = db.get_user(user_id)
    return {"token": token, "user": user_data}

@app.get("/api/auth/me")
async def get_current_user(user_id: int = Depends(verify_jwt_token)):
    user = db.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user": user}

# Business management
@app.post("/api/businesses")
async def create_business(business: BusinessCreate, user_id: int = Depends(verify_jwt_token)):
    business_id = db.create_business(user_id, business.name, business.website, business.description)
    return {"business_id": business_id}

@app.get("/api/businesses")
async def get_businesses(user_id: int = Depends(verify_jwt_token)):
    businesses = db.get_user_businesses(user_id)
    return {"businesses": businesses}

@app.get("/api/businesses/{business_id}")
async def get_business(business_id: int, user_id: int = Depends(verify_jwt_token)):
    business = db.get_business(business_id, user_id)
    if business is None:
        raise HTTPException(status_code=404, detail="Business not found")
    return {"business": business}

@app.put("/api/businesses/{business_id}")
async def update_business(business_id: int, business: BusinessCreate, user_id: int = Depends(verify_jwt_token)):
    # Verify business ownership
    existing_business = db.get_business(business_id, user_id)
    if existing_business is None:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Update business (we'll need to add this method to the database)
    success = db.update_business(business_id, business.name, business.website, business.description)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update business")
    
    return {"success": True}

# Website analysis
@app.post("/api/businesses/{business_id}/analyze-website")
async def analyze_website(business_id: int, data: WebsiteAnalyze, user_id: int = Depends(verify_jwt_token)):
    # Verify business ownership
    business = db.get_business(business_id, user_id)
    if business is None:
        raise HTTPException(status_code=404, detail="Business not found")
    
    try:
        # Analyze website for keywords
        keywords = ai_analyzer.analyze_website_for_keywords(data.website_url, business['name'])
        
        # Suggest subreddits
        keyword_list = [kw['keyword'] for kw in keywords]
        subreddits = ai_analyzer.suggest_subreddits_for_keywords(keyword_list, business['name'])
        
        return {
            "keywords": keywords,
            "subreddits": subreddits
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# Keywords management
@app.post("/api/businesses/{business_id}/keywords")
async def add_keyword(business_id: int, keyword: KeywordAdd, user_id: int = Depends(verify_jwt_token)):
    # Verify business ownership
    business = db.get_business(business_id, user_id)
    if business is None:
        raise HTTPException(status_code=404, detail="Business not found")
    
    db.add_keyword(business_id, keyword.keyword, keyword.source)
    return {"success": True}

@app.get("/api/businesses/{business_id}/keywords")
async def get_keywords(business_id: int, user_id: int = Depends(verify_jwt_token)):
    # Verify business ownership
    business = db.get_business(business_id, user_id)
    if business is None:
        raise HTTPException(status_code=404, detail="Business not found")
    
    keywords = db.get_business_keywords(business_id)
    return {"keywords": keywords}

@app.delete("/api/businesses/{business_id}/keywords/{keyword_id}")
async def remove_keyword(business_id: int, keyword_id: int, user_id: int = Depends(verify_jwt_token)):
    # Verify business ownership
    business = db.get_business(business_id, user_id)
    if business is None:
        raise HTTPException(status_code=404, detail="Business not found")
    
    db.remove_keyword(keyword_id, business_id)
    return {"success": True}

# Subreddits management
@app.post("/api/businesses/{business_id}/subreddits")
async def add_subreddit(business_id: int, subreddit: SubredditAdd, user_id: int = Depends(verify_jwt_token)):
    # Verify business ownership
    business = db.get_business(business_id, user_id)
    if business is None:
        raise HTTPException(status_code=404, detail="Business not found")
    
    db.add_subreddit(business_id, subreddit.subreddit, subreddit.source)
    return {"success": True}

@app.get("/api/businesses/{business_id}/subreddits")
async def get_subreddits(business_id: int, user_id: int = Depends(verify_jwt_token)):
    # Verify business ownership
    business = db.get_business(business_id, user_id)
    if business is None:
        raise HTTPException(status_code=404, detail="Business not found")
    
    subreddits = db.get_business_subreddits(business_id)
    return {"subreddits": subreddits}

@app.delete("/api/businesses/{business_id}/subreddits/{subreddit_id}")
async def remove_subreddit(business_id: int, subreddit_id: int, user_id: int = Depends(verify_jwt_token)):
    # Verify business ownership
    business = db.get_business(business_id, user_id)
    if business is None:
        raise HTTPException(status_code=404, detail="Business not found")
    
    db.remove_subreddit(subreddit_id, business_id)
    return {"success": True}

# Leads management
@app.get("/api/businesses/{business_id}/leads")
async def get_business_leads(business_id: int, limit: int = 50, user_id: int = Depends(verify_jwt_token)):
    # Verify business ownership
    business = db.get_business(business_id, user_id)
    if business is None:
        raise HTTPException(status_code=404, detail="Business not found")
    
    leads = db.get_business_leads(business_id, limit)
    return {"leads": leads, "total": len(leads)}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Reddit Lead Finder API v2...")
    uvicorn.run(app, host="0.0.0.0", port=8001)