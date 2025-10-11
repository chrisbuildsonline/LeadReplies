# X (Twitter) Lead Scraper

A powerful tool for finding potential leads on X (Twitter) using keyword-based searches with snscrape.

## Features

- 🔍 **Keyword-based search** - Find tweets containing specific marketing-related keywords
- 📊 **Smart scoring** - Confidence and hotness scores based on engagement, recency, and content quality
- 🎯 **Advanced filtering** - Filter by engagement, age, content quality, and exclude spam
- 🔄 **Continuous monitoring** - Real-time monitoring for new leads
- 💾 **JSON export** - Save results in structured format for further analysis
- 📈 **Analytics** - Detailed statistics on keywords, hashtags, and engagement

## Installation

1. Install required dependencies:
```bash
cd server/x
pip install -r requirements.txt
```

2. Install snscrape (if not already installed):
```bash
pip install snscrape
```

## Quick Start

### Basic Search
Search for leads using configured keywords:
```bash
python run_x_scraper.py search
```

### Search Specific Keyword
Search for a specific keyword or phrase:
```bash
python run_x_scraper.py search "How do I market myself"
```

### Continuous Monitoring
Start real-time monitoring for new leads:
```bash
python run_x_scraper.py monitor
```

### View Configuration
Check current settings:
```bash
python run_x_scraper.py config
```

## Configuration

Edit `scraper_config.py` to customize:

### Keywords
Add marketing-related keywords to search for:
```python
KEYWORDS = [
    "how do I market myself",
    "marketing help", 
    "need marketing advice",
    "promote my business",
    # Add more keywords...
]
```

### Search Parameters
```python
SEARCH_CONFIG = {
    "days_back": 7,      # How many days to look back
    "limit": 200,        # Maximum tweets to check
    "min_likes": 0,      # Minimum likes required
    "include_replies": True,    # Include reply tweets
    "include_retweets": False,  # Include retweets
}
```

### Filtering Options
```python
FILTER_CONFIG = {
    "min_confidence": 0.2,     # Minimum confidence score (0-1)
    "min_hotness": 5,          # Minimum hotness score
    "min_engagement": 1,       # Minimum total engagement
    "max_age_hours": 168,      # Maximum tweet age (7 days)
    "exclude_keywords": [...], # Keywords to exclude
}
```

## Output Format

Results are saved as JSON with the following structure:

```json
{
  "metadata": {
    "timestamp": "2025-09-24T...",
    "total_leads": 45,
    "keywords_used": [...],
    "platform": "X (Twitter)"
  },
  "leads": [
    {
      "id": "tweet_id",
      "url": "https://twitter.com/user/status/...",
      "content": "Tweet content...",
      "user": "Display Name",
      "username": "username",
      "created_date": "2025-09-24T...",
      "like_count": 5,
      "retweet_count": 2,
      "reply_count": 1,
      "hashtags": ["marketing", "help"],
      "keywords_matched": ["marketing help"],
      "confidence_score": 0.75,
      "hotness_score": 12.5,
      "engagement_total": 8
    }
  ]
}
```

## Scoring System

### Confidence Score (0-1)
Based on:
- **Keyword matching** (30%) - How well keywords match the content
- **Engagement** (20%) - Likes, retweets, replies
- **Recency** (20%) - How recent the tweet is
- **User activity** (15%) - User's general engagement patterns
- **Content quality** (15%) - Quality indicators in the content

### Hotness Score
Combines engagement metrics with recency decay:
- Higher engagement = higher score
- Recent tweets get boosted
- Older tweets lose hotness over time

## Advanced Usage

### Custom Search Queries
You can modify the search logic in `x_scraper.py` to use advanced Twitter search operators:

```python
# Example: Search for questions only
query = f"({' OR '.join(keywords)}) ?"

# Example: Exclude retweets
query = f"({' OR '.join(keywords)}) -filter:retweets"

# Example: Only from verified accounts
query = f"({' OR '.join(keywords)}) filter:verified"
```

### Monitoring Mode
The monitoring mode checks for new tweets every 15 minutes (configurable) and saves results automatically:

```python
MONITORING_CONFIG = {
    "interval_minutes": 15,
    "days_back": 1,
    "save_to_file": True,
    "max_tweets_per_check": 100
}
```

## Tips for Better Results

1. **Use specific keywords** - "marketing help" works better than just "marketing"
2. **Include question indicators** - Tweets with "?" often indicate people seeking help
3. **Monitor regularly** - Fresh leads are more valuable
4. **Adjust confidence thresholds** - Start with 0.2 and adjust based on results
5. **Check hashtags** - Popular hashtags can indicate trending topics

## Troubleshooting

### Rate Limiting
If you encounter rate limiting:
- Reduce the `limit` in `SEARCH_CONFIG`
- Increase `interval_minutes` in monitoring mode
- Use more specific keywords to get fewer but better results

### No Results
If you're not getting results:
- Check if keywords are too specific
- Reduce `min_confidence` threshold
- Increase `days_back` to search further back
- Verify snscrape is working: `python -c "import snscrape.modules.twitter"`

### Installation Issues
If snscrape installation fails:
```bash
# Try installing from git
pip install git+https://github.com/JustAnotherArchivist/snscrape.git

# Or use specific version
pip install snscrape==0.7.0
```

## Example Workflow

1. **Configure keywords** for your target market
2. **Run initial search** to test and tune settings
3. **Adjust filters** based on result quality
4. **Start monitoring** for continuous lead generation
5. **Export results** for your CRM or outreach tools

## Integration

The JSON output can be easily integrated with:
- CRM systems (Salesforce, HubSpot, etc.)
- Email marketing tools
- Lead scoring systems
- Analytics dashboards
- Automated outreach tools

## Legal & Ethical Considerations

- Respect Twitter's Terms of Service
- Don't spam or harass users
- Use leads for legitimate business purposes
- Consider privacy and data protection laws
- Be transparent in your outreach