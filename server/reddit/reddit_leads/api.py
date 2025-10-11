"""API interface for Reddit lead generation."""
from typing import List, Dict, Any, Optional
from .config import RedditConfig, SearchConfig
from .lead_finder import RedditLeadFinder, Lead

class RedditLeadsAPI:
    """API wrapper for Reddit lead generation."""
    
    def __init__(self):
        """Initialize with Reddit configuration from environment."""
        self.reddit_config = RedditConfig.from_env()
        self.finder = RedditLeadFinder(self.reddit_config)
    
    def search_leads(
        self,
        subreddits: List[str],
        keywords: List[str],
        max_results: int = 50,
        time_filter: str = 'week',
        sort: str = 'hot',
        min_score: int = 1,
        exclude_keywords: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Search for leads with specified parameters.
        
        Args:
            subreddits: List of subreddit names (without r/)
            keywords: List of keywords to search for
            max_results: Maximum number of results to return
            time_filter: Time filter for search (hour, day, week, month, year, all)
            sort: Sort method (hot, new, top, rising)
            min_score: Minimum score for posts/comments
            exclude_keywords: Keywords to exclude from results
        
        Returns:
            Dictionary with search results and metadata
        """
        search_config = SearchConfig(
            subreddits=subreddits,
            keywords=keywords,
            max_results=max_results,
            time_filter=time_filter,
            sort=sort,
            min_score=min_score,
            exclude_keywords=exclude_keywords or []
        )
        
        try:
            leads = self.finder.find_leads(search_config)
            
            return {
                'success': True,
                'total_leads': len(leads),
                'search_config': {
                    'subreddits': subreddits,
                    'keywords': keywords,
                    'max_results': max_results,
                    'time_filter': time_filter,
                    'sort': sort,
                    'min_score': min_score,
                    'exclude_keywords': exclude_keywords or []
                },
                'leads': [lead.to_dict() for lead in leads]
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'leads': []
            }
    
    def get_user_info(self, username: str) -> Dict[str, Any]:
        """Get information about a Reddit user."""
        return self.finder.get_user_info(username)
    
    def filter_leads(
        self,
        leads: List[Dict[str, Any]],
        min_score: Optional[int] = None,
        max_age_days: Optional[int] = None,
        required_keywords: Optional[List[str]] = None,
        exclude_authors: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Filter existing leads based on additional criteria.
        
        Args:
            leads: List of lead dictionaries
            min_score: Minimum score threshold
            max_age_days: Maximum age in days
            required_keywords: Keywords that must be present
            exclude_authors: Authors to exclude
        
        Returns:
            Filtered list of leads
        """
        filtered_leads = []
        
        for lead in leads:
            # Check minimum score
            if min_score is not None and lead.get('score', 0) < min_score:
                continue
            
            # Check age
            if max_age_days is not None:
                from datetime import datetime, timedelta
                created_time = datetime.fromtimestamp(lead.get('created_utc', 0))
                if datetime.now() - created_time > timedelta(days=max_age_days):
                    continue
            
            # Check required keywords
            if required_keywords:
                text = f"{lead.get('title', '')} {lead.get('body', '')}".lower()
                if not any(keyword.lower() in text for keyword in required_keywords):
                    continue
            
            # Check excluded authors
            if exclude_authors and lead.get('author') in exclude_authors:
                continue
            
            filtered_leads.append(lead)
        
        return filtered_leads