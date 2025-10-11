#!/usr/bin/env python3
"""
Test the database fix with a small scrape
"""

from reddit_scraper_final import RedditLeadScraper
from ai_analyzer import AILeadAnalyzer
from database import Database

def test_db_fix():
    """Test database saving with fixed raw_data handling"""
    print("🧪 Testing database fix...")
    
    # Initialize components
    db = Database()
    scraper = RedditLeadScraper()
    ai_analyzer = AILeadAnalyzer()
    
    # Get a small sample
    print("📡 Scraping small sample...")
    leads = scraper.search_leads(
        keywords=["help", "tool"],
        subreddits=["entrepreneur"],
        days_back=1
    )
    
    if not leads:
        print("❌ No leads found")
        return
    
    print(f"✅ Found {len(leads)} leads")
    
    # Test AI analysis on first lead
    print("🤖 Testing AI analysis...")
    first_lead = leads[0]
    analysis = ai_analyzer.analyze_lead(first_lead)
    first_lead['ai_probability'] = analysis['probability']
    first_lead['ai_analysis'] = analysis['analysis']
    
    print(f"✅ AI analysis: {analysis['probability']}%")
    
    # Test database save
    print("💾 Testing database save...")
    success = db.save_lead(first_lead)
    
    if success:
        print("✅ Database save successful!")
        
        # Test retrieval
        saved_leads = db.get_leads(limit=1, min_probability=0)
        if saved_leads:
            print(f"✅ Retrieved lead: {saved_leads[0].get('title', '')[:50]}...")
            return True
    else:
        print("❌ Database save failed")
        return False

if __name__ == "__main__":
    test_db_fix()