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
import logging
from dotenv import load_dotenv

from database import Database
from deepseek_analyzer import DeepSeekAnalyzer
from supabase_auth import SupabaseAuth

load_dotenv()

# Also try to load from server/.env if we're in a Docker container
if os.path.exists('/app/server/.env'):
    load_dotenv('/app/server/.env')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
supabase_auth = SupabaseAuth()

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
        logger.info(f"🔍 Verifying token: {credentials.credentials[:20]}...")
        
        # Verify Supabase token
        user_data = supabase_auth.verify_token(credentials.credentials)
        if not user_data:
            logger.warning("❌ Token verification failed - invalid token")
            raise HTTPException(status_code=401, detail="Invalid token")
        
        logger.info(f"✅ Token verified for user: {user_data.get('email')} (ID: {user_data.get('user_id')})")
        
        # Create or update user profile in local database
        supabase_auth.create_or_update_user_profile(user_data)
        
        # Get local user ID
        local_user_id = supabase_auth.get_local_user_id(user_data['user_id'])
        if not local_user_id:
            logger.warning(f"❌ User {user_data.get('user_id')} not found in local database")
            raise HTTPException(status_code=401, detail="User not found in local database")
        
        logger.info(f"✅ Local user ID: {local_user_id}")
        return local_user_id
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Token verification error: {e}")
        raise HTTPException(status_code=401, detail="Token verification failed")

# Routes
@app.get("/")
async def root():
    return {"message": "Reddit Lead Finder API v2", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint for Docker and Coolify"""
    try:
        # Test database connection with timeout
        import psycopg2
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        conn.close()
        
        return {
            "status": "healthy",
            "service": "Reddit Lead Finder API v2",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        # Return 200 but with unhealthy status during startup
        return {
            "status": "starting",
            "service": "Reddit Lead Finder API v2",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "connecting",
            "error": str(e)
        }

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

# Dashboard endpoint
@app.get("/api/dashboard")
async def get_dashboard_data(user_id: int = Depends(verify_jwt_token)):
    """Get dashboard data including metrics, leads stats, and activity."""
    try:
        logger.info(f"Dashboard request for user_id: {user_id}")
        
        # Get user's businesses
        businesses = db.get_user_businesses(user_id)
        logger.info(f"Found {len(businesses)} businesses for user {user_id}")
        
        if not businesses:
            logger.warning(f"No businesses found for user {user_id}")
            return {
                "metrics": {
                    "totalLeads": 0,
                    "leadsToday": 0,
                    "leadsThisWeek": 0,
                    "highQualityLeads": 0
                },
                "platformStats": [],
                "recentActivity": [],
                "businessStats": []
            }
        
        # Calculate metrics across all businesses using direct SQL for accuracy
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Get business IDs for this user
        business_ids = tuple(b['id'] for b in businesses)
        
        # Get total leads for user's businesses
        cursor.execute('''
            SELECT COUNT(*) FROM business_leads 
            WHERE business_id = ANY(%s)
        ''', (list(business_ids),))
        total_leads = cursor.fetchone()[0]
        
        # Get today's leads (using current date)
        cursor.execute('''
            SELECT COUNT(*) FROM business_leads 
            WHERE business_id = ANY(%s)
            AND DATE(processed_at) = CURRENT_DATE
        ''', (list(business_ids),))
        leads_today = cursor.fetchone()[0]
        
        # Get this week's leads
        cursor.execute('''
            SELECT COUNT(*) FROM business_leads 
            WHERE business_id = ANY(%s)
            AND processed_at >= CURRENT_DATE - INTERVAL '7 days'
        ''', (list(business_ids),))
        leads_this_week = cursor.fetchone()[0]
        
        # Get high quality leads (80%+)
        cursor.execute('''
            SELECT COUNT(*) FROM business_leads 
            WHERE business_id = ANY(%s)
            AND ai_score >= 80
        ''', (list(business_ids),))
        high_quality_leads = cursor.fetchone()[0]
        
        logger.info(f"SQL Results - Total: {total_leads}, Today: {leads_today}, Week: {leads_this_week}, High Quality: {high_quality_leads}")
        
        platform_stats = {}
        recent_activity = []
        business_stats = []
        
        from datetime import datetime, timedelta
        now = datetime.now()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = today - timedelta(days=7)
        
        logger.info(f"Today: {today}, Week ago: {week_ago}")
        
        # Get platform stats
        cursor.execute('''
            SELECT gl.platform, COUNT(*) as lead_count
            FROM business_leads bl
            JOIN global_leads gl ON bl.global_lead_id = gl.id
            WHERE bl.business_id = ANY(%s)
            GROUP BY gl.platform
        ''', (list(business_ids),))
        platform_results = cursor.fetchall()
        
        for platform, count in platform_results:
            platform_stats[platform] = {
                'leads': count,
                'businesses': len([b for b in businesses])  # All businesses could potentially have this platform
            }
        
        # Get recent activity (last 10 leads)
        cursor.execute('''
            SELECT bl.id, b.name as business_name, gl.title, gl.platform, bl.ai_score, bl.processed_at
            FROM business_leads bl
            JOIN businesses b ON bl.business_id = b.id
            JOIN global_leads gl ON bl.global_lead_id = gl.id
            WHERE bl.business_id = ANY(%s)
            ORDER BY bl.processed_at DESC
            LIMIT 10
        ''', (list(business_ids),))
        activity_results = cursor.fetchall()
        
        for row in activity_results:
            recent_activity.append({
                'id': row[0],
                'business': row[1],
                'title': row[2][:50] + '...' if len(row[2]) > 50 else row[2],
                'platform': row[3],
                'score': row[4],
                'processed_at': row[5]
            })
        
        # Get individual business stats
        for business in businesses:
            business_id = business['id']
            business_name = business['name']
            
            # Get counts for this specific business
            cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN DATE(processed_at) = DATE('now') THEN 1 ELSE 0 END) as today,
                    SUM(CASE WHEN DATE(processed_at) >= DATE('now', '-7 days') THEN 1 ELSE 0 END) as week,
                    SUM(CASE WHEN ai_score >= 80 THEN 1 ELSE 0 END) as high_quality
                FROM business_leads 
                WHERE business_id = ?
            ''', (business_id,))
            
            result = cursor.fetchone()
            business_stats.append({
                'id': business_id,
                'name': business_name,
                'totalLeads': result[0] or 0,
                'leadsToday': result[1] or 0,
                'leadsThisWeek': result[2] or 0,
                'highQualityLeads': result[3] or 0
            })
        
        conn.close()
        
        # Format platform stats
        formatted_platform_stats = []
        for platform, stats in platform_stats.items():
            formatted_platform_stats.append({
                'platform': platform,
                'leads': stats['leads'],
                'businesses': len(stats['businesses'])
            })
        
        # Sort recent activity by processed_at
        recent_activity.sort(key=lambda x: x['processed_at'], reverse=True)
        
        return {
            "metrics": {
                "totalLeads": total_leads,
                "leadsToday": leads_today,
                "leadsThisWeek": leads_this_week,
                "highQualityLeads": high_quality_leads
            },
            "platformStats": formatted_platform_stats,
            "recentActivity": recent_activity[:10],
            "businessStats": business_stats
        }
        
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to load dashboard data")

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
    import time
    
    print("🚀 Starting Reddit Lead Finder API v2...")
    
    # Wait for database to be ready
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            print(f"🔍 Attempting to connect to database (attempt {retry_count + 1}/{max_retries})...")
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            conn.close()
            print("✅ Database connection successful!")
            break
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            retry_count += 1
            if retry_count < max_retries:
                print(f"⏳ Waiting 2 seconds before retry...")
                time.sleep(2)
            else:
                print("💥 Max retries reached. Exiting...")
                exit(1)
    
    # Get port from environment or use default
    port = int(os.getenv("BACKEND_PORT", 6070))
    print(f"🌐 Starting server on 0.0.0.0:{port}")
    
    uvicorn.run(app, host="0.0.0.0", port=port)