#!/usr/bin/env python3
"""
Demo script showing what X scraper results would look like for "how to market".
This simulates the output format and scoring system.
"""

import json
from datetime import datetime, timedelta
import random

def generate_demo_leads():
    """Generate realistic demo leads for 'how to market' search."""
    
    # Sample tweets that would match "how to market" searches
    sample_tweets = [
        {
            "text": "How to market my small business on a tight budget? Any tips for getting started with digital marketing?",
            "username": "smallbiz_owner",
            "engagement": {"likes": 15, "retweets": 3, "replies": 8},
            "hours_ago": 2.5
        },
        {
            "text": "Struggling with how to market my freelance services. Social media feels overwhelming. Where should I start?",
            "username": "freelancer_jane",
            "engagement": {"likes": 8, "retweets": 1, "replies": 12},
            "hours_ago": 6.2
        },
        {
            "text": "How to market a SaaS product effectively? Looking for advice on customer acquisition strategies.",
            "username": "saas_founder",
            "engagement": {"likes": 23, "retweets": 7, "replies": 15},
            "hours_ago": 12.1
        },
        {
            "text": "Need help figuring out how to market my online course. Any recommendations for platforms or strategies?",
            "username": "course_creator",
            "engagement": {"likes": 11, "retweets": 2, "replies": 6},
            "hours_ago": 18.5
        },
        {
            "text": "How to market myself as a consultant? Building personal brand seems daunting but necessary.",
            "username": "consultant_mike",
            "engagement": {"likes": 19, "retweets": 4, "replies": 9},
            "hours_ago": 24.3
        },
        {
            "text": "Any advice on how to market a local restaurant? Traditional advertising is too expensive.",
            "username": "restaurant_owner",
            "engagement": {"likes": 7, "retweets": 1, "replies": 4},
            "hours_ago": 36.7
        },
        {
            "text": "How to market my app without a huge budget? Bootstrap marketing strategies needed!",
            "username": "app_developer",
            "engagement": {"likes": 14, "retweets": 5, "replies": 7},
            "hours_ago": 48.2
        },
        {
            "text": "Looking for tips on how to market my photography business. Word of mouth isn't enough anymore.",
            "username": "photographer_pro",
            "engagement": {"likes": 9, "retweets": 2, "replies": 5},
            "hours_ago": 72.1
        }
    ]
    
    leads = []
    keywords = ["how to market"]
    
    for i, tweet_data in enumerate(sample_tweets):
        # Calculate engagement total
        eng = tweet_data["engagement"]
        engagement_total = eng["likes"] + eng["retweets"] + eng["replies"]
        
        # Calculate confidence score
        keyword_score = 1.0  # All tweets contain "how to market"
        engagement_score = min(engagement_total / 20, 1.0)  # Normalize to 0-1
        recency_score = max(0, 1 - (tweet_data["hours_ago"] / (24 * 7)))  # Decay over week
        quality_score = 0.8 if "?" in tweet_data["text"] else 0.6  # Questions are higher quality
        
        confidence_score = (keyword_score * 0.4 + 
                          engagement_score * 0.3 + 
                          recency_score * 0.2 + 
                          quality_score * 0.1)
        
        # Calculate hotness score
        hotness_score = engagement_total * max(0.1, 1 - (tweet_data["hours_ago"] / (24 * 3)))
        
        # Create timestamp
        created_time = datetime.now() - timedelta(hours=tweet_data["hours_ago"])
        
        lead = {
            "id": f"demo_tweet_{i+1}",
            "url": f"https://twitter.com/{tweet_data['username']}/status/{1234567890 + i}",
            "text": tweet_data["text"],
            "username": tweet_data["username"],
            "created_at": created_time.isoformat(),
            "like_count": eng["likes"],
            "retweet_count": eng["retweets"],
            "reply_count": eng["replies"],
            "engagement_total": engagement_total,
            "keywords_matched": keywords,
            "confidence_score": round(confidence_score, 3),
            "hotness_score": round(hotness_score, 1),
            "hours_ago": round(tweet_data["hours_ago"], 1)
        }
        
        leads.append(lead)
    
    # Sort by confidence score
    leads.sort(key=lambda x: x['confidence_score'], reverse=True)
    
    return leads

def display_demo_results():
    """Display demo results in the same format as the real scraper."""
    print("🐦 X (Twitter) Lead Search - DEMO RESULTS")
    print("🔍 Searching for: 'how to market'")
    print("=" * 60)
    
    leads = generate_demo_leads()
    
    print(f"✅ Found {len(leads)} potential leads")
    print(f"📊 Results sorted by confidence score")
    print()
    
    # Show top results
    print("🏆 Top leads:")
    for i, lead in enumerate(leads[:5], 1):
        print(f"{i:2d}. [@{lead['username']}] {lead['text'][:80]}...")
        print(f"    Confidence: {lead['confidence_score']:.2f} | Engagement: {lead['engagement_total']} | Hotness: {lead['hotness_score']}")
        print(f"    {lead['hours_ago']}h ago | {lead['like_count']} likes | {lead['retweet_count']} RTs | {lead['reply_count']} replies")
        print(f"    🔗 {lead['url']}")
        print()
    
    # Show statistics
    print("📊 Lead Statistics:")
    avg_confidence = sum(l['confidence_score'] for l in leads) / len(leads)
    avg_engagement = sum(l['engagement_total'] for l in leads) / len(leads)
    high_confidence = len([l for l in leads if l['confidence_score'] > 0.7])
    
    print(f"  Average confidence: {avg_confidence:.2f}")
    print(f"  Average engagement: {avg_engagement:.1f}")
    print(f"  High confidence leads (>0.7): {high_confidence}")
    print()
    
    # Show engagement distribution
    recent_leads = len([l for l in leads if l['hours_ago'] < 24])
    print(f"📈 Recency distribution:")
    print(f"  Last 24 hours: {recent_leads} leads")
    print(f"  Last 48 hours: {len([l for l in leads if l['hours_ago'] < 48])} leads")
    print(f"  Last week: {len(leads)} leads")
    print()
    
    # Save demo results
    results = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "total_leads": len(leads),
            "search_query": "how to market",
            "platform": "X (Twitter)",
            "note": "DEMO DATA - Real results would come from Twitter API"
        },
        "leads": leads
    }
    
    with open("demo_x_leads.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"💾 Demo results saved to demo_x_leads.json")
    print()
    print("🔧 To get real results:")
    print("  1. Set up Twitter API access (see setup_twitter_api.md)")
    print("  2. Run: python twitter_api_scraper.py")
    print("  3. Or use browser automation approach")

if __name__ == "__main__":
    display_demo_results()