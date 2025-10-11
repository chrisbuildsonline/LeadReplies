#!/usr/bin/env python3
"""
FastAPI server to bridge Reddit Lead Finder with the frontend.
Provides REST API endpoints for the React frontend to consume.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import uvicorn
from database import Database
from reddit_scraper_final import RedditLeadScraper
from ai_analyzer import AILeadAnalyzer
import asyncio
import threading
import time

app = FastAPI(title="Reddit Lead Finder API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3050", "http://localhost:3000", "http://localhost:5173", "http://localhost:6070"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
db = Database()
scraper = RedditLeadScraper()
ai_analyzer = AILeadAnalyzer()

# Background scraping state
scraping_active = False
last_scrape_time = None

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Reddit Lead Finder API", "status": "running"}

@app.get("/api/dashboard")
async def get_dashboard():
    """Get dashboard data compatible with frontend"""
    try:
        # Get leads data
        all_leads = db.get_leads(limit=1000, min_probability=0)
        high_quality_leads = [l for l in all_leads if l.get('ai_probability', 0) >= 70]
        
        # Calculate metrics
        total_replies = len(all_leads)
        products_promoted = len(set(l.get('subreddit', '') for l in all_leads))
        avg_probability = sum(l.get('ai_probability', 0) for l in all_leads) / len(all_leads) if all_leads else 0
        
        # Get recent leads for activity feed
        recent_leads = db.get_leads(limit=10, min_probability=40)
        
        # Convert leads to replies format for frontend
        replies = []
        for lead in recent_leads[:4]:
            replies.append({
                "id": lead.get('id', ''),
                "platform": "reddit",
                "content": lead.get('ai_analysis', '')[:100] + "..." if lead.get('ai_analysis') else lead.get('content', '')[:100] + "...",
                "originalPost": lead.get('title', ''),
                "username": f"r/{lead.get('subreddit', '')}",
                "upvotes": lead.get('upvotes', 0),
                "campaignId": None,
                "createdAt": lead.get('processed_at', datetime.now()).isoformat() if isinstance(lead.get('processed_at'), datetime) else datetime.now().isoformat()
            })
        
        # Mock accounts data (since we don't have account purchasing in our system)
        accounts = [
            {
                "id": "1",
                "platform": "reddit",
                "username": "",
                "price": 5.0,
                "age": "1yr old",
                "stats": "500+ karma",
                "description": "active history",
                "available": True
            },
            {
                "id": "2", 
                "platform": "reddit",
                "username": "",
                "price": 8.0,
                "age": "2yr old", 
                "stats": "1000+ karma",
                "description": "verified email",
                "available": True
            }
        ]
        
        # Get active keywords and subreddits
        keywords = db.get_active_keywords()
        subreddits = db.get_active_subreddits()
        
        return {
            "metrics": {
                "id": "1",
                "totalReplies": total_replies,
                "productsPromoted": products_promoted,
                "clickThroughRate": round(avg_probability / 10, 1),  # Convert to CTR-like metric
                "engagementRate": round(avg_probability, 1),
                "updatedAt": datetime.now().isoformat()
            },
            "platformStats": [
                {
                    "id": "reddit",
                    "platform": "reddit",
                    "repliesPosted": total_replies,
                    "accountsConnected": 2,
                    "isActive": True,
                    "updatedAt": datetime.now().isoformat()
                }
            ],
            "campaigns": [
                {
                    "id": "reddit-leads",
                    "name": "Reddit Lead Generation",
                    "keywords": keywords[:10],  # Show first 10 keywords
                    "platforms": ["reddit"],
                    "status": "active" if scraping_active else "paused",
                    "productUrl": "https://your-product.com",
                    "description": f"Monitoring {len(subreddits)} subreddits for {len(keywords)} keywords",
                    "createdAt": datetime.now().isoformat()
                }
            ],
            "replies": replies,
            "accounts": accounts,
            "dailyStats": {
                "id": "today",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "repliesPosted": len([l for l in all_leads if l.get('processed_at') and 
                                   isinstance(l.get('processed_at'), datetime) and 
                                   l.get('processed_at').date() == datetime.now().date()]),
                "clicksGenerated": len(high_quality_leads),
                "engagementRate": round(avg_probability, 1),
                "keywordsTracked": len(keywords)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch dashboard data: {str(e)}")

@app.get("/api/leads")
async def get_leads(limit: int = 50, min_probability: int = 0):
    """Get leads with filtering"""
    try:
        leads = db.get_leads(limit=limit, min_probability=min_probability)
        
        # Convert to frontend-friendly format
        formatted_leads = []
        for lead in leads:
            formatted_leads.append({
                "id": lead.get('id', ''),
                "reddit_id": lead.get('reddit_id', ''),
                "title": lead.get('title', ''),
                "content": lead.get('content', ''),
                "url": lead.get('url', ''),
                "author": lead.get('author', ''),
                "subreddit": lead.get('subreddit', ''),
                "ai_probability": lead.get('ai_probability', 0),
                "ai_analysis": lead.get('ai_analysis', ''),
                "keywords_matched": lead.get('keywords_matched', []),
                "upvotes": lead.get('upvotes', 0),
                "created_date": lead.get('created_date', ''),
                "processed_at": lead.get('processed_at', '')
            })
        
        return {"leads": formatted_leads, "total": len(formatted_leads)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch leads: {str(e)}")

@app.get("/api/leads/high-quality")
async def get_high_quality_leads():
    """Get high quality leads (70%+)"""
    return await get_leads(limit=100, min_probability=70)

@app.get("/api/scraping/status")
async def get_scraping_status():
    """Get current scraping status"""
    return {
        "active": scraping_active,
        "last_scrape": last_scrape_time.isoformat() if last_scrape_time else None,
        "total_leads": len(db.get_leads(limit=10000, min_probability=0))
    }

@app.post("/api/scraping/start")
async def start_scraping():
    """Start background scraping"""
    global scraping_active
    
    if scraping_active:
        return {"message": "Scraping already active"}
    
    scraping_active = True
    
    # Start background scraping in a separate thread
    def background_scrape():
        global last_scrape_time
        while scraping_active:
            try:
                print("🔄 Running background scrape...")
                
                # Get keywords and subreddits
                keywords = db.get_active_keywords()
                subreddits = db.get_active_subreddits()
                
                if keywords and subreddits:
                    # Scrape Reddit
                    leads = scraper.search_leads(keywords, subreddits, days_back=1)
                    
                    if leads:
                        # AI Analysis
                        analyzed_leads = ai_analyzer.analyze_batch(leads)
                        
                        # Save to database
                        saved_count = 0
                        for lead in analyzed_leads:
                            if db.save_lead(lead):
                                saved_count += 1
                        
                        print(f"✅ Background scrape complete: {saved_count} leads saved")
                    
                last_scrape_time = datetime.now()
                
                # Wait 1 hour before next scrape
                time.sleep(3600)
                
            except Exception as e:
                print(f"❌ Background scrape error: {e}")
                time.sleep(300)  # Wait 5 minutes on error
    
    thread = threading.Thread(target=background_scrape, daemon=True)
    thread.start()
    
    return {"message": "Background scraping started"}

@app.post("/api/scraping/stop")
async def stop_scraping():
    """Stop background scraping"""
    global scraping_active
    scraping_active = False
    return {"message": "Background scraping stopped"}

@app.post("/api/scraping/run-once")
async def run_scraping_once():
    """Run scraping once immediately"""
    try:
        # Get keywords and subreddits
        keywords = db.get_active_keywords()
        subreddits = db.get_active_subreddits()
        
        if not keywords or not subreddits:
            raise HTTPException(status_code=400, detail="No keywords or subreddits configured")
        
        # Scrape Reddit
        leads = scraper.search_leads(keywords, subreddits, days_back=1)
        
        if not leads:
            return {"message": "No leads found", "leads_processed": 0}
        
        # AI Analysis
        analyzed_leads = ai_analyzer.analyze_batch(leads)
        
        # Save to database
        saved_count = 0
        for lead in analyzed_leads:
            if db.save_lead(lead):
                saved_count += 1
        
        global last_scrape_time
        last_scrape_time = datetime.now()
        
        return {
            "message": "Scraping completed successfully",
            "leads_found": len(leads),
            "leads_processed": len(analyzed_leads),
            "leads_saved": saved_count,
            "high_quality_leads": len([l for l in analyzed_leads if l.get('ai_probability', 0) >= 70])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

@app.get("/api/keywords")
async def get_keywords():
    """Get active keywords"""
    try:
        keywords = db.get_active_keywords()
        return {"keywords": keywords}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch keywords: {str(e)}")

@app.get("/api/subreddits")
async def get_subreddits():
    """Get active subreddits"""
    try:
        subreddits = db.get_active_subreddits()
        return {"subreddits": subreddits}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch subreddits: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting Reddit Lead Finder API Server...")
    print("📊 Dashboard: http://localhost:6070")
    print("📋 API Docs: http://localhost:6070/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=6070)