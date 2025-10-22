# Reddit Keyword Scraping - Scaling Guide

## Current Implementation Analysis

Your F5Bot Reddit scraper has been optimized to handle large keyword lists efficiently. Here's what you need to know:

## Keyword Limits & Best Practices

### Reddit API Limitations
- **URL Length Limit**: ~2000 characters maximum
- **Query Complexity**: Reddit may timeout on overly complex queries
- **Rate Limits**: 60 requests per minute (your scraper handles this automatically)
- **Results per Request**: 100 posts maximum

### Optimal Batching Strategy

Your scraper now automatically splits keywords into optimal batches:

- **Batch Size**: 10-12 keywords per batch
- **Query Length**: Max 1800 characters per query (conservative limit)
- **Automatic Splitting**: Handles any number of keywords

### Performance Estimates

| Keywords | Batches | API Requests | Estimated Time |
|----------|---------|--------------|----------------|
| 50       | 4-5     | 8-10         | ~45 seconds    |
| 100      | 8-9     | 16-18        | ~1.5 minutes   |
| 200      | 17-18   | 34-36        | ~3 minutes     |
| 500      | 42-43   | 84-86        | ~7 minutes     |

## How It Works

### 1. Automatic Batching
```python
# Your scraper automatically splits large keyword lists
keywords = ["keyword1", "keyword2", ..., "keyword100"]
scraper = F5BotRedditScraper()
results = scraper.search_reddit_for_keywords(keywords, limit=100)
```

### 2. Smart Query Building
Each batch creates optimized queries like:
```
("keyword1" OR "keyword2" OR "keyword3" OR ... OR "keyword12")
```

### 3. Rate Limit Protection
- Built-in delays: 3-7 seconds between requests
- Exponential backoff on rate limits
- User agent rotation
- Conservative request timing

## Recommendations by Scale

### Small Scale (1-50 keywords)
- **Single Session**: Run normally
- **Time Filter**: Use 'week' or 'month'
- **Expected Results**: 50-200 leads

### Medium Scale (50-150 keywords)
- **Single Session**: Works well
- **Time Filter**: Use 'week' for recent content
- **Expected Results**: 100-500 leads
- **Runtime**: 1-3 minutes

### Large Scale (150-500 keywords)
- **Consider Multiple Sessions**: Split by business/category
- **Time Filter**: Use 'week' to avoid overwhelming results
- **Expected Results**: 200-1000+ leads
- **Runtime**: 3-10 minutes

### Enterprise Scale (500+ keywords)
- **Multiple Sessions**: Definitely split by business/category
- **Stagger Runs**: Run different batches at different times
- **Time Filter**: Use 'day' or 'week' only
- **Monitor**: Watch for rate limits and adjust

## Configuration Options

### Environment Variables
```bash
# In your .env file
SCRAPING_INTERVAL_MINUTES=120  # How often to run
```

### Scraper Settings
```python
# In f5bot_reddit_scraper.py
max_keywords_per_batch = 12    # Keywords per API request
max_query_length = 1800        # Max URL length
min_delay = 3                  # Minimum delay between requests
max_delay = 7                  # Maximum delay between requests
```

## Testing Your Setup

Run the test script to see how your keywords will be batched:
```bash
cd server
python3 test_keyword_batching.py
```

## Monitoring & Troubleshooting

### Signs of Rate Limiting
- HTTP 429 responses
- Sudden drop in results
- Timeout errors

### Solutions
- Increase delays between requests
- Reduce batch sizes
- Use longer time filters
- Split into multiple sessions

### Logs to Watch
```bash
tail -f server/background_service.log
```

Look for:
- "Rate limited (429)" - Increase delays
- "Batch X failed" - Reduce batch size
- "Found 0 posts" - Check keywords or time filter

## Best Practices Summary

1. **Start Small**: Test with 20-50 keywords first
2. **Monitor Performance**: Watch logs and response times
3. **Use Time Filters**: 'week' or 'month' for most cases
4. **Batch Intelligently**: Let the scraper handle batching automatically
5. **Respect Rate Limits**: Don't modify delay settings unless necessary
6. **Split by Business**: For 200+ keywords, consider separate runs per business

## Example Usage

```python
# Your current usage works with any number of keywords
from f5bot_reddit_scraper import search_reddit_leads_efficient

# This automatically handles batching for 100+ keywords
keywords = ["saas", "crm", "project management", ...] # 100+ keywords
leads = search_reddit_leads_efficient(
    keywords=keywords,
    days_back=7,
    limit=200
)

print(f"Found {len(leads)} leads from {len(keywords)} keywords")
```

The scraper will automatically:
- Split keywords into optimal batches
- Handle rate limiting
- Combine and deduplicate results
- Return the best matches first

## Need Help?

If you're seeing issues with large keyword lists:
1. Check the logs for rate limiting
2. Reduce batch size in the scraper settings
3. Increase delays between requests
4. Consider splitting keywords by business category