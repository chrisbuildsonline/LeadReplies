#!/usr/bin/env python3
"""
Test script to verify PostgreSQL migration is working correctly
"""

import sys
import os

# Add server directory to path
sys.path.append('./server')

def test_database_connection():
    """Test PostgreSQL database connection"""
    print("🔍 Testing PostgreSQL connection...")
    
    try:
        from database import Database
        db = Database()
        print("✅ PostgreSQL connection successful!")
        return True
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {str(e)}")
        return False

def test_dashboard_api():
    """Test dashboard API with PostgreSQL"""
    print("🔍 Testing dashboard API...")
    
    try:
        from database import Database
        db = Database()
        
        # Test getting businesses
        businesses = db.get_user_businesses(1)  # Assuming user 1 exists
        print(f"✅ Found {len(businesses)} businesses")
        
        if businesses:
            # Test getting leads
            business_id = businesses[0]['id']
            leads = db.get_business_leads(business_id, limit=5)
            print(f"✅ Found {len(leads)} leads for business {business_id}")
        
        return True
    except Exception as e:
        print(f"❌ Dashboard API test failed: {str(e)}")
        return False

def test_reddit_scraper():
    """Test Reddit scraper with PostgreSQL"""
    print("🔍 Testing Reddit scraper integration...")
    
    try:
        sys.path.append('./f5bot_tests')
        from reddit_scrape import save_posts_to_database, RedditPost
        
        # Create a test post
        test_post = RedditPost(
            id='test_post_123',
            title='Test PostgreSQL Integration',
            content='This is a test post to verify PostgreSQL integration works.',
            author='test_user',
            subreddit='test',
            url='https://reddit.com/test',
            score=1,
            num_comments=0,
            created_utc=1234567890,
            permalink='https://reddit.com/test',
            matched_keywords=['test', 'postgresql']
        )
        
        # Try to save it
        saved_count = save_posts_to_database([test_post])
        
        if saved_count > 0:
            print("✅ Reddit scraper PostgreSQL integration working!")
            return True
        else:
            print("⚠️  Reddit scraper test completed (post may have been duplicate)")
            return True
            
    except Exception as e:
        print(f"❌ Reddit scraper test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🧪 POSTGRESQL MIGRATION VERIFICATION")
    print("=" * 40)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Dashboard API", test_dashboard_api),
        ("Reddit Scraper", test_reddit_scraper)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 20)
        
        if test_func():
            passed += 1
        
    print(f"\n📊 TEST RESULTS")
    print("=" * 20)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! PostgreSQL migration successful!")
        print("\n🚀 Next steps:")
        print("  1. Start the app: ./start-app.sh")
        print("  2. Visit: http://localhost:3050/dashboard")
        print("  3. Test Reddit scraper: cd f5bot_tests && python reddit_scrape.py")
        return True
    else:
        print("❌ Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)