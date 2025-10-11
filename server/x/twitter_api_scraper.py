#!/usr/bin/env python3
"""
Twitter API v2 scraper for lead generation.
Requires Twitter API credentials but provides reliable access.
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests
from dataclasses import dataclass


@dataclass
class TwitterLead:
    """Data class for Twitter lead information."""
    id: str
    text: str
    author_id: str
    username: str
    created_at: datetime
    public_metrics: Dict
    url: str


class TwitterAPILeadFinder:
    """Lead finder using official Twitter API v2."""
    
    def __init__(self, bearer_token: str = None):
        """
        Initialize with Twitter API credentials.
        
        Args:
            bearer_token: Twitter API Bearer Token
        """
        self.bearer_token = bearer_token or os.getenv('TWITTER_BEARER_TOKEN')
        if not self.bearer_token:
            raise ValueError("Twitter Bearer Token is required. Set TWITTER_BEARER_TOKEN environment variable.")
        
        self.base_url = "https://api.twitter.com/2"
        self.headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        }
    
    def search_tweets(self, query: str, max_results: int = 100, days_back: int = 7) -> List[TwitterLead]:
        """
        Search for tweets using Twitter API v2.
        
        Args:
            query: Search query
            max_results: Maximum number of tweets (10-100 for recent search)
            days_back: How many days back to search
            
        Returns:
            List of TwitterLead objects
        """
        # Calculate start time (Twitter API requires ISO format)
        start_time = (datetime.now() - timedelta(days=days_back)).isoformat()
        
        # API endpoint
        url = f"{self.base_url}/tweets/search/recent"
        
        # Parameters
        params = {
            'query': query,
            'max_results': min(max_results, 100),  # API limit
            'start_time': start_time,
            'tweet.fields': 'created_at,author_id,public_metrics,context_annotations',
            'expansions': 'author_id',
            'user.fields': 'username,name,public_metrics'
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            tweets = []
            
            if 'data' not in data:
                print("No tweets found for query:", query)
                return tweets
            
            # Create user lookup for usernames
            users = {}
            if 'includes' in data and 'users' in data['includes']:
                for user in data['includes']['users']:
                    users[user['id']] = user
            
            # Process tweets
            for tweet_data in data['data']:
                author_id = tweet_data['author_id']
                username = users.get(author_id, {}).get('username', 'unknown')
                
                tweet = TwitterLead(
                    id=tweet_data['id'],
                    text=tweet_data['text'],
                    author_id=author_id,
                    username=username,
                    created_at=datetime.fromisoformat(tweet_data['created_at'].replace('Z', '+00:00')),
                    public_metrics=tweet_data.get('public_metrics', {}),
                    url=f"https://twitter.com/{username}/status/{tweet_data['id']}"
                )
                tweets.append(tweet)
            
            return tweets
            
        except requests.exceptions.RequestException as e:
            print(f"Error making API request: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return []
    
    def calculate_lead_score(self, tweet: TwitterLead, keywords: List[str]) -> Dict:
        """Calculate lead scoring for a tweet."""
        text_lower = tweet.text.lower()
        
        # Keyword matching
        keywords_matched = [kw for kw in keywords if kw.lower() in text_lower]
        keyword_score = len(keywords_matched) / len(keywords) if keywords else 0
        
        # Engagement score
        metrics = tweet.public_metrics
        engagement = (
            metrics.get('like_count', 0) + 
            metrics.get('retweet_count', 0) * 2 + 
            metrics.get('reply_count', 0) * 1.5
        )
        
        # Recency score
        hours_ago = (datetime.now() - tweet.created_at.replace(tzinfo=None)).total_seconds() / 3600
        recency_score = max(0, 1 - (hours_ago / (24 * 7)))  # Decay over a week
        
        # Content quality indicators
        quality_indicators = ['?', 'help', 'advice', 'how to', 'need', 'looking for']
        quality_score = sum(1 for indicator in quality_indicators if indicator in text_lower) / len(quality_indicators)
        
        # Combined confidence score
        confidence_score = (keyword_score * 0.4 + 
                          min(engagement / 10, 1) * 0.3 + 
                          recency_score * 0.2 + 
                          quality_score * 0.1)
        
        return {
            'id': tweet.id,
            'url': tweet.url,
            'text': tweet.text,
            'username': tweet.username,
            'author_id': tweet.author_id,
            'created_at': tweet.created_at.isoformat(),
            'public_metrics': tweet.public_metrics,
            'keywords_matched': keywords_matched,
            'confidence_score': min(confidence_score, 1.0),
            'engagement_total': engagement,
            'hours_ago': hours_ago
        }


def search_twitter_leads_api(keywords: List[str], max_results: int = 100, days_back: int = 7) -> List[Dict]:
    """
    Search for leads using Twitter API v2.
    
    Args:
        keywords: List of keywords to search for
        max_results: Maximum tweets to retrieve
        days_back: Days to look back
        
    Returns:
        List of lead dictionaries
    """
    try:
        finder = TwitterAPILeadFinder()
    except ValueError as e:
        print(f"❌ {e}")
        print("\n🔧 To use Twitter API:")
        print("1. Get Twitter API access at https://developer.twitter.com")
        print("2. Create a Bearer Token")
        print("3. Set environment variable: export TWITTER_BEARER_TOKEN='your_token'")
        print("4. Or add it to your .env file")
        return []
    
    # Create search query
    query = ' OR '.join([f'"{keyword}"' for keyword in keywords])
    
    print(f"🔍 Searching Twitter API for: {query}")
    print(f"📅 Looking back {days_back} days")
    print(f"🎯 Max results: {max_results}")
    
    # Search tweets
    tweets = finder.search_tweets(query, max_results=max_results, days_back=days_back)
    
    if not tweets:
        return []
    
    print(f"📊 Found {len(tweets)} tweets")
    
    # Analyze tweets
    leads = []
    for tweet in tweets:
        lead = finder.calculate_lead_score(tweet, keywords)
        leads.append(lead)
    
    # Sort by confidence score
    leads.sort(key=lambda x: x['confidence_score'], reverse=True)
    
    return leads


if __name__ == "__main__":
    # Example usage
    test_keywords = ["how to market", "marketing help", "need marketing advice"]
    
    print("🐦 Twitter API Lead Finder")
    print("=" * 40)
    
    leads = search_twitter_leads_api(test_keywords, max_results=50, days_back=3)
    
    if leads:
        print(f"\n✅ Found {len(leads)} potential leads")
        
        # Show top 5 results
        for i, lead in enumerate(leads[:5], 1):
            print(f"\n{i}. @{lead['username']}: {lead['text'][:100]}...")
            print(f"   Confidence: {lead['confidence_score']:.2f} | Engagement: {lead['engagement_total']}")
            print(f"   Keywords: {', '.join(lead['keywords_matched'])}")
            print(f"   🔗 {lead['url']}")
    else:
        print("\n❌ No leads found or API not configured")