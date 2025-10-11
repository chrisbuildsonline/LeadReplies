# Reddit Leads Finder

A Python package for finding potential leads on Reddit based on keywords and subreddits using PRAW (Python Reddit API Wrapper).

## Features

- Search multiple subreddits for posts and comments
- Keyword-based filtering with exclude keywords
- Configurable search parameters (time filter, sort method, minimum score)
- User profile research
- Export results to JSON
- Command-line interface and Python API

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up Reddit API credentials in your `.env` file:
```
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=YourApp/1.0
```

## Usage

### Command Line Interface

1. Create a sample configuration:
```bash
python -m reddit_leads.main --create-config
```

2. Search using configuration file:
```bash
python -m reddit_leads.main --config search_config.json --output my_leads.json
```

3. Quick search with parameters:
```bash
python -m reddit_leads.main --subreddits entrepreneur startups --keywords "need help" "looking for" --max-results 25
```

### Python API

```python
from reddit_leads.api import RedditLeadsAPI

# Initialize API
api = RedditLeadsAPI()

# Search for leads
results = api.search_leads(
    subreddits=['entrepreneur', 'smallbusiness'],
    keywords=['need help with', 'looking for advice'],
    max_results=50,
    min_score=2
)

# Process results
if results['success']:
    for lead in results['leads']:
        print(f"Title: {lead['title']}")
        print(f"Subreddit: r/{lead['subreddit']}")
        print(f"Score: {lead['score']}")
        print(f"URL: {lead['url']}")
        print("---")
```

## Configuration Options

### SearchConfig Parameters

- `subreddits`: List of subreddit names (without r/)
- `keywords`: List of keywords to search for
- `max_results`: Maximum number of results (default: 50)
- `time_filter`: Time filter - 'hour', 'day', 'week', 'month', 'year', 'all' (default: 'week')
- `sort`: Sort method - 'hot', 'new', 'top', 'rising' (default: 'hot')
- `min_score`: Minimum score for posts/comments (default: 1)
- `exclude_keywords`: Keywords to exclude from results

### Example Configuration File

```json
{
  "subreddits": ["entrepreneur", "smallbusiness", "startups"],
  "keywords": ["need help with", "looking for", "advice needed"],
  "max_results": 50,
  "time_filter": "week",
  "sort": "hot",
  "min_score": 2,
  "exclude_keywords": ["spam", "scam", "free only"]
}
```

## Lead Data Structure

Each lead contains:
- `id`: Reddit post/comment ID
- `title`: Post title or comment context
- `body`: Post/comment content
- `author`: Reddit username
- `subreddit`: Subreddit name
- `url`: Direct URL to content
- `permalink`: Reddit permalink
- `score`: Upvote score
- `num_comments`: Number of comments (posts only)
- `created_utc`: Creation timestamp
- `matched_keywords`: Keywords that matched
- `is_comment`: Whether it's a comment or post
- `parent_id`: Parent post ID (for comments)

## Best Practices

1. **Respect Reddit's API limits**: Don't make too many requests too quickly
2. **Use specific keywords**: More specific keywords yield better quality leads
3. **Filter by score**: Higher scored posts/comments are more visible
4. **Check user profiles**: Research potential leads before reaching out
5. **Be genuine**: Provide real value when engaging with leads
6. **Follow subreddit rules**: Each subreddit has its own posting guidelines

## Examples

See `example_usage.py` for detailed usage examples including:
- Basic lead search
- Advanced filtering
- User profile research
- Saving results to files