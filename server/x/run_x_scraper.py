#!/usr/bin/env python3
"""
Main script to run X (Twitter) scraper with configuration.
"""

import json
import sys
import time
from datetime import datetime, timedelta
from x_scraper import XScrapingLeadFinder, search_x_leads
from scraper_config import (
    KEYWORDS, SEARCH_CONFIG, MONITORING_CONFIG, 
    FILTER_CONFIG, OUTPUT_CONFIG, ADVANCED_SEARCH
)


def run_single_search():
    """Run a single search with configured parameters."""
    print("🐦 Starting X (Twitter) Lead Search")
    print("=" * 50)
    
    print(f"Keywords ({len(KEYWORDS)}): {', '.join(KEYWORDS[:3])}{'...' if len(KEYWORDS) > 3 else ''}")
    print(f"Days back: {SEARCH_CONFIG['days_back']}")
    print(f"Limit: {SEARCH_CONFIG['limit']}")
    print(f"Language: {ADVANCED_SEARCH.get('language', 'all')}")
    print()
    
    # Perform search
    leads = search_x_leads(
        keywords=KEYWORDS,
        days_back=SEARCH_CONFIG['days_back'],
        limit=SEARCH_CONFIG['limit']
    )
    
    # Apply additional filters
    filtered_leads = apply_filters(leads)
    
    print(f"✅ Found {len(leads)} total tweets")
    print(f"✅ {len(filtered_leads)} leads after filtering")
    
    if filtered_leads:
        # Sort results
        sort_field = OUTPUT_CONFIG.get('sort_by', 'hotness_score')
        filtered_leads.sort(key=lambda x: x.get(sort_field, 0), reverse=True)
        
        # Show top results
        print(f"\n🏆 Top 10 leads (sorted by {sort_field}):")
        for i, lead in enumerate(filtered_leads[:10], 1):
            created_date = datetime.fromisoformat(lead['created_date'].replace('Z', '+00:00'))
            hours_ago = (datetime.now() - created_date.replace(tzinfo=None)).total_seconds() / 3600
            
            print(f"{i:2d}. [@{lead['username']}] {lead['content'][:80]}...")
            print(f"    Engagement: {lead['engagement_total']} | Confidence: {lead['confidence_score']:.2f} | Hotness: {lead['hotness_score']:.1f}")
            print(f"    Keywords: {', '.join(lead['keywords_matched'])}")
            print(f"    {hours_ago:.1f}h ago | {lead['like_count']} likes | {lead['retweet_count']} RTs")
            if lead['hashtags']:
                print(f"    Hashtags: {', '.join(lead['hashtags'][:3])}")
            print(f"    🔗 {lead['url']}")
            print()
        
        # Show statistics
        show_lead_stats(filtered_leads)
        
        # Save results
        save_results(filtered_leads)
    
    return filtered_leads


def apply_filters(leads):
    """Apply filtering based on configuration."""
    filtered = []
    
    for lead in leads:
        # Check minimum confidence
        if lead.get('confidence_score', 0) < FILTER_CONFIG['min_confidence']:
            continue
            
        # Check minimum hotness
        if lead.get('hotness_score', 0) < FILTER_CONFIG['min_hotness']:
            continue
            
        # Check minimum engagement
        if lead.get('engagement_total', 0) < FILTER_CONFIG['min_engagement']:
            continue
            
        # Check tweet age
        created_date = datetime.fromisoformat(lead['created_date'].replace('Z', '+00:00'))
        hours_ago = (datetime.now() - created_date.replace(tzinfo=None)).total_seconds() / 3600
        if hours_ago > FILTER_CONFIG['max_age_hours']:
            continue
            
        # Check for excluded keywords
        content = lead.get('content', '').lower()
        if any(excluded.lower() in content for excluded in FILTER_CONFIG['exclude_keywords']):
            continue
            
        # Check for excluded users
        username = lead.get('username', '').lower()
        if any(excluded.lower() in username for excluded in FILTER_CONFIG['exclude_users']):
            continue
            
        # Skip retweets if configured
        if not SEARCH_CONFIG['include_retweets'] and lead.get('is_retweet', False):
            continue
            
        filtered.append(lead)
    
    return filtered


