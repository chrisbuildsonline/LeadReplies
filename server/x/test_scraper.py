#!/usr/bin/env python3
"""
Test script for X scraper to verify installation and basic functionality.
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported."""
    print("🧪 Testing imports...")
    
    try:
        import snscrape.modules.twitter as sntwitter
        print("✅ snscrape imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import snscrape: {e}")
        print("💡 Install with: pip install snscrape")
        return False
    
    try:
        from x_scraper import XScrapingLeadFinder, search_x_leads
        print("✅ x_scraper imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import x_scraper: {e}")
        return False
    
    try:
        from scraper_config import KEYWORDS, SEARCH_CONFIG
        print("✅ scraper_config imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import scraper_config: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic scraper functionality with a simple search."""
    print("\n🔍 Testing basic search functionality...")
    
    try:
        from x_scraper import search_x_leads
        
        # Test with a simple, common keyword
        test_keywords = ["marketing"]
        
        print(f"Searching for: {test_keywords}")
        print("(This may take a moment...)")
        
        # Search with minimal parameters
        leads = search_x_leads(
            keywords=test_keywords,
            days_back=1,  # Only search last day
            limit=5       # Only get 5 tweets for testing
        )
        
        print(f"✅ Search completed successfully!")
        print(f"📊 Found {len(leads)} tweets")
        
        if leads:
            print("\n📝 Sample result:")
            lead = leads[0]
            print(f"  User: @{lead['username']}")
            print(f"  Content: {lead['content'][:100]}...")
            print(f"  Confidence: {lead['confidence_score']:.2f}")
            print(f"  Engagement: {lead['engagement_total']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Search test failed: {e}")
        return False

def test_configuration():
    """Test configuration loading."""
    print("\n⚙️  Testing configuration...")
    
    try:
        from scraper_config import KEYWORDS, SEARCH_CONFIG, FILTER_CONFIG
        
        print(f"✅ Loaded {len(KEYWORDS)} keywords")
        print(f"✅ Search config: {SEARCH_CONFIG}")
        print(f"✅ Filter config loaded")
        
        # Check if keywords are reasonable
        if len(KEYWORDS) == 0:
            print("⚠️  Warning: No keywords configured")
        elif len(KEYWORDS) > 50:
            print("⚠️  Warning: Many keywords configured, searches may be slow")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 X Scraper Test Suite")
    print("=" * 40)
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Imports
    if test_imports():
        tests_passed += 1
    
    # Test 2: Configuration
    if test_configuration():
        tests_passed += 1
    
    # Test 3: Basic functionality (only if imports work)
    if tests_passed >= 1:
        if test_basic_functionality():
            tests_passed += 1
    else:
        print("\n⏭️  Skipping functionality test due to import failures")
    
    # Results
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! X scraper is ready to use.")
        print("\n🚀 Next steps:")
        print("  1. Customize keywords in scraper_config.py")
        print("  2. Run: python run_x_scraper.py search")
        print("  3. Or search specific keyword: python run_x_scraper.py search 'your keyword'")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        
        if tests_passed == 0:
            print("\n💡 Quick fix suggestions:")
            print("  - Install snscrape: pip install snscrape")
            print("  - Make sure you're in the server/x directory")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)