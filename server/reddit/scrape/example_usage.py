#!/usr/bin/env python3
"""
Example usage of the improved Reddit scraper with customizable parameters.
"""

from reddit_scrape import search_reddit_leads, RedditScrapingLeadFinder
import json
from datetime import datetime

def example_basic_search():
    """Basic search example with custom parameters."""
    print("=== Basic Search Example ===")
    
    # Define your search parameters
    keywords = [
        "SaaS", "marketing automation", "CRM", "lead generation",
        "email marketing", "customer acquisition", "growth hacking"
    ]
    
    # Target specific subreddits
    subreddits = [
        "entrepreneur", "startups", "marketing", "SaaS",
        "smallbusiness", "digitalnomad", "webdev"
    ]
    
    # Search the last 4 days (as requested)
    days_back = 4
    
    print(f"Searching for keywords: {', '.join(keywords)}")
    print(f"In subreddits: {', '.join([f'r/{sub}' for sub in subreddits])}")
    print(f"Looking back: {days_back} days")
    print("Using JSON endpoints only (no API keys needed)...")
    
    # Perform the search
    leads = search_reddit_leads(
        keywords=keywords,
        subreddits=subreddits,
        days_back=days_back,
        limit=1000
    )
    
    print(f"\nFound {len(leads)} leads!")
    
    # Show top results
    if leads:
        print("\nTop 10 leads:")
        for i, lead in enumerate(leads[:10], 1):
            created_date = datetime.fromisoformat(lead['created_date'].replace('Z', '+00:00'))
            days_ago = (datetime.now() - created_date.replace(tzinfo=None)).days
            print(f"{i:2d}. [{lead['type'].upper()}] {lead['title'][:70]}...")
            print(f"    r/{lead['subreddit']} | Score: {lead['hotness_score']} | {days_ago}d ago")
            print(f"    Keywords: {', '.join(lead['keywords_matched'])}")
            print(f"    URL: {lead['url']}")
            print()
    
    # Save results
    with open("example_leads.json", "w") as f:
        json.dump(leads, f, indent=2)
    print(f"Results saved to example_leads.json")
    
    return leads

def example_targeted_search():
    """Example of a more targeted search for specific use cases."""
    print("\n=== Targeted Search Example ===")
    
    # More specific keywords for a particular niche
    keywords = [
        "email automation", "drip campaign", "email sequence",
        "marketing automation", "email marketing tool", "autoresponder"
    ]
    
    # Focus on marketing-related subreddits
    subreddits = ["marketing", "emailmarketing", "entrepreneur", "smallbusiness"]
    
    # Look back 7 days for more comprehensive results
    days_back = 7
    
    leads = search_reddit_leads(
        keywords=keywords,
        subreddits=subreddits,
        days_back=days_back,
        limit=500
    )
    
    print(f"Found {len(leads)} targeted leads for email marketing tools")
    
    # Analyze keyword performance
    keyword_stats = {}
    for lead in leads:
        for keyword in lead['keywords_matched']:
            keyword_stats[keyword] = keyword_stats.get(keyword, 0) + 1
    
    if keyword_stats:
        print("\nKeyword performance:")
        for keyword, count in sorted(keyword_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"  {keyword}: {count} matches")
    
    return leads

def example_continuous_monitoring():
    """Example of continuous monitoring setup."""
    print("\n=== Continuous Monitoring Example ===")
    
    finder = RedditScrapingLeadFinder()
    
    keywords = ["SaaS", "B2B software", "marketing tool"]
    subreddits = ["entrepreneur", "startups", "SaaS"]
    
    def handle_new_leads(leads):
        """Callback function to handle new leads as they're found."""
        print(f"🚨 Found {len(leads)} new leads!")
        for lead in leads:
            print(f"  - {lead['title'][:50]}... in r/{lead['subreddit']}")
        
        # Save to file or send notification
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"new_leads_{timestamp}.json"
        with open(filename, "w") as f:
            json.dump(leads, f, indent=2)
    
    print("Starting continuous monitoring...")
    print("(This will run indefinitely - press Ctrl+C to stop)")
    print(f"Checking every 5 minutes for new content in the last 1 day")
    
    # Uncomment the line below to start monitoring
    # finder.monitor_continuous(
    #     keywords=keywords,
    #     subreddits=subreddits,
    #     interval_minutes=5,
    #     days_back=1,
    #     callback=handle_new_leads
    # )

def main():
    """Run all examples."""
    print("Reddit Lead Scraper - Enhanced Version")
    print("=====================================")
    
    # Run basic search
    leads1 = example_basic_search()
    
    # Run targeted search
    leads2 = example_targeted_search()
    
    # Show monitoring example (but don't actually start it)
    example_continuous_monitoring()
    
    print(f"\nTotal leads found: {len(leads1) + len(leads2)}")
    print("All examples completed!")

if __name__ == "__main__":
    main()