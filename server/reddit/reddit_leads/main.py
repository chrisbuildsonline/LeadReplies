"""Main script for Reddit lead generation."""
import json
import argparse
from datetime import datetime
from typing import List, Dict, Any
from .config import RedditConfig, SearchConfig
from .lead_finder import RedditLeadFinder, Lead

def save_leads_to_file(leads: List[Lead], filename: str = None) -> str:
    """Save leads to JSON file."""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reddit_leads_{timestamp}.json"
    
    leads_data = {
        'timestamp': datetime.now().isoformat(),
        'total_leads': len(leads),
        'leads': [lead.to_dict() for lead in leads]
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(leads_data, f, indent=2, ensure_ascii=False)
    
    return filename

def load_search_config_from_file(config_file: str) -> SearchConfig:
    """Load search configuration from JSON file."""
    with open(config_file, 'r', encoding='utf-8') as f:
        config_data = json.load(f)
    
    return SearchConfig(**config_data)

def create_sample_config(filename: str = "search_config.json"):
    """Create a sample search configuration file."""
    sample_config = {
        "subreddits": [
            "entrepreneur",
            "smallbusiness",
            "startups",
            "marketing"
        ],
        "keywords": [
            "need help with",
            "looking for",
            "struggling with",
            "advice needed",
            "recommendations",
            "freelancer",
            "consultant"
        ],
        "max_results": 50,
        "time_filter": "week",
        "sort": "hot",
        "min_score": 2,
        "exclude_keywords": [
            "spam",
            "scam",
            "free"
        ]
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(sample_config, f, indent=2)
    
    print(f"Sample configuration created: {filename}")
    return filename

def main():
    """Main function for command line usage."""
    parser = argparse.ArgumentParser(description='Find Reddit leads based on keywords')
    parser.add_argument('--config', '-c', help='Path to search configuration JSON file')
    parser.add_argument('--output', '-o', help='Output filename for leads')
    parser.add_argument('--create-config', action='store_true', help='Create sample configuration file')
    parser.add_argument('--subreddits', nargs='+', help='Subreddits to search (space separated)')
    parser.add_argument('--keywords', nargs='+', help='Keywords to search for (space separated)')
    parser.add_argument('--max-results', type=int, default=50, help='Maximum number of results')
    
    args = parser.parse_args()
    
    if args.create_config:
        create_sample_config()
        return
    
    # Initialize Reddit configuration
    reddit_config = RedditConfig.from_env()
    if not reddit_config.client_id or not reddit_config.client_secret:
        print("Error: Reddit API credentials not found in environment variables")
        print("Please set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET")
        return
    
    # Load or create search configuration
    if args.config:
        search_config = load_search_config_from_file(args.config)
    elif args.subreddits and args.keywords:
        search_config = SearchConfig(
            subreddits=args.subreddits,
            keywords=args.keywords,
            max_results=args.max_results
        )
    else:
        print("Error: Either provide --config file or --subreddits and --keywords")
        print("Use --create-config to create a sample configuration file")
        return
    
    # Find leads
    print(f"Searching for leads in subreddits: {', '.join(search_config.subreddits)}")
    print(f"Keywords: {', '.join(search_config.keywords)}")
    
    finder = RedditLeadFinder(reddit_config)
    leads = finder.find_leads(search_config)
    
    print(f"\nFound {len(leads)} potential leads:")
    
    # Display results
    for i, lead in enumerate(leads[:10], 1):  # Show first 10
        print(f"\n{i}. {lead.title}")
        print(f"   Subreddit: r/{lead.subreddit}")
        print(f"   Author: u/{lead.author}")
        print(f"   Score: {lead.score}")
        print(f"   Keywords matched: {', '.join(lead.matched_keywords)}")
        print(f"   URL: {lead.url}")
        if lead.body and len(lead.body) > 100:
            print(f"   Preview: {lead.body[:100]}...")
    
    if len(leads) > 10:
        print(f"\n... and {len(leads) - 10} more leads")
    
    # Save to file
    output_file = save_leads_to_file(leads, args.output)
    print(f"\nAll leads saved to: {output_file}")

if __name__ == "__main__":
    main()