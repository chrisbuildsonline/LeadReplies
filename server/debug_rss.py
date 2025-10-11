#!/usr/bin/env python3
"""
Debug RSS feeds to see what's happening
"""

import requests
import xml.etree.ElementTree as ET

def test_rss_direct():
    """Test RSS feeds directly"""
    print("🔍 Testing RSS feeds directly...")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    })
    
    test_urls = [
        "https://www.reddit.com/r/entrepreneur/new/.rss?limit=5",
        "https://www.reddit.com/r/entrepreneur/.rss?limit=5",
        "https://www.reddit.com/r/startups/new/.rss?limit=5",
    ]
    
    for url in test_urls:
        print(f"\n📡 Testing: {url}")
        try:
            response = session.get(url, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   Content length: {len(response.text)}")
                
                # Try to parse XML
                try:
                    root = ET.fromstring(response.text)
                    items = root.findall('.//item')
                    print(f"   Items found: {len(items)}")
                    
                    if items:
                        first_item = items[0]
                        title_elem = first_item.find('title')
                        if title_elem is not None:
                            print(f"   First title: {title_elem.text[:60]}...")
                        else:
                            print("   No title found in first item")
                    
                except ET.ParseError as e:
                    print(f"   XML Parse Error: {e}")
                    print(f"   First 200 chars: {response.text[:200]}")
                
            else:
                print(f"   Error: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"   Exception: {e}")

if __name__ == "__main__":
    test_rss_direct()