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
from notification_service import notification_service

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Reddit Lead Finder API v2")
security = HTTPBearer()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3050", "http://localhost:5173"],
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

class SocialAccountCreate(BaseModel):
    platform: str
    username: str
    password: str
    notes: Optional[str] = None

class SocialAccountUpdate(BaseModel):
    is_active: bool

class NotificationPreferenceUpdate(BaseModel):
    notification_type: str
    email_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None

class BusinessAISettings(BaseModel):
    persona: Optional[str] = None
    instructions: Optional[str] = None
    bad_words: Optional[List[str]] = None
    service_links: Optional[dict] = None
    tone: Optional[str] = None
    max_reply_length: Optional[int] = None
    include_links: Optional[bool] = None
    auto_reply_enabled: Optional[bool] = None
    confidence_threshold: Optional[float] = None

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
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

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

@app.get("/api/businesses/{business_id}/ai-settings")
async def get_business_ai_settings(business_id: int, user_id: int = Depends(verify_jwt_token)):
    """Get AI reply settings for a business"""
    # Verify business ownership
    business = db.get_business(business_id, user_id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    settings = db.get_business_ai_settings(business_id)
    return {"ai_settings": settings}

@app.put("/api/businesses/{business_id}/ai-settings")
async def update_business_ai_settings(
    business_id: int,
    settings: BusinessAISettings,
    user_id: int = Depends(verify_jwt_token)
):
    """Update AI reply settings for a business"""
    # Verify business ownership
    business = db.get_business(business_id, user_id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Convert to dict and filter None values
    settings_dict = {k: v for k, v in settings.model_dump().items() if v is not None}
    
    success = db.update_business_ai_settings(business_id, settings_dict)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update AI settings")
    
    return {"message": "AI settings updated successfully"}

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
        
        # Calculate metrics using simple JOIN query
        conn = db.get_connection()
        cursor = conn.cursor()
        
        logger.info(f"Calculating metrics for user {user_id} with {len(businesses)} businesses")
        
        # Get lead metrics
        cursor.execute('''
            SELECT 
                COUNT(*) as total_leads,
                COUNT(CASE WHEN DATE(bl.processed_at) = CURRENT_DATE THEN 1 END) as leads_today,
                COUNT(CASE WHEN bl.processed_at >= CURRENT_DATE - INTERVAL '7 days' THEN 1 END) as leads_this_week,
                COUNT(CASE WHEN bl.ai_score >= 80 THEN 1 END) as high_quality_leads
            FROM business_leads bl
            JOIN businesses b ON bl.business_id = b.id
            WHERE b.user_id = %s
        ''', (user_id,))
        
        result = cursor.fetchone()
        total_leads = result[0] or 0
        leads_today = result[1] or 0
        leads_this_week = result[2] or 0
        high_quality_leads = result[3] or 0
        
        # Get reply metrics
        cursor.execute('''
            SELECT 
                COUNT(CASE WHEN r.status = 'submitted' THEN 1 END) as total_replies_posted,
                COUNT(CASE WHEN DATE(r.submitted_at) = CURRENT_DATE AND r.status = 'submitted' THEN 1 END) as replies_today,
                COUNT(CASE WHEN r.submitted_at >= CURRENT_DATE - INTERVAL '7 days' AND r.status = 'submitted' THEN 1 END) as replies_this_week
            FROM replies r
            JOIN business_leads bl ON r.business_lead_id = bl.id
            JOIN businesses b ON bl.business_id = b.id
            WHERE b.user_id = %s
        ''', (user_id,))
        
        reply_result = cursor.fetchone()
        total_replies_posted = reply_result[0] or 0
        replies_today = reply_result[1] or 0
        replies_this_week = reply_result[2] or 0
        
        logger.info(f"Dashboard metrics - Leads: {total_leads}, Replies Posted: {total_replies_posted}, Today: {leads_today}, Week: {leads_this_week}, High Quality: {high_quality_leads}")
        
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
            JOIN businesses b ON bl.business_id = b.id
            WHERE b.user_id = %s
            GROUP BY gl.platform
        ''', (user_id,))
        platform_results = cursor.fetchall()
        
        for platform, count in platform_results:
            platform_stats[platform] = {
                'leads': count,
                'businesses': len(businesses)
            }
        
        # Get recent activity (last 10 leads)
        cursor.execute('''
            SELECT bl.id, b.name as business_name, gl.title, gl.platform, bl.ai_score, bl.processed_at
            FROM business_leads bl
            JOIN businesses b ON bl.business_id = b.id
            JOIN global_leads gl ON bl.global_lead_id = gl.id
            WHERE b.user_id = %s
            ORDER BY bl.processed_at DESC
            LIMIT 10
        ''', (user_id,))
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
        cursor.execute('''
            SELECT 
                b.id,
                b.name,
                COUNT(bl.id) as total,
                COUNT(CASE WHEN DATE(bl.processed_at) = CURRENT_DATE THEN 1 END) as today,
                COUNT(CASE WHEN bl.processed_at >= CURRENT_DATE - INTERVAL '7 days' THEN 1 END) as week,
                COUNT(CASE WHEN bl.ai_score >= 80 THEN 1 END) as high_quality
            FROM businesses b
            LEFT JOIN business_leads bl ON b.id = bl.business_id
            WHERE b.user_id = %s
            GROUP BY b.id, b.name
            ORDER BY b.name
        ''', (user_id,))
        
        business_results = cursor.fetchall()
        for row in business_results:
            business_stats.append({
                'id': row[0],
                'name': row[1],
                'totalLeads': row[2] or 0,
                'leadsToday': row[3] or 0,
                'leadsThisWeek': row[4] or 0,
                'highQualityLeads': row[5] or 0
            })
        
        conn.close()
        
        # Format platform stats
        formatted_platform_stats = []
        for platform, stats in platform_stats.items():
            formatted_platform_stats.append({
                'platform': platform,
                'leads': stats['leads'],
                'businesses': stats['businesses']
            })
        
        # Sort recent activity by processed_at
        recent_activity.sort(key=lambda x: x['processed_at'], reverse=True)
        
        return {
            "metrics": {
                "totalLeads": total_leads,
                "leadsToday": leads_today,
                "leadsThisWeek": leads_this_week,
                "highQualityLeads": high_quality_leads,
                "totalRepliesPosted": total_replies_posted,
                "repliesToday": replies_today,
                "repliesThisWeek": replies_this_week
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

# Reply management endpoints
@app.post("/api/replies")
async def create_reply(
    business_lead_id: int, 
    reply_content: str, 
    user_id: int = Depends(verify_jwt_token)
):
    """Create a new AI reply for a business lead."""
    try:
        # Verify the business lead belongs to the user
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT bl.id FROM business_leads bl
            JOIN businesses b ON bl.business_id = b.id
            WHERE bl.id = %s AND b.user_id = %s
        ''', (business_lead_id, user_id))
        
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Business lead not found")
        
        cursor.close()
        conn.close()
        
        # Create the reply
        reply_id = db.add_reply(business_lead_id, user_id, reply_content)
        
        if reply_id:
            return {"reply_id": reply_id, "status": "created"}
        else:
            raise HTTPException(status_code=400, detail="Reply already exists for this lead")
            
    except Exception as e:
        logger.error(f"Create reply error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create reply")

@app.put("/api/replies/{reply_id}/status")
async def update_reply_status(
    reply_id: int,
    status: str,
    platform_reply_id: str = None,
    user_id: int = Depends(verify_jwt_token)
):
    """Update reply status (pending -> submitted -> posted)."""
    try:
        # Verify the reply belongs to the user
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT r.id FROM replies r
            JOIN business_leads bl ON r.business_lead_id = bl.id
            JOIN businesses b ON bl.business_id = b.id
            WHERE r.id = %s AND b.user_id = %s
        ''', (reply_id, user_id))
        
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Reply not found")
        
        cursor.close()
        conn.close()
        
        # Update the reply status
        success = db.update_reply_status(reply_id, status, platform_reply_id)
        
        if success:
            return {"success": True, "status": status}
        else:
            raise HTTPException(status_code=400, detail="Failed to update reply status")
            
    except Exception as e:
        logger.error(f"Update reply status error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update reply status")

@app.get("/api/replies")
async def get_user_replies(
    status: str = None,
    limit: int = 50,
    user_id: int = Depends(verify_jwt_token)
):
    """Get replies for the current user."""
    try:
        replies = db.get_user_replies(user_id, status, limit)
        return {"replies": replies}
        
    except Exception as e:
        logger.error(f"Get replies error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get replies")

# Platform settings endpoints
@app.get("/api/platforms/settings")
async def get_platform_settings(user_id: int = Depends(verify_jwt_token)):
    """Get all platform settings for the current user."""
    try:
        settings = db.get_user_platform_settings(user_id)
        return {"settings": settings}
        
    except Exception as e:
        logger.error(f"Get platform settings error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get platform settings")

@app.get("/api/platforms/{platform_id}/settings")
async def get_platform_setting(
    platform_id: str,
    user_id: int = Depends(verify_jwt_token)
):
    """Get specific platform setting for the current user."""
    try:
        setting = db.get_platform_setting(user_id, platform_id)
        if not setting:
            # Return default settings if none exist
            return {
                "platform_id": platform_id,
                "is_active": platform_id == "reddit",  # Reddit active by default
                "auto_reply": False,
                "confidence_threshold": 80,
                "write_reply_suggestion": False
            }
        return setting
        
    except Exception as e:
        logger.error(f"Get platform setting error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get platform setting")

@app.put("/api/platforms/{platform_id}/settings")
async def update_platform_setting(
    platform_id: str,
    settings: dict,
    user_id: int = Depends(verify_jwt_token)
):
    """Update platform settings for the current user."""
    try:
        # Validate platform_id
        valid_platforms = ['reddit', 'twitter', 'linkedin']
        if platform_id not in valid_platforms:
            raise HTTPException(status_code=400, detail="Invalid platform ID")
        
        # Extract settings from request
        is_active = settings.get('isActive')
        auto_reply = settings.get('autoReply')
        confidence_threshold = settings.get('confidenceThreshold')
        write_reply_suggestion = settings.get('writeReplySuggestion')
        
        # Validate confidence threshold
        if confidence_threshold is not None:
            if not isinstance(confidence_threshold, int) or confidence_threshold < 50 or confidence_threshold > 100:
                raise HTTPException(status_code=400, detail="Confidence threshold must be between 50 and 100")
        
        # Update settings
        success = db.update_platform_setting(
            user_id=user_id,
            platform_id=platform_id,
            is_active=is_active,
            auto_reply=auto_reply,
            confidence_threshold=confidence_threshold,
            write_reply_suggestion=write_reply_suggestion
        )
        
        if success:
            return {"success": True, "message": "Platform settings updated successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to update platform settings")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update platform setting error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update platform settings")

# Social Accounts endpoints
@app.get("/api/accounts")
async def get_social_accounts(user_id: int = Depends(verify_jwt_token)):
    """Get all social accounts for the authenticated user"""
    accounts = db.get_user_social_accounts(user_id)
    return {"accounts": accounts}

@app.post("/api/accounts")
async def create_social_account(
    account: SocialAccountCreate,
    user_id: int = Depends(verify_jwt_token)
):
    """Create a new social media account"""
    account_id = db.add_social_account(
        user_id=user_id,
        platform=account.platform,
        username=account.username,
        password=account.password,
        notes=account.notes
    )
    
    if account_id is None:
        raise HTTPException(
            status_code=400,
            detail="Account with this username already exists for this platform"
        )
    
    return {"message": "Account created successfully", "account_id": account_id}

@app.put("/api/accounts/{account_id}/status")
async def update_account_status(
    account_id: int,
    update: SocialAccountUpdate,
    user_id: int = Depends(verify_jwt_token)
):
    """Update the active status of a social account"""
    success = db.update_social_account_status(account_id, user_id, update.is_active)
    
    if not success:
        raise HTTPException(status_code=404, detail="Account not found")
    
    return {"message": "Account status updated successfully"}

@app.delete("/api/accounts/{account_id}")
async def delete_social_account(
    account_id: int,
    user_id: int = Depends(verify_jwt_token)
):
    """Delete a social media account"""
    success = db.delete_social_account(account_id, user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Account not found")
    
    return {"message": "Account deleted successfully"}

@app.post("/api/accounts/upload-csv")
async def upload_accounts_csv(
    file: bytes,
    user_id: int = Depends(verify_jwt_token)
):
    """Upload accounts from CSV file"""
    import csv
    import io
    
    try:
        # Parse CSV content
        csv_content = file.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        
        added_accounts = []
        errors = []
        
        for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 because row 1 is header
            try:
                # Validate required fields
                platform = row.get('platform', '').strip().lower()
                username = row.get('username', '').strip()
                password = row.get('password', '').strip()
                notes = row.get('notes', '').strip()
                
                if not platform or not username or not password:
                    errors.append(f"Row {row_num}: Missing required fields (platform, username, password)")
                    continue
                
                # Validate platform
                if platform not in ['reddit', 'twitter', 'linkedin']:
                    errors.append(f"Row {row_num}: Invalid platform '{platform}'. Must be reddit, twitter, or linkedin")
                    continue
                
                # Add account
                account_id = db.add_social_account(
                    user_id=user_id,
                    platform=platform,
                    username=username,
                    password=password,
                    notes=notes if notes else None
                )
                
                if account_id:
                    added_accounts.append({
                        'platform': platform,
                        'username': username,
                        'account_id': account_id
                    })
                else:
                    errors.append(f"Row {row_num}: Account @{username} on {platform} already exists")
                    
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
        
        return {
            "message": f"Successfully added {len(added_accounts)} accounts",
            "added_accounts": added_accounts,
            "errors": errors,
            "total_processed": len(added_accounts) + len(errors)
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process CSV: {str(e)}")

# Notifications endpoints
@app.get("/api/notifications")
async def get_notifications(
    limit: int = 50,
    unread_only: bool = False,
    user_id: int = Depends(verify_jwt_token)
):
    """Get notifications for the authenticated user"""
    notifications = db.get_user_notifications(user_id, limit, unread_only)
    unread_count = db.get_unread_notification_count(user_id)
    
    return {
        "notifications": notifications,
        "unread_count": unread_count,
        "total_count": len(notifications)
    }

@app.put("/api/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    user_id: int = Depends(verify_jwt_token)
):
    """Mark a notification as read"""
    success = db.mark_notification_read(notification_id, user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {"message": "Notification marked as read"}

@app.put("/api/notifications/mark-all-read")
async def mark_all_notifications_read(user_id: int = Depends(verify_jwt_token)):
    """Mark all notifications as read"""
    count = db.mark_all_notifications_read(user_id)
    
    return {"message": f"Marked {count} notifications as read", "count": count}

@app.delete("/api/notifications/{notification_id}")
async def delete_notification(
    notification_id: int,
    user_id: int = Depends(verify_jwt_token)
):
    """Delete a notification"""
    success = db.delete_notification(notification_id, user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {"message": "Notification deleted"}

@app.get("/api/notifications/preferences")
async def get_notification_preferences(user_id: int = Depends(verify_jwt_token)):
    """Get notification preferences for the user"""
    preferences = db.get_user_notification_preferences(user_id)
    
    return {"preferences": preferences}

@app.put("/api/notifications/preferences")
async def update_notification_preferences(
    preference: NotificationPreferenceUpdate,
    user_id: int = Depends(verify_jwt_token)
):
    """Update notification preferences"""
    success = db.update_notification_preference(
        user_id, 
        preference.notification_type,
        preference.email_enabled,
        preference.push_enabled
    )
    
    return {"message": "Notification preferences updated"}

# Replies endpoints
@app.get("/api/replies")
async def get_replies(
    status: Optional[str] = None,
    limit: int = 50,
    user_id: int = Depends(verify_jwt_token)
):
    """Get replies for the authenticated user"""
    replies = db.get_user_replies(user_id, status, limit)
    
    # Get stats
    stats = db.get_reply_stats(user_id)
    
    return {
        "replies": replies,
        "total": len(replies),
        "stats": stats
    }

@app.put("/api/replies/{reply_id}")
async def update_reply(
    reply_id: int,
    reply_content: str,
    user_id: int = Depends(verify_jwt_token)
):
    """Update a reply's content"""
    # Verify reply ownership through business ownership
    reply = db.get_reply_by_id(reply_id, user_id)
    if not reply:
        raise HTTPException(status_code=404, detail="Reply not found")
    
    success = db.update_reply_content(reply_id, reply_content)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update reply")
    
    return {"message": "Reply updated successfully"}

@app.delete("/api/replies/{reply_id}")
async def delete_reply(
    reply_id: int,
    user_id: int = Depends(verify_jwt_token)
):
    """Delete a reply"""
    # Verify reply ownership through business ownership
    reply = db.get_reply_by_id(reply_id, user_id)
    if not reply:
        raise HTTPException(status_code=404, detail="Reply not found")
    
    success = db.delete_reply(reply_id, user_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete reply")
    
    return {"message": "Reply deleted successfully"}

@app.post("/api/replies/{reply_id}/post")
async def post_reply(
    reply_id: int,
    user_id: int = Depends(verify_jwt_token)
):
    """Post a reply to the platform"""
    # Verify reply ownership
    reply = db.get_reply_by_id(reply_id, user_id)
    if not reply:
        raise HTTPException(status_code=404, detail="Reply not found")
    
    if reply['status'] != 'draft':
        raise HTTPException(status_code=400, detail="Only draft replies can be posted")
    
    # Update status to pending
    db.update_reply_status(reply_id, 'pending')
    
    # TODO: Implement actual posting to platform
    # For now, we'll simulate posting
    import time
    time.sleep(1)  # Simulate API call
    
    # Update to posted status with fake platform ID
    platform_reply_id = f"fake_reply_{reply_id}_{int(time.time())}"
    db.update_reply_status(reply_id, 'posted', platform_reply_id)
    
    return {"message": "Reply posted successfully", "platform_reply_id": platform_reply_id}

@app.get("/api/platforms")
async def get_available_platforms():
    """Get list of available platforms and their status."""
    platforms = [
        {
            "id": "reddit",
            "name": "Reddit",
            "description": "Track leads from Reddit posts and comments",
            "isAvailable": True,
            "icon": "reddit"
        },
        {
            "id": "twitter", 
            "name": "Twitter/X",
            "description": "Track leads from Twitter posts and mentions",
            "isAvailable": False,
            "icon": "twitter"
        },
        {
            "id": "linkedin",
            "name": "LinkedIn", 
            "description": "Track leads from LinkedIn posts and comments",
            "isAvailable": False,
            "icon": "linkedin"
        }
    ]
    
    return {"platforms": platforms}

@app.get("/api/scraper/status")
async def get_scraper_status(user_id: int = Depends(verify_jwt_token)):
    """Get the current status of the scraper service"""
    try:
        # Check last scrape activity from database
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT MAX(scraped_at) as last_scrape 
            FROM global_leads 
            WHERE scraped_at > %s
        ''', (datetime.now() - timedelta(hours=3),))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        last_scrape = result[0] if result and result[0] else None
        recent_activity = last_scrape and (datetime.now() - last_scrape).total_seconds() < 10800  # 3 hours
        
        # Simple check - if we have recent scraping activity, consider it active
        is_active = recent_activity
        
        return {
            "is_active": is_active,
            "last_scrape": last_scrape.isoformat() if last_scrape else None,
            "recent_activity": recent_activity,
            "status_message": "Scraper is active" if is_active else "Scraper offline"
        }
        
    except Exception as e:
        logger.error(f"Error checking scraper status: {e}")
        return {
            "is_active": False,
            "last_scrape": None,
            "recent_activity": False,
            "status_message": "Scraper offline"
        }

if __name__ == "__main__":
    import uvicorn
    import time
    
    print("🚀 Starting Reddit Lead Finder API v2...")
    
    # Wait for database to be ready
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            logger.info(f"Attempting database connection (attempt {retry_count + 1}/{max_retries})")
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            conn.close()
            logger.info("✅ Database connection successful!")
            break
        except Exception as e:
            logger.warning(f"⚠️ Database connection failed: {e}")
            retry_count += 1
            if retry_count < max_retries:
                logger.info(f"🔄 Retrying in 2 seconds...")
                time.sleep(2)
            else:
                logger.error("❌ Max database connection retries exceeded. Starting server anyway...")
                break
    
    port = int(os.getenv("BACKEND_PORT", 8001))
    logger.info(f"🌐 Starting API server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)