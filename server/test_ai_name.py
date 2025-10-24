#!/usr/bin/env python3
"""
Test script to debug AI business name extraction
"""
import sys
import os
sys.path.append('.')

from deepseek_analyzer import DeepSeekAnalyzer
import json

def test_business_name_extraction():
    analyzer = DeepSeekAnalyzer()
    
    # Test with gojiberry.ai
    website_url = "https://gojiberry.ai/"
    business_name = "test5"  # Current name from the form
    
    print(f"🔍 Testing AI analysis for:")
    print(f"   Website: {website_url}")
    print(f"   Current Name: {business_name}")
    print("=" * 50)
    
    try:
        result = analyzer.comprehensive_business_setup(
            website_url=website_url,
            business_name=business_name
        )
        
        print("✅ AI Analysis Result:")
        print(json.dumps(result, indent=2))
        
        if result.get('business_info'):
            ai_name = result['business_info'].get('name')
            print(f"\n🏢 Business Name Analysis:")
            print(f"   Original: '{business_name}'")
            print(f"   AI Suggested: '{ai_name}'")
            print(f"   Changed: {'Yes' if ai_name != business_name else 'No'}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_business_name_extraction()