# Reddit Lead Scraper - Enhanced Version

A powerful Reddit scraper that uses only JSON endpoints (no API keys required) to find leads based on keywords, specific subreddits, and customizable time ranges.

## Features

✅ **Customizable Days Lookback** - Search posts/comments from the last N days  
✅ **Specific Subreddit Targeting** - Focus on relevant communities  
✅ **Keyword Filtering** - Find content matching your target keywords  
✅ **JSON-Only Approach** - No API keys or rate limits  
✅ **Continuous Monitoring** - Real-time lead detection  
✅ **Smart Filtering** - Remove low-quality content  
✅ **Detailed Analytics** - Keyword and subreddit statistics  

## Quick Start

### 1. Basic Search
```python
from reddit_scrape import search_reddit_leads

leads = search_reddit_leads(
    keywords=["SaaS", "marketing tool", "CRM"],
    subreddits=["entrepreneur", "startups", "marketing"],
    days_back=4,  # Look back 4 days
    limit=1000
)

print(f"Found {len(leads)} leads!")
```

### 2. Using the Configuration File
Edit `scraper_config.py` to customize your search parameters, then run:

```bash
# Single search
python run_scraper.py search

# Continuous monitoring
python run_scraper.py monitor

# Show current config
python run_scraper.py config
```

### 3. Advanced Usage
```python
from reddit_scrape import RedditScrapingLeadFinder

finder = RedditScrapingLeadFinder()

# Custom search with date filtering
leads = finder.search_leads(
    keywords=["email automation", "drip campaign"],
    subreddits=["marketing", "entrepreneur"],
    limit=500,
    days_back=7  # Last 7 days only
)

# Continuous monitoring
finder.monitor_continuous(
    keywords=["SaaS", "B2B software"],
    subreddits=["startups", "entrepreneur"],
    interval_minutes=5,
    days_back=1,  # Only check last 24 hours
    callback=lambda leads: print(f"Found {len(leads)} new leads!")
)
```

## Configuration Options

### Keywords
Add relevant keywords to find your target audience:
```python
KEYWORDS = [
    "SaaS", "marketing automation", "CRM",
    "struggling with", "need help with", "looking for",
    "alternative to", "better than"
]
```

### Subreddits
Target specific communities:
```python
SUBREDDITS = [
    "entrepreneur", "startups", "marketing", "SaaS",
    "smallbusiness", "webdev", "digitalnomad"
]
```

### Search Parameters
```python
SEARCH_CONFIG = {
    "days_back": 4,     # How many days to look back
    "limit": 1000,      # Max posts/comments to check
    "min_score": 1,     # Minimum upvotes
    "min_comments": 0   # Minimum comments for posts
}
```

## Output Format

Each lead contains:
```json
{
  "id": "post_abc123",
  "title": "Looking for a good CRM solution",
  "content": "We're a small startup and need...",
  "url": "https://reddit.com/r/entrepreneur/comments/...",
  "author": "username",
  "subreddit": "entrepreneur",
  "type": "post",
  "hotness_score": 85,
  "keywords_matched": ["CRM", "startup"],
  "created_date": "2025-09-23T10:30:00",
  "confidence_score": 0.67,
  "upvotes": 15,
  "num_comments": 8
}
```

## Examples

### Example 1: SaaS Lead Generation
```python
# Look for SaaS opportunities in the last 4 days
leads = search_reddit_leads(
    keywords=[
        "SaaS", "software solution", "business tool",
        "automate", "streamline", "efficiency"
    ],
    subreddits=[
        "entrepreneur", "startups", "smallbusiness", 
        "SaaS", "webdev"
    ],
    days_back=4,
    limit=1000
)
```

### Example 2: Marketing Tool Leads
```python
# Find people looking for marketing tools
leads = search_reddit_leads(
    keywords=[
        "email marketing", "marketing automation", 
        "lead generation", "CRM", "analytics"
    ],
    subreddits=[
        "marketing", "digitalmarketing", "entrepreneur",
        "smallbusiness", "ecommerce"
    ],
    days_back=7,
    limit=500
)
```

### Example 3: Continuous Monitoring
```python
# Monitor for new opportunities every 5 minutes
finder = RedditScrapingLeadFinder()

def handle_leads(new_leads):
    print(f"🚨 {len(new_leads)} new leads found!")
    # Send email, Slack notification, etc.

finder.monitor_continuous(
    keywords=["looking for", "need help", "recommend"],
    subreddits=["entrepreneur", "startups"],
    interval_minutes=5,
    days_back=1,
    callback=handle_leads
)
```

## Files

- `reddit_scrape.py` - Main scraper class
- `scraper_config.py` - Configuration settings
- `run_scraper.py` - Command-line interface
- `example_usage.py` - Usage examples
- `README.md` - This file

## Tips for Better Results

1. **Use specific keywords** - "email automation" vs "email"
2. **Target relevant subreddits** - Focus on communities where your audience hangs out
3. **Adjust days_back** - Recent posts (1-4 days) often have more engaged users
4. **Monitor continuously** - Catch opportunities as they happen
5. **Filter by engagement** - Higher upvotes/comments = more active discussions

## Legal & Ethical Usage

- Only scrape public Reddit data
- Respect rate limits (built-in delays)
- Don't spam or self-promote excessively
- Follow Reddit's terms of service
- Use data responsibly

## Troubleshooting

**No leads found?**
- Check if keywords are too specific
- Verify subreddit names (no 'r/' prefix)
- Increase days_back or limit values

**Rate limited?**
- Built-in delays should prevent this
- If it happens, the scraper will automatically retry

**Want more leads?**
- Add more relevant keywords
- Include more subreddits
- Increase the limit parameter
- Extend days_back range