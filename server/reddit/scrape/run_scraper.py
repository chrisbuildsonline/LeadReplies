#!/usr/bin/env python3
"""
Main script to run Reddit scraper with configuration.
Uses both JSON API and RSS fallback for maximum reliability.
"""

import json
import sys
from datetime import datetime
from reddit_scrape import RedditScrapingLeadFinder, search_reddit_leads
from reddit_rss_scraper import search_reddit_leads_rss
from scraper_config import (
    KEYWORDS, SUBREDDITS, SEARCH_CONFIG, MONITORING_CONFIG, 
    FILTER_CONFIG, OUTPUT_CONFIG
)

def run_single_search():
    """Run a single search with configured parameters using F5Bot methodology."""
    print("🔍 Starting F5Bot-Style Reddit Lead Search")
    print("=" * 50)
    
    print(f"Keywords ({len(KEYWORDS)}): {', '.join(KEYWORDS[:5])}{'...' if len(KEYWORDS) > 5 else ''}")
    print(f"Subreddits ({len(SUBREDDITS)}): {', '.join([f'r/{sub}' for sub in SUBREDDITS[:5]])}{'...' if len(SUBREDDITS) > 5 else ''}")
    print(f"Days back: {SEARCH_CONFIG['days_back']}")
    print(f"Limit: {SEARCH_CONFIG['limit']}")
    print()
    
    # Try JSON API first (F5Bot primary method)
    print("🚀 Attempting JSON API scraping (F5Bot primary method)...")
    leads = []
    
    try:
        leads = search_reddit_leads(
            keywords=KEYWORDS,
            subreddits=SUBREDDITS,
            days_back=SEARCH_CONFIG['days_back'],
            limit=SEARCH_CONFIG['limit']
        )
        
        if leads:
            print(f"✅ JSON API successful: Found {len(leads)} leads")
        else:
            print("⚠️  JSON API returned no results, trying RSS fallback...")
            raise Exception("No results from JSON API")
            
    except Exception as e:
        print(f"❌ JSON API failed: {str(e)}")
        print("🔄 Falling back to RSS scraping (F5Bot backup method)...")
        
        try:
            # Use RSS as fallback
            leads = search_reddit_leads_rss(
                keywords=KEYWORDS,
                subreddits=SUBREDDITS,
                days_back=SEARCH_CONFIG['days_back'],
                limit_per_sub=max(10, SEARCH_CONFIG['limit'] // len(SUBREDDITS))
            )
            
            if leads:
                print(f"✅ RSS fallback successful: Found {len(leads)} leads")
            else:
                print("❌ Both methods failed to find leads")
                
        except Exception as rss_error:
            print(f"❌ RSS fallback also failed: {str(rss_error)}")
            print("💡 Try reducing the number of subreddits or increasing delays")
    
    # Apply additional filters
    filtered_leads = apply_filters(leads)
    
    print(f"✅ Found {len(leads)} total leads")
    print(f"✅ {len(filtered_leads)} leads after filtering")
    
    if filtered_leads:
        # Sort results
        sort_field = OUTPUT_CONFIG.get('sort_by', 'hotness_score')
        filtered_leads.sort(key=lambda x: x.get(sort_field, 0), reverse=True)
        
        # Show top results
        print(f"\n🏆 Top 10 leads (sorted by {sort_field}):")
        for i, lead in enumerate(filtered_leads[:10], 1):
            created_date = datetime.fromisoformat(lead['created_date'].replace('Z', '+00:00'))
            days_ago = (datetime.now() - created_date.replace(tzinfo=None)).days
            
            print(f"{i:2d}. [{lead['type'].upper()}] {lead['title'][:60]}...")
            print(f"    r/{lead['subreddit']} | Score: {lead['hotness_score']} | Confidence: {lead['confidence_score']:.2f}")
            print(f"    Keywords: {', '.join(lead['keywords_matched'])}")
            print(f"    {days_ago}d ago | {lead['upvotes']} upvotes")
            print()
        
        # Show keyword statistics
        show_keyword_stats(filtered_leads)
        
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
            
        # Check minimum score
        if lead.get('upvotes', 0) < SEARCH_CONFIG['min_score']:
            continue
            
        # Check for excluded keywords
        content = f"{lead.get('title', '')} {lead.get('content', '')}".lower()
        if any(excluded in content for excluded in FILTER_CONFIG['exclude_keywords']):
            continue
            
        filtered.append(lead)
    
    return filtered

def show_keyword_stats(leads):
    """Show statistics about keyword matches."""
    keyword_stats = {}
    subreddit_stats = {}
    
    for lead in leads:
        # Count keyword matches
        for keyword in lead['keywords_matched']:
            keyword_stats[keyword] = keyword_stats.get(keyword, 0) + 1
            
        # Count subreddit distribution
        subreddit = lead['subreddit']
        subreddit_stats[subreddit] = subreddit_stats.get(subreddit, 0) + 1
    
    if keyword_stats:
        print("📊 Top keyword matches:")
        for keyword, count in sorted(keyword_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {keyword}: {count} matches")
        print()
    
    if subreddit_stats:
        print("📊 Subreddit distribution:")
        for subreddit, count in sorted(subreddit_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  r/{subreddit}: {count} leads")
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
            "subreddits_searched": SUBREDDITS,
            "search_config": SEARCH_CONFIG,
            "filter_config": FILTER_CONFIG
        },
        "leads": leads
    }
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"💾 Results saved to {output_file}")

