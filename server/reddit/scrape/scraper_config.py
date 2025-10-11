"""
Configuration file for Reddit scraper.
Customize these settings for your specific needs.
"""

# Keywords to search for (add/remove as needed)
KEYWORDS = [
    # SaaS & Business Tools
    "SaaS", "software as a service", "B2B software", "business tool",
    "marketing automation", "CRM", "customer relationship management",
    "email automation", "drip campaign", "email sequence",
    "lead generation", "customer acquisition", "growth hacking",
    
    # Marketing & Analytics
    "marketing tool", "analytics", "tracking", "conversion optimization",
    "A/B testing", "funnel optimization", "user engagement",
    "customer retention", "churn reduction",
    
    # Specific Pain Points
    "struggling with", "need help with", "looking for", "recommend",
    "alternative to", "better than", "replacement for",
    "automate", "streamline", "efficiency", "productivity"
]

# Subreddits to monitor (without the 'r/' prefix)
SUBREDDITS = [
    # Business & Entrepreneurship
    "entrepreneur", "startups", "smallbusiness", "business",
    "EntrepreneurRideAlong", "sweatystartup",
    
    # Marketing & Sales
    "marketing", "digitalmarketing", "emailmarketing", "sales",
    "PPC", "SEO", "socialmedia", "content_marketing",
    
    # Tech & SaaS
    "SaaS", "webdev", "programming", "technology",
    "digitalnomad", "remotework",
    
    # Industry Specific
    "ecommerce", "shopify", "amazon", "dropshipping",
    "realestate", "investing", "personalfinance"
]

# Search parameters
SEARCH_CONFIG = {
    "days_back": 4,  # How many days to look back
    "limit": 1000,   # Maximum posts/comments to check per search
    "min_score": 1,  # Minimum upvote score for posts/comments
    "min_comments": 0,  # Minimum number of comments for posts
}

# Continuous monitoring settings
MONITORING_CONFIG = {
    "interval_minutes": 5,  # How often to check for new content
    "days_back": 1,         # Only check content from last N days
    "save_to_file": True,   # Save results to JSON file
    "notify_on_leads": True # Print notifications when leads found
}

# Filtering settings
FILTER_CONFIG = {
    # Exclude posts/comments containing these terms
    "exclude_keywords": [
        "[deleted]", "[removed]", "spam", "advertisement",
        "self-promotion", "affiliate link"
    ],
    
    # Minimum confidence score (0.0 to 1.0)
    "min_confidence": 0.1,
    
    # Minimum hotness score
    "min_hotness": 10
}

# Output settings
OUTPUT_CONFIG = {
    "output_file": "scraping_leads.json",
    "max_content_length": 500,  # Truncate content to this length
    "include_raw_data": True,   # Include raw Reddit data in output
    "sort_by": "hotness_score"  # Sort results by this field
}