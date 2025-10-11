"""Reddit lead finder using PRAW."""
import praw
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from .config import RedditConfig, SearchConfig

@dataclass
class Lead:
    """Represents a potential lead from Reddit."""
    id: str
    title: str
    body: str
    author: str
    subreddit: str
    url: str
    permalink: str
    score: int
    num_comments: int
    created_utc: float
    matched_keywords: List[str]
    is_comment: bool = False
    parent_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

class RedditLeadFinder:
    """Find leads on Reddit based on keywords and subreddits."""
    
    def __init__(self, reddit_config: RedditConfig):
        """Initialize with Reddit configuration."""
        self.reddit = praw.Reddit(
            client_id=reddit_config.client_id,
            client_secret=reddit_config.client_secret,
            user_agent=reddit_config.user_agent
        )
    
    def find_leads(self, search_config: SearchConfig) -> List[Lead]:
        """Find leads based on search configuration."""
        leads = []
        
        for subreddit_name in search_config.subreddits:
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                
                # Search posts
                post_leads = self._search_posts(subreddit, search_config)
                leads.extend(post_leads)
                
                # Search comments in recent posts
                comment_leads = self._search_comments(subreddit, search_config)
                leads.extend(comment_leads)
                
            except Exception as e:
                print(f"Error searching subreddit {subreddit_name}: {e}")
                continue
        
        # Remove duplicates and sort by score
        unique_leads = {lead.id: lead for lead in leads}
        sorted_leads = sorted(unique_leads.values(), key=lambda x: x.score, reverse=True)
        
        return sorted_leads[:search_config.max_results]
    
    def _search_posts(self, subreddit, search_config: SearchConfig) -> List[Lead]:
        """Search posts in a subreddit."""
        leads = []
        
        try:
            # Get posts based on sort method
            if search_config.sort == 'hot':
                posts = subreddit.hot(limit=100)
            elif search_config.sort == 'new':
                posts = subreddit.new(limit=100)
            elif search_config.sort == 'top':
                posts = subreddit.top(time_filter=search_config.time_filter, limit=100)
            elif search_config.sort == 'rising':
                posts = subreddit.rising(limit=100)
            else:
                posts = subreddit.hot(limit=100)
            
            for post in posts:
                if post.score < search_config.min_score:
                    continue
                
                # Check if post matches keywords
                matched_keywords = self._check_keywords(
                    f"{post.title} {post.selftext}",
                    search_config.keywords,
                    search_config.exclude_keywords
                )
                
                if matched_keywords:
                    lead = Lead(
                        id=post.id,
                        title=post.title,
                        body=post.selftext,
                        author=str(post.author) if post.author else '[deleted]',
                        subreddit=str(post.subreddit),
                        url=post.url,
                        permalink=f"https://reddit.com{post.permalink}",
                        score=post.score,
                        num_comments=post.num_comments,
                        created_utc=post.created_utc,
                        matched_keywords=matched_keywords,
                        is_comment=False
                    )
                    leads.append(lead)
        
        except Exception as e:
            print(f"Error searching posts: {e}")
        
        return leads
    
    def _search_comments(self, subreddit, search_config: SearchConfig) -> List[Lead]:
        """Search comments in recent posts."""
        leads = []
        
        try:
            # Get recent posts to search their comments
            recent_posts = list(subreddit.new(limit=20))
            
            for post in recent_posts:
                try:
                    post.comments.replace_more(limit=0)  # Remove "more comments"
                    
                    for comment in post.comments.list():
                        if comment.score < search_config.min_score:
                            continue
                        
                        # Check if comment matches keywords
                        matched_keywords = self._check_keywords(
                            comment.body,
                            search_config.keywords,
                            search_config.exclude_keywords
                        )
                        
                        if matched_keywords:
                            lead = Lead(
                                id=comment.id,
                                title=f"Comment on: {post.title}",
                                body=comment.body,
                                author=str(comment.author) if comment.author else '[deleted]',
                                subreddit=str(post.subreddit),
                                url=f"https://reddit.com{comment.permalink}",
                                permalink=comment.permalink,
                                score=comment.score,
                                num_comments=0,
                                created_utc=comment.created_utc,
                                matched_keywords=matched_keywords,
                                is_comment=True,
                                parent_id=post.id
                            )
                            leads.append(lead)
                
                except Exception as e:
                    print(f"Error processing comments for post {post.id}: {e}")
                    continue
        
        except Exception as e:
            print(f"Error searching comments: {e}")
        
        return leads
    
    def _check_keywords(self, text: str, keywords: List[str], exclude_keywords: List[str]) -> List[str]:
        """Check if text contains keywords and doesn't contain exclude keywords."""
        if not text:
            return []
        
        text_lower = text.lower()
        
        # Check exclude keywords first
        for exclude_keyword in exclude_keywords:
            if exclude_keyword.lower() in text_lower:
                return []
        
        # Check for matching keywords
        matched = []
        for keyword in keywords:
            if keyword.lower() in text_lower:
                matched.append(keyword)
        
        return matched
    
    def get_user_info(self, username: str) -> Dict[str, Any]:
        """Get information about a Reddit user."""
        try:
            user = self.reddit.redditor(username)
            return {
                'name': user.name,
                'comment_karma': user.comment_karma,
                'link_karma': user.link_karma,
                'created_utc': user.created_utc,
                'is_verified': user.verified if hasattr(user, 'verified') else False,
                'has_premium': user.is_gold if hasattr(user, 'is_gold') else False
            }
        except Exception as e:
            return {'error': str(e)}