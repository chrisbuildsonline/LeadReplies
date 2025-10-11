#!/usr/bin/env python3
"""
Debug what Reddit is actually returning
"""

import requests

def check_reddit_response():
    """Check what Reddit actually returns"""
    print("🔍 Checking Reddit response content...")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    })
    
    url = "https://www.reddit.com/r/entrepreneur/new/.rss?limit=5"
    
    try:
        response = session.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'unknown')}")
        print(f"Content length: {len(response.text)}")
        print("\nFirst 500 characters:")
        print("=" * 50)
        print(response.text[:500])
        print("=" * 50)
        
        # Check if it's HTML instead of RSS
        if '<html' in response.text.lower():
            print("\n⚠️  Response is HTML, not RSS!")
            print("This suggests Reddit is blocking RSS access or redirecting.")
        elif '<?xml' in response.text:
            print("\n✅ Response appears to be XML")
        else:
            print("\n❓ Response format unclear")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_reddit_response()