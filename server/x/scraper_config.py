"""
Configuration file for X (Twitter) scraper.
Customize these settings for your specific needs.
"""

# Keywords to search for (add/remove as needed)
KEYWORDS = [
    # Marketing & Self-Promotion
    "how do I market myself", "marketing help", "need marketing advice",
    "promote my business", "get more customers", "increase sales",
    "build my brand", "personal branding", "social media marketing",
    
    # Business Growth
    "grow my business", "startup marketing", "small business marketing",
    "digital marketing tips", "marketing strategy", "customer acquisition",
    "lead generation", "conversion optimization", "sales funnel",
    
    # Specific Pain Points
    "struggling with marketing", "marketing budget", "marketing tools",
    "marketing automation", "email marketing", "content marketing",
    "SEO help", "social media strategy", "advertising help",
    
    # Questions & Requests
    "recommend marketing", "best marketing", "marketing advice",
    "how to promote", "marketing consultant", "marketing agency",
    "marketing course", "learn marketing", "marketing tips"
]

# Search parameters
SEARCH_CONFIG = {
    "days_back": 7,      # How many days to look back
    "limit": 200,        # Maximum tweets to check per search
    "min_likes": 0,      # Minimum likes for tweets
    "min_retweets": 0,   # Minimum retweets for tweets
    "include_replies": True,    # Include reply tweets
    "include_retweets": False,  # Include retweets (usually less valuable)
}

# Continuous monitoring settings
MONITORING_CONFIG = {
    "interval_minutes": 15,  # How often to check for new content
    "days_back": 1,          # Only check content from last N days
    "save_to_file": True,    # Save results to JSON file
    "notify_on_leads": True, # Print notifications when leads found
    "max_tweets_per_check": 100  # Limit tweets per monitoring cycle
}

# Filtering settings
FILTER_CONFIG = {
    # Exclude tweets containing these terms
    "exclude_keywords": [
        "spam", "bot", "fake", "scam", "advertisement", "ad",
        "affiliate", "promo code", "discount code", "buy now",
        "click here", "limited time", "act now"
    ],
    
    # Exclude tweets from these usernames (bots, spam accounts)
    "exclude_users": [
        "bot", "spam", "promo", "deal", "offer"
    ],
    
    # Minimum confidence score (0.0 to 1.0)
    "min_confidence": 0.2,
    
    # Minimum hotness score
    "min_hotness": 5,
    
    # Minimum engagement (likes + retweets + replies)
    "min_engagement": 1,
    
    # Maximum tweet age in hours
    "max_age_hours": 168  # 7 days
}

# Output settings
OUTPUT_CONFIG = {
    "output_file": "x_scraping_leads.json",
    "max_content_length": 280,  # Twitter's character limit
    "include_raw_data": True,   # Include raw tweet data in output
    "sort_by": "hotness_score", # Sort results by this field
    "include_hashtags": True,   # Include hashtag analysis
    "include_mentions": True    # Include mention analysis
}

# Advanced search configurations
ADVANCED_SEARCH = {
    # Language filter (None for all languages, 'en' for English only)
    "language": "en",
    
    # Geographic filters (None for worldwide)
    "geocode": None,  # Format: "latitude,longitude,radius" e.g., "37.781157,-122.398720,1mi"
    
    # Result type filter
    "result_type": "mixed",  # Options: "recent", "popular", "mixed"
    
    # Additional search operators
    "exclude_retweets": True,  # Exclude retweets from results
    "verified_only": False,    # Only include verified accounts
    "min_followers": None,     # Minimum follower count (None for no limit)
}

# Scoring weights for confidence calculation
SCORING_WEIGHTS = {
    "keyword_match": 0.3,      # How well keywords match
    "engagement": 0.2,         # Likes, retweets, replies
    "recency": 0.2,           # How recent the tweet is
    "user_activity": 0.15,    # User's general activity level
    "content_quality": 0.15   # Quality indicators in content
}

# Content quality indicators
QUALITY_INDICATORS = {
    "positive": [
        "?", "help", "advice", "recommend", "suggest", "tips",
        "how to", "best way", "looking for", "need", "want"
    ],
    "negative": [
        "!!!", "BUY NOW", "LIMITED TIME", "CLICK HERE", "FREE",
        "GUARANTEED", "AMAZING", "INCREDIBLE", "UNBELIEVABLE"
    ]
}