def run_continuous_monitoring():
    """Run continuous monitoring."""
    print("🔄 Starting Continuous Monitoring")
    print("=" * 50)
    
    finder = RedditScrapingLeadFinder()
    
    def handle_new_leads(leads):
        """Handle new leads found during monitoring."""
        if not leads:
            return
            
        filtered_leads = apply_filters(leads)
        
        if filtered_leads:
            print(f"🚨 Found {len(filtered_leads)} new qualified leads!")
            
            for lead in filtered_leads[:3]:  # Show first 3
                print(f"  - {lead['title'][:50]}... in r/{lead['subreddit']}")
            
            if MONITORING_CONFIG['save_to_file']:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"monitoring_leads_{timestamp}.json"
                with open(filename, 'w') as f:
                    json.dump(filtered_leads, f, indent=2)
                print(f"  💾 Saved to {filename}")
    
    print(f"Monitoring keywords: {', '.join(KEYWORDS[:3])}...")
    print(f"Monitoring subreddits: {', '.join([f'r/{sub}' for sub in SUBREDDITS[:3]])}...")
    print(f"Check interval: {MONITORING_CONFIG['interval_minutes']} minutes")
    print(f"Days back: {MONITORING_CONFIG['days_back']} days")
    print("\nPress Ctrl+C to stop monitoring\n")
    
    try:
        finder.monitor_continuous(
            keywords=KEYWORDS,
            subreddits=SUBREDDITS,
            interval_minutes=MONITORING_CONFIG['interval_minutes'],
            days_back=MONITORING_CONFIG['days_back'],
            callback=handle_new_leads
        )
    except KeyboardInterrupt:
        print("\n⏹️  Monitoring stopped by user")

def main():
    """Main function with command line options."""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "monitor":
            run_continuous_monitoring()
        elif command == "search":
            run_single_search()
        elif command == "config":
            print("Current configuration:")
            print(f"Keywords: {len(KEYWORDS)} items")
            print(f"Subreddits: {len(SUBREDDITS)} items")
            print(f"Search config: {SEARCH_CONFIG}")
            print(f"Filter config: {FILTER_CONFIG}")
        else:
            print("Usage:")
            print("  python run_scraper.py search   - Run single search")
            print("  python run_scraper.py monitor  - Start continuous monitoring")
            print("  python run_scraper.py config   - Show current configuration")
    else:
        # Default: run single search
        run_single_search()

if __name__ == "__main__":
    main()