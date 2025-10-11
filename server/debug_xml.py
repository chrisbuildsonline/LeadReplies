#!/usr/bin/env python3
"""
Debug XML structure
"""

import requests
import xml.etree.ElementTree as ET

def debug_xml():
    """Debug the actual XML structure"""
    print("🔍 Debugging XML structure...")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    })
    
    url = "https://www.reddit.com/r/entrepreneur/new/.rss?limit=3"
    response = session.get(url, timeout=10)
    
    print(f"✅ Got response: {response.status_code}")
    
    try:
        root = ET.fromstring(response.text)
        
        print(f"Root tag: {root.tag}")
        print(f"Root attributes: {root.attrib}")
        
        # Find all entries
        atom_ns = {'atom': 'http://www.w3.org/2005/Atom'}
        entries = root.findall('.//atom:entry', atom_ns)
        
        print(f"Found {len(entries)} entries")
        
        if entries:
            entry = entries[0]
            print(f"\nFirst entry tag: {entry.tag}")
            print(f"First entry attributes: {entry.attrib}")
            
            print("\nAll child elements:")
            for child in entry:
                print(f"  {child.tag}: {child.text[:50] if child.text else 'None'}...")
                if child.attrib:
                    print(f"    Attributes: {child.attrib}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_xml()