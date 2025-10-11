#!/usr/bin/env python3
"""
Test just the parsing function
"""

import requests
from reddit_scraper_final import RedditLeadScraper

def test_parse_only():
    """Test just the parsing function"""
    print("🧪 Testing RSS parsing function only...")
    
    scraper = RedditLeadScraper()
    
    # Get RSS content
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    })
    
    url = "https://www.reddit.com/r/entrepreneur/new/.rss?limit=5"
    response = session.get(url, timeout=10)
    
    print(f"✅ Got RSS response: {response.status_code}")
    
    # Test parsing
    posts = scraper._parse_rss_feed(response.text, "entrepreneur")
    
    print(f"📊 Parsed {len(posts)} posts")
    
    if posts:
        for i, post in enumerate(posts[:3], 1):
            print(f"{i}. {post.get('title', '')[:50]}...")
            print(f"   ID: {post.get('id', '')}")
            print(f"   URL: {post.get('url', '')}")
            print(f"   Content: {post.get('selftext', '')[:50]}...")
            print()
    else:
        print("❌ No posts parsed")

if __name__ == "__main__":
    test_parse_only()