def show_lead_stats(leads):
    """Show statistics about the leads found."""
    if not leads:
        return
        
    # Keyword statistics
    keyword_stats = {}
    hashtag_stats = {}
    user_stats = {}
    
    total_engagement = 0
    
    for lead in leads:
        # Count keyword matches
        for keyword in lead['keywords_matched']:
            keyword_stats[keyword] = keyword_stats.get(keyword, 0) + 1
            
        # Count hashtag usage
        for hashtag in lead.get('hashtags', []):
            hashtag_stats[hashtag] = hashtag_stats.get(hashtag, 0) + 1
            
        # Count user activity
        username = lead['username']
        user_stats[username] = user_stats.get(username, 0) + 1
        
        # Sum engagement
        total_engagement += lead.get('engagement_total', 0)
    
    print("📊 Lead Statistics:")
    print(f"  Average engagement: {total_engagement / len(leads):.1f}")
    print(f"  Average confidence: {sum(l['confidence_score'] for l in leads) / len(leads):.2f}")
    print()
    
    if keyword_stats:
        print("🔑 Top keyword matches:")
        for keyword, count in sorted(keyword_stats.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  '{keyword}': {count} matches")
        print()
    
    if hashtag_stats:
        print("# Top hashtags:")
        for hashtag, count in sorted(hashtag_stats.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  #{hashtag}: {count} uses")
        print()
    
    # Show engagement distribution
    high_engagement = len([l for l in leads if l['engagement_total'] > 10])
    medium_engagement = len([l for l in leads if 3 <= l['engagement_total'] <= 10])
    low_engagement = len([l for l in leads if l['engagement_total'] < 3])
    
    print("📈 Engagement distribution:")
    print(f"  High (>10): {high_engagement} tweets")
    print(f"  Medium (3-10): {medium_engagement} tweets")
    print(f"  Low (<3): {low_engagement} tweets")
    print()


def save_results(leads):
    """Save results to file."""
    output_file = OUTPUT_CONFIG['output_file']
    
    # Add metadata
    results = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "total_leads": len(leads),
            "keywords_used": KEYWORDS,
            "search_config": SEARCH_CONFIG,
            "filter_config": FILTER_CONFIG,
            "platform": "X (Twitter)"
        },
        "leads": leads
    }
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"💾 Results saved to {output_file}")


def run_continuous_monitoring():
    """Run continuous monitoring for new tweets."""
    print("🔄 Starting Continuous X Monitoring")
    print("=" * 50)
    
    def handle_new_leads(leads):
        """Handle new leads found during monitoring."""
        if not leads:
            return
            
        filtered_leads = apply_filters(leads)
        
        if filtered_leads:
            print(f"🚨 Found {len(filtered_leads)} new qualified leads!")
            
            for lead in filtered_leads[:3]:  # Show first 3
                print(f"  - @{lead['username']}: {lead['content'][:60]}...")
            
            if MONITORING_CONFIG['save_to_file']:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"x_monitoring_leads_{timestamp}.json"
                with open(filename, 'w') as f:
                    json.dump(filtered_leads, f, indent=2)
                print(f"  💾 Saved to {filename}")
    
    print(f"Monitoring keywords: {', '.join(KEYWORDS[:3])}...")
    print(f"Check interval: {MONITORING_CONFIG['interval_minutes']} minutes")
    print(f"Days back: {MONITORING_CONFIG['days_back']} days")
    print("\nPress Ctrl+C to stop monitoring\n")
    
    try:
        while True:
            print(f"🔍 Checking for new tweets... ({datetime.now().strftime('%H:%M:%S')})")
            
            # Search for recent tweets
            leads = search_x_leads(
                keywords=KEYWORDS,
                days_back=MONITORING_CONFIG['days_back'],
                limit=MONITORING_CONFIG['max_tweets_per_check']
            )
            
            handle_new_leads(leads)
            
            # Wait for next check
            time.sleep(MONITORING_CONFIG['interval_minutes'] * 60)
            
    except KeyboardInterrupt:
        print("\n⏹️  Monitoring stopped by user")


def search_specific_keyword(keyword: str):
    """Search for a specific keyword."""
    print(f"🔍 Searching X for specific keyword: '{keyword}'")
    print("=" * 50)
    
    leads = search_x_leads(
        keywords=[keyword],
        days_back=SEARCH_CONFIG['days_back'],
        limit=SEARCH_CONFIG['limit']
    )
    
    filtered_leads = apply_filters(leads)
    
    print(f"✅ Found {len(filtered_leads)} leads for '{keyword}'")
    
    if filtered_leads:
        for i, lead in enumerate(filtered_leads[:5], 1):
            print(f"\n{i}. @{lead['username']}: {lead['content'][:100]}...")
            print(f"   Confidence: {lead['confidence_score']:.2f} | Engagement: {lead['engagement_total']}")
            print(f"   🔗 {lead['url']}")
    
    return filtered_leads


def main():
    """Main function with command line options."""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "monitor":
            run_continuous_monitoring()
        elif command == "search":
            if len(sys.argv) > 2:
                # Search for specific keyword
                keyword = " ".join(sys.argv[2:])
                search_specific_keyword(keyword)
            else:
                run_single_search()
        elif command == "config":
            print("Current X Scraper Configuration:")
            print(f"Keywords: {len(KEYWORDS)} items")
            print(f"Search config: {SEARCH_CONFIG}")
            print(f"Filter config: {FILTER_CONFIG}")
            print(f"Advanced search: {ADVANCED_SEARCH}")
        else:
            print("Usage:")
            print("  python run_x_scraper.py search                    - Run search with all configured keywords")
            print("  python run_x_scraper.py search 'specific keyword' - Search for specific keyword")
            print("  python run_x_scraper.py monitor                   - Start continuous monitoring")
            print("  python run_x_scraper.py config                    - Show current configuration")
    else:
        # Default: run single search
        run_single_search()


if __name__ == "__main__":
    main()