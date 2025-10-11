"""Configuration for Reddit lead generation."""
import os
from typing import List, Dict, Any
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class RedditConfig:
    """Reddit API configuration."""
    client_id: str
    client_secret: str
    user_agent: str
    
    @classmethod
    def from_env(cls) -> 'RedditConfig':
        """Create config from environment variables."""
        return cls(
            client_id=os.getenv('REDDIT_CLIENT_ID', ''),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET', ''),
            user_agent=os.getenv('REDDIT_USER_AGENT', 'LeadBot/1.0')
        )

@dataclass
class SearchConfig:
    """Search configuration for finding leads."""
    subreddits: List[str]
    keywords: List[str]
    max_results: int = 50
    time_filter: str = 'week'  # hour, day, week, month, year, all
    sort: str = 'hot'  # hot, new, top, rising
    min_score: int = 1
    exclude_keywords: List[str] = None
    
    def __post_init__(self):
        if self.exclude_keywords is None:
            self.exclude_keywords = []