#!/usr/bin/env python3
"""
Debug the parsing process step by step
"""

import requests
import xml.etree.ElementTree as ET
import re
from datetime import datetime, timedelta

def debug_parsing():
    """Debug the parsing process"""
    print("🔍 Debugging Reddit feed parsing...")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    })
    
    url = "https://www.reddit.com/r/entrepreneur/new/.rss?limit=5"
    
    try:
        response = session.get(url, timeout=10)
        print(f"✅ Got response: {response.status_code}")
        
        root = ET.fromstring(response.text)
        
        # Handle Atom feeds
        atom_ns = {'atom': 'http://www.w3.org/2005/Atom'}
        entries = root.findall('.//atom:entry', atom_ns)
        
        print(f"📊 Found {len(entries)} entries")
        
        if entries:
            print("\n🔍 Analyzing first entry:")
            entry = entries[0]
            
            # Get title
            title_elem = entry.find('.//{http://www.w3.org/2005/Atom}title')
            title = title_elem.text if title_elem is not None else "No title"
            print(f"   Title: {title[:60]}...")
            
            # Get link
            link_elem = entry.find('.//{http://www.w3.org/2005/Atom}link[@rel="alternate"]')
            if not link_elem:
                link_elem = entry.find('.//{http://www.w3.org/2005/Atom}link')
            link = link_elem.get('href', '') if link_elem is not None else "No link"
            print(f"   Link: {link}")
            
            # Get date
            date_elem = entry.find('.//{http://www.w3.org/2005/Atom}published') or entry.find('.//{http://www.w3.org/2005/Atom}updated')
            if date_elem is not None:
                date_str = date_elem.text
                print(f"   Date string: {date_str}")
                
                # Try to parse date
                try:
                    pub_date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S%z')
                    print(f"   Parsed date: {pub_date}")
                    
                    # Check if it's within our date range
                    cutoff_date = datetime.now() - timedelta(days=2)
                    print(f"   Cutoff date: {cutoff_date}")
                    print(f"   Within range: {pub_date.replace(tzinfo=None) >= cutoff_date}")
                    
                except ValueError as e:
                    print(f"   Date parse error: {e}")
            else:
                print("   No date found")
            
            # Get content
            content_elem = entry.find('.//{http://www.w3.org/2005/Atom}content')
            if content_elem is not None:
                content = content_elem.text or ""
                clean_content = re.sub(r'<[^>]+>', '', content)
                print(f"   Content: {clean_content[:100]}...")
            else:
                print("   No content found")
            
            # Test keyword matching
            test_keywords = ["SaaS", "marketing", "CRM", "help", "tool"]
            full_text = f"{title} {clean_content if 'clean_content' in locals() else ''}".lower()
            
            matched_keywords = []
            for keyword in test_keywords:
                if keyword.lower() in full_text:
                    matched_keywords.append(keyword)
            
            print(f"   Matched keywords: {matched_keywords}")
            
        else:
            print("❌ No entries found in feed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_parsing()