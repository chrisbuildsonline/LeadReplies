#!/usr/bin/env python3
"""
Test script for the new efficient Reddit scraper.
Tests the single-query approach that avoids rate limiting.
"""

from reddit_scraper_v2 import EfficientRedditScraper

def test_scraper():
    """Test the new scraper with a small set of keywords and subreddits"""
    print("🧪 Testing Efficient Reddit Scraper")
    print("=" * 40)
    
    # Test with a small set
    test_keywords = ["SaaS", "marketing tool", "CRM", "automation"]
    test_subreddits = ["entrepreneur", "startups", "marketing"]
    
    print(f"Keywords: {', '.join(test_keywords)}")
    print(f"Subreddits: {', '.join([f'r/{s}' for s in test_subreddits])}")
    print(f"Days back: 3")
    print()
    
    scraper = EfficientRedditScraper()
    
    try:
        # Test the single-query approach
        leads = scraper.search_leads(test_keywords, test_subreddits, days_back=3)
        
        print(f"\n✅ Scraping completed!")
        print(f"📊 Found {len(leads)} leads")
        
        if leads:
            print(f"\n🏆 Top 5 leads:")
            for i, lead in enumerate(leads[:5], 1):
                print(f"{i}. [{lead.get('hotness_score', 0)}] {lead.get('title', '')[:60]}...")
                print(f"   r/{lead.get('subreddit', '')} | {lead.get('upvotes', 0)} upvotes | Keywords: {', '.join(lead.get('keywords_matched', []))}")
                print()
        else:
            print("ℹ️  No leads found. This could be normal if:")
            print("   - No recent posts match the keywords")
            print("   - Rate limiting occurred")
            print("   - Subreddits are private/restricted")
        
        return len(leads) > 0
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

def test_batch_method():
    """Test the batch keyword method"""
    print("\n🧪 Testing Batch Keyword Method")
    print("=" * 40)
    
    test_keywords = ["SaaS", "marketing tool", "CRM", "automation", "lead generation", "email marketing"]
    test_subreddits = ["entrepreneur", "startups"]
    
    scraper = EfficientRedditScraper()
    
    try:
        leads = scraper.search_by_keyword_batch(test_keywords, test_subreddits, days_back=3)
        
        print(f"\n✅ Batch scraping completed!")
        print(f"📊 Found {len(leads)} leads")
        
        if leads:
            print(f"\n🏆 Top 3 leads:")
            for i, lead in enumerate(leads[:3], 1):
                print(f"{i}. [{lead.get('hotness_score', 0)}] {lead.get('title', '')[:50]}...")
                print(f"   r/{lead.get('subreddit', '')} | Keywords: {', '.join(lead.get('keywords_matched', []))}")
        
        return len(leads) > 0
        
    except Exception as e:
        print(f"❌ Batch test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Reddit Scraper V2 - Test Suite")
    print("=" * 50)
    
    # Test 1: Regular method
    success1 = test_scraper()
    
    # Test 2: Batch method
    success2 = test_batch_method()
    
    print(f"\n📋 Test Results:")
    print(f"   Regular method: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"   Batch method: {'✅ PASS' if success2 else '❌ FAIL'}")
    
    if success1 or success2:
        print(f"\n🎉 At least one method works! You can proceed with:")
        print(f"   python setup_database.py  # Setup database")
        print(f"   python scheduler.py once   # Test full pipeline")
    else:
        print(f"\n⚠️  Both methods failed. This might be due to:")
        print(f"   - Reddit rate limiting (try again later)")
        print(f"   - Network issues")
        print(f"   - No recent posts matching keywords")