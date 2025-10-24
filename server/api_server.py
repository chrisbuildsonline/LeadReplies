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

app = FastAPI(title="Lead Finder API v2")
security = HTTPBearer()

# CORS middleware
# CORS configuration
cors_origins_env = os.getenv("CORS_ORIGINS")
if cors_origins_env:
    # Use environment variable if set (comma-separated list)
    cors_origins = [origin.strip() for origin in cors_origins_env.split(",")]
elif os.getenv("NODE_ENV") == "production":
    # Allow all origins in production
    cors_origins = ["*"]
else:
    # Local development origins
    cors_origins = [
        "http://localhost:3000", 
        "http://localhost:3050", 
        "http://localhost:5173"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
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
    buying_intent: Optional[str] = None

class KeywordAdd(BaseModel):
    keyword: str
    source: str = "manual"



class WebsiteAnalyze(BaseModel):
    website_url: str

# Helper functions
def get_business_by_public_id_or_404(public_id: str, user_id: int):
    """Helper function to get business by public_id and raise 404 if not found"""
    logger.info(f"🔍 Looking for business {public_id} for user {user_id}")
    business = db.get_business_by_public_id(public_id, user_id)
    if business is None:
        logger.warning(f"❌ Business {public_id} not found for user {user_id}")
        
        # Debug: Check if business exists for any user
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM businesses WHERE public_id = %s", (public_id,))
        result = cursor.fetchone()
        if result:
            logger.warning(f"❌ Business {public_id} exists but belongs to user {result[0]}, not {user_id}")
        else:
            logger.warning(f"❌ Business {public_id} does not exist at all")
        cursor.close()
        conn.close()
        
        raise HTTPException(status_code=404, detail="Business not found")
    
    logger.info(f"✅ Found business {business['name']} (ID: {business['id']}) for user {user_id}")
    return business

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
    return {
        "message": "Lead Finder API v2", 
        "status": "running",
        "version": "2.1.0-uuid-fix",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/debug/businesses")
async def debug_businesses():
    """Debug endpoint to check all businesses"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, public_id, user_id, name FROM businesses LIMIT 10")
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        businesses = []
        for row in results:
            businesses.append({
                "internal_id": row[0],
                "public_id": str(row[1]) if row[1] else None,
                "user_id": row[2],
                "name": row[3]
            })
        
        return {"businesses": businesses}
    except Exception as e:
        return {"error": str(e)}

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
            "service": "Lead Finder API v2",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        # Return 200 but with unhealthy status during startup
        return {
            "status": "starting",
            "service": "Lead Finder API v2",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "connecting",
            "error": str(e)
        }

@app.get("/api/scraper/status")
async def get_scraper_status(user_id: int = Depends(verify_jwt_token)):
    """Get the status of the background scraping service"""
    try:
        # Import here to avoid circular imports
        from background_service import LeadScrapingService
        
        # Create a service instance to get status
        service = LeadScrapingService()
        status = service.get_status()
        
        # Transform to match frontend interface
        return {
            "is_active": status.get("status") == "running",
            "last_scrape": status.get("last_run"),
            "recent_activity": status.get("last_run") is not None,
            "status_message": f"Service {status.get('status', 'unknown')} - Next run in {status.get('interval_minutes', 120)} minutes"
        }
        
    except Exception as e:
        logger.error(f"Scraper status error: {e}")
        return {
            "is_active": False,
            "last_scrape": None,
            "recent_activity": False,
            "status_message": f"Service unavailable: {str(e)}"
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
    result = db.create_business(user_id, business.name, business.website, business.description, business.buying_intent)
    return {"business_id": result["public_id"], "id": result["public_id"]}

@app.get("/api/businesses")
async def get_businesses(user_id: int = Depends(verify_jwt_token)):
    logger.info(f"📋 Getting businesses for user {user_id}")
    businesses = db.get_user_businesses(user_id)
    logger.info(f"📋 Found {len(businesses)} businesses: {[b.get('name', 'Unknown') for b in businesses]}")
    
    # Transform to use public_id as the main id for frontend
    for business in businesses:
        if business.get('public_id'):
            business['id'] = str(business['public_id'])  # Use public_id as the main id
        else:
            logger.warning(f"⚠️ Business {business.get('name')} has no public_id!")
    
    return {"businesses": businesses}

@app.get("/api/businesses/{business_id}")
async def get_business(business_id: str, user_id: int = Depends(verify_jwt_token)):
    logger.info(f"🏢 Getting business {business_id} for user {user_id}")
    business = db.get_business_by_public_id(business_id, user_id)
    if business is None:
        logger.warning(f"❌ Business {business_id} not found for user {user_id}")
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Transform response to use public_id as the main id
    business['id'] = str(business['public_id'])
    
    logger.info(f"✅ Found business: {business['name']}")
    return {"business": business}

@app.put("/api/businesses/{business_id}")
async def update_business(business_id: str, business: BusinessCreate, user_id: int = Depends(verify_jwt_token)):
    # Verify business ownership
    existing_business = get_business_by_public_id_or_404(business_id, user_id)
    
    # Update business using internal ID
    success = db.update_business(existing_business['id'], business.name, business.website, business.description, business.buying_intent)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update business")
    
    return {"success": True}

@app.get("/api/businesses/{business_id}/ai-settings")
async def get_business_ai_settings(business_id: str, user_id: int = Depends(verify_jwt_token)):
    """Get AI reply settings for a business"""
    # Verify business ownership
    business = get_business_by_public_id_or_404(business_id, user_id)
    
    # Return default AI settings for now
    return {
        "ai_settings": {
            "persona": None,
            "instructions": None,
            "bad_words": [],
            "service_links": {},
            "tone": "professional",
            "max_reply_length": 500,
            "include_links": True,
            "auto_reply_enabled": False,
            "confidence_threshold": 80.0
        }
    }

@app.put("/api/businesses/{business_id}/ai-settings")
async def update_business_ai_settings(
    business_id: str,
    settings: dict,
    user_id: int = Depends(verify_jwt_token)
):
    """Update AI reply settings for a business"""
    # Verify business ownership
    business = get_business_by_public_id_or_404(business_id, user_id)
    
    # For now, just return success (implement actual storage later)
    return {"message": "AI settings updated successfully"}

# Website analysis
@app.post("/api/businesses/{business_id}/analyze-website")
async def analyze_website(business_id: str, data: WebsiteAnalyze, user_id: int = Depends(verify_jwt_token)):
    # Verify business ownership
    business = get_business_by_public_id_or_404(business_id, user_id)
    
    try:
        # Analyze website for keywords
        keywords = ai_analyzer.analyze_website_for_keywords(data.website_url, business['name'])
        
        return {
            "keywords": keywords
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# AI Auto-Setup endpoint
@app.post("/api/businesses/{business_id}/ai-auto-setup")
async def ai_auto_setup(business_id: str, data: dict, user_id: int = Depends(verify_jwt_token)):
    # Verify business ownership
    business = get_business_by_public_id_or_404(business_id, user_id)
    
    try:
        mode = data.get('mode', 'website')
        business_name = data.get('business_name', business['name'])
        
        if mode == 'website':
            website_url = data.get('website_url')
            if not website_url:
                raise HTTPException(status_code=400, detail="Website URL is required for website mode")
            
            # Perform comprehensive AI analysis with website
            setup_data = ai_analyzer.comprehensive_business_setup(
                website_url=website_url,
                business_name=business_name
            )
            
            # Update business with website URL
            if setup_data.get('business_info'):
                info = setup_data['business_info']
                new_name = info.get('name', business_name)
                logger.info(f"🏢 Updating business name from '{business_name}' to '{new_name}'")
                db.update_business(
                    business['id'], 
                    new_name,  # Use AI-generated name if available
                    website_url,
                    info.get('description'),
                    info.get('buying_intent')
                )
        
        elif mode == 'text':
            business_prompt = data.get('business_prompt')
            if not business_prompt:
                raise HTTPException(status_code=400, detail="Business prompt is required for text mode")
            
            # Perform AI analysis with text prompt only
            setup_data = ai_analyzer.text_based_business_setup(
                business_prompt=business_prompt,
                business_name=business_name
            )
            
            # Update business without changing website URL
            if setup_data.get('business_info'):
                info = setup_data['business_info']
                new_name = info.get('name', business_name)
                logger.info(f"🏢 Updating business name from '{business_name}' to '{new_name}'")
                db.update_business(
                    business['id'], 
                    new_name,  # Use AI-generated name if available
                    business.get('website'),  # Keep existing website
                    info.get('description'),
                    info.get('buying_intent')
                )
        
        else:
            raise HTTPException(status_code=400, detail="Invalid mode. Must be 'website' or 'text'")
        
        # Clear existing keywords and add AI-generated ones (max 10)
        if setup_data.get('keywords'):
            # Clear all existing keywords first
            db.clear_all_business_keywords(business['id'])
            
            # Add new keywords (limit to 10)
            keywords_to_add = setup_data['keywords'][:10]  # Limit to 10
            for keyword_data in keywords_to_add:
                db.add_business_keyword(
                    business['id'], 
                    keyword_data['keyword'], 
                    'ai_auto_setup'
                )
        
        # Debug logging
        logger.info(f"🔍 AI Setup Data: {setup_data}")
        if setup_data.get('business_info'):
            logger.info(f"📝 Business Name from AI: {setup_data['business_info'].get('name')}")
        
        return setup_data
        
    except Exception as e:
        logger.error(f"❌ AI Auto-Setup failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI Auto-Setup failed: {str(e)}")

# Keywords management
@app.post("/api/businesses/{business_id}/keywords")
async def add_keyword(business_id: str, keyword: KeywordAdd, user_id: int = Depends(verify_jwt_token)):
    # Verify business ownership
    business = get_business_by_public_id_or_404(business_id, user_id)
    
    db.add_business_keyword(business['id'], keyword.keyword, keyword.source)
    return {"success": True}

@app.get("/api/businesses/{business_id}/keywords")
async def get_keywords(business_id: str, user_id: int = Depends(verify_jwt_token)):
    # Verify business ownership
    business = get_business_by_public_id_or_404(business_id, user_id)
    
    keywords = db.get_business_keywords(business['id'])
    return {"keywords": keywords}

@app.delete("/api/businesses/{business_id}/keywords/{keyword_id}")
async def remove_keyword(business_id: str, keyword_id: int, user_id: int = Depends(verify_jwt_token)):
    # Verify business ownership
    business = get_business_by_public_id_or_404(business_id, user_id)
    
    db.delete_business_keyword(keyword_id, business['id'])
    return {"success": True}

@app.delete("/api/businesses/{business_id}/keywords")
async def clear_all_keywords(business_id: str, user_id: int = Depends(verify_jwt_token)):
    # Verify business ownership
    business = get_business_by_public_id_or_404(business_id, user_id)
    
    db.clear_all_business_keywords(business['id'])
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
            logger.info(f"🔍 Processing platform {platform} with count {count}, businesses type: {type(businesses)}")
            platform_stats[platform] = {
                'leads': count,
                'businesses': len(businesses)  # All businesses could potentially have this platform
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
            
            # Get counts for this specific business using PostgreSQL syntax
            logger.info(f"🔍 Executing business stats query for business_id: {business_id}")
            cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN DATE(processed_at) = CURRENT_DATE THEN 1 ELSE 0 END) as today,
                    SUM(CASE WHEN processed_at >= CURRENT_DATE - INTERVAL '7 days' THEN 1 ELSE 0 END) as week,
                    SUM(CASE WHEN ai_score >= 80 THEN 1 ELSE 0 END) as high_quality
                FROM business_leads 
                WHERE business_id = %s
            ''', (business_id,))
            logger.info(f"✅ Business stats query executed successfully")
            
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
        logger.info(f"🔍 Platform stats before formatting: {platform_stats}")
        
        try:
            for platform, stats in platform_stats.items():
                logger.info(f"🔍 Formatting platform {platform}, stats: {stats}, stats type: {type(stats)}")
                
                # Ensure we have the right data types
                leads_count = stats.get('leads', 0) if isinstance(stats, dict) else 0
                business_count = stats.get('businesses', 0) if isinstance(stats, dict) else 0
                
                formatted_platform_stats.append({
                    'platform': platform,
                    'leads': leads_count,
                    'businesses': business_count
                })
        except Exception as e:
            logger.error(f"❌ Error formatting platform stats: {e}")
            # Fallback to empty list
            formatted_platform_stats = []
        
        # Sort recent activity by processed_at (safely)
        try:
            if recent_activity and isinstance(recent_activity, list):
                recent_activity.sort(key=lambda x: x.get('processed_at', ''), reverse=True)
        except Exception as e:
            logger.error(f"❌ Error sorting recent activity: {e}")
            recent_activity = []
        
        # Ensure all data is properly formatted and safe
        result = {
            "metrics": {
                "totalLeads": int(total_leads or 0),
                "leadsToday": int(leads_today or 0),
                "leadsThisWeek": int(leads_this_week or 0),
                "highQualityLeads": int(high_quality_leads or 0)
            },
            "platformStats": formatted_platform_stats if formatted_platform_stats else [],
            "recentActivity": recent_activity[:10] if recent_activity else [],
            "businessStats": business_stats if business_stats else []
        }
        
        logger.info(f"✅ Dashboard data prepared successfully with {len(result['platformStats'])} platforms")
        return result
        
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to load dashboard data")

# Leads management
@app.get("/api/businesses/{business_id}/leads")
async def get_business_leads(business_id: str, limit: int = 50, user_id: int = Depends(verify_jwt_token)):
    # Verify business ownership
    business = get_business_by_public_id_or_404(business_id, user_id)
    
    leads = db.get_business_leads(business['id'], limit)
    return {"leads": leads, "total": len(leads)}

if __name__ == "__main__":
    # Development server - use uvicorn directly
    import uvicorn
    import time
    
    print("🚀 Starting Lead Finder API v2 (Development)...")
    
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
    print(f"🌐 Starting development server on 0.0.0.0:{port}")
    print("⚠️  For production, use: python3 start_production.py")
    
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)