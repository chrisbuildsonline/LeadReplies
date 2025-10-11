#!/usr/bin/env python3
"""
Test the final Reddit scraper with RSS fallback.
"""

from reddit_scraper_final import RedditLeadScraper

def test_final_scraper():
    """Test the production-ready scraper"""
    print("🧪 Testing Final Reddit Scraper (RSS + JSON)")
    print("=" * 50)
    
    # Test with a small set
    test_keywords = ["SaaS", "marketing", "CRM", "help", "tool"]
    test_subreddits = ["entrepreneur", "startups"]  # Smaller set for testing
    
    print(f"Keywords: {', '.join(test_keywords)}")
    print(f"Subreddits: {', '.join([f'r/{s}' for s in test_subreddits])}")
    print(f"Days back: 2")
    print()
    
    scraper = RedditLeadScraper()
    
    try:
        leads = scraper.search_leads(test_keywords, test_subreddits, days_back=2)
        
        print(f"\n✅ Scraping completed!")
        print(f"📊 Found {len(leads)} leads")
        
        if leads:
            print(f"\n🏆 Sample leads:")
            for i, lead in enumerate(leads[:3], 1):
                print(f"{i}. [{lead.get('hotness_score', 0)}] {lead.get('title', '')[:60]}...")
                print(f"   r/{lead.get('subreddit', '')} | Keywords: {', '.join(lead.get('keywords_matched', []))}")
                print(f"   URL: {lead.get('url', '')}")
                print()
            
            return True
        else:
            print("ℹ️  No leads found. This could be normal for a small test.")
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_final_scraper()
    
    if success:
        print("🎉 Scraper is working! You can now:")
        print("   1. python3 setup_database.py  # Setup database")
        print("   2. python3 scheduler.py once   # Test full pipeline")
        print("   3. python3 scheduler.py        # Start monitoring")
    else:
        print("⚠️  Scraper test failed. Check your internet connection and try again.")