#!/usr/bin/env python3
"""
X (Twitter) scraper using snscrape for keyword-based lead generation.
"""

import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import snscrape.modules.twitter as sntwitter
from dataclasses import dataclass


@dataclass
class Tweet:
    """Data class for tweet information."""
    id: str
    url: str
    content: str
    user: str
    username: str
    date: datetime
    retweet_count: int
    like_count: int
    reply_count: int
    quote_count: int
    hashtags: List[str]
    mentions: List[str]
    is_retweet: bool
    is_reply: bool


class XScrapingLeadFinder:
    """Main class for finding leads on X using keyword searches."""
    
    def __init__(self):
        self.confidence_weights = {
            'keyword_match': 0.3,
            'engagement': 0.2,
            'recency': 0.2,
            'user_activity': 0.15,
            'content_quality': 0.15
        }
    
    def search_tweets(self, query: str, limit: int = 100, days_back: int = 7) -> List[Tweet]:
        """
        Search for tweets using snscrape.
        
        Args:
            query: Search query (can include keywords, hashtags, etc.)
            limit: Maximum number of tweets to retrieve
            days_back: How many days back to search
            
        Returns:
            List of Tweet objects
        """
        tweets = []
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Format query with date range
        formatted_query = f"{query} since:{start_date.strftime('%Y-%m-%d')} until:{end_date.strftime('%Y-%m-%d')}"
        
        try:
            # Use snscrape to get tweets
            for i, tweet in enumerate(sntwitter.TwitterSearchScraper(formatted_query).get_items()):
                if i >= limit:
                    break
                
                # Extract hashtags and mentions
                hashtags = [tag.lower() for tag in re.findall(r'#(\w+)', tweet.rawContent)]
                mentions = [mention for mention in re.findall(r'@(\w+)', tweet.rawContent)]
                
                tweet_obj = Tweet(
                    id=str(tweet.id),
                    url=tweet.url,
                    content=tweet.rawContent,
                    user=tweet.user.displayname or tweet.user.username,
                    username=tweet.user.username,
                    date=tweet.date,
                    retweet_count=tweet.retweetCount or 0,
                    like_count=tweet.likeCount or 0,
                    reply_count=tweet.replyCount or 0,
                    quote_count=tweet.quoteCount or 0,
                    hashtags=hashtags,
                    mentions=mentions,
                    is_retweet=hasattr(tweet, 'retweetedTweet') and tweet.retweetedTweet is not None,
                    is_reply=tweet.inReplyToTweetId is not None
                )
                
                tweets.append(tweet_obj)
                
        except Exception as e:
            print(f"Error scraping tweets: {e}")
            
        return tweets
    
    def calculate_confidence_score(self, tweet: Tweet, keywords: List[str]) -> float:
        """Calculate confidence score for a tweet based on various factors."""
        score = 0.0
        
        # Keyword matching score
        content_lower = tweet.content.lower()
        keyword_matches = sum(1 for keyword in keywords if keyword.lower() in content_lower)
        keyword_score = min(keyword_matches / len(keywords), 1.0)
        score += keyword_score * self.confidence_weights['keyword_match']
        
        # Engagement score (normalized)
        total_engagement = tweet.like_count + tweet.retweet_count + tweet.reply_count
        engagement_score = min(total_engagement / 100, 1.0)  # Normalize to 0-1
        score += engagement_score * self.confidence_weights['engagement']
        
        # Recency score
        hours_ago = (datetime.now() - tweet.date.replace(tzinfo=None)).total_seconds() / 3600
        recency_score = max(0, 1 - (hours_ago / (24 * 7)))  # Decay over a week
        score += recency_score * self.confidence_weights['recency']
        
        # Content quality score (basic heuristics)
        content_quality = self._calculate_content_quality(tweet)
        score += content_quality * self.confidence_weights['content_quality']
        
        # User activity score (based on engagement patterns)
        user_activity = min((tweet.like_count + tweet.retweet_count) / 50, 1.0)
        score += user_activity * self.confidence_weights['user_activity']
        
        return min(score, 1.0)
    
    def _calculate_content_quality(self, tweet: Tweet) -> float:
        """Calculate content quality score based on various factors."""
        content = tweet.content
        
        # Basic quality indicators
        quality_score = 0.5  # Base score
        
        # Length check (not too short, not too long)
        if 50 <= len(content) <= 280:
            quality_score += 0.2
        
        # Has question marks (indicates asking for help/recommendations)
        if '?' in content:
            quality_score += 0.2
        
        # Contains specific pain point indicators
        pain_indicators = ['need', 'help', 'struggling', 'looking for', 'recommend', 'advice']
        if any(indicator in content.lower() for indicator in pain_indicators):
            quality_score += 0.3
        
        # Avoid spam-like content
        if content.count('!') > 3 or content.isupper():
            quality_score -= 0.3
        
        # Not a retweet (original content is usually better)
        if not tweet.is_retweet:
            quality_score += 0.1
        
        return max(0, min(quality_score, 1.0))
    
    def calculate_hotness_score(self, tweet: Tweet) -> float:
        """Calculate hotness score based on engagement and recency."""
        # Engagement component
        engagement = tweet.like_count + (tweet.retweet_count * 2) + (tweet.reply_count * 1.5)
        
        # Recency component (tweets lose hotness over time)
        hours_ago = (datetime.now() - tweet.date.replace(tzinfo=None)).total_seconds() / 3600
        recency_multiplier = max(0.1, 1 - (hours_ago / (24 * 3)))  # Decay over 3 days
        
        return engagement * recency_multiplier
    
    def analyze_tweet(self, tweet: Tweet, keywords: List[str]) -> Dict:
        """Analyze a single tweet and return lead information."""
        # Find matched keywords
        content_lower = tweet.content.lower()
        keywords_matched = [kw for kw in keywords if kw.lower() in content_lower]
        
        # Calculate scores
        confidence_score = self.calculate_confidence_score(tweet, keywords)
        hotness_score = self.calculate_hotness_score(tweet)
        
        return {
            'id': tweet.id,
            'url': tweet.url,
            'type': 'tweet',
            'content': tweet.content,
            'user': tweet.user,
            'username': tweet.username,
            'created_date': tweet.date.isoformat(),
            'like_count': tweet.like_count,
            'retweet_count': tweet.retweet_count,
            'reply_count': tweet.reply_count,
            'quote_count': tweet.quote_count,
            'hashtags': tweet.hashtags,
            'mentions': tweet.mentions,
            'is_retweet': tweet.is_retweet,
            'is_reply': tweet.is_reply,
            'keywords_matched': keywords_matched,
            'confidence_score': confidence_score,
            'hotness_score': hotness_score,
            'engagement_total': tweet.like_count + tweet.retweet_count + tweet.reply_count
        }


def search_x_leads(keywords: List[str], days_back: int = 7, limit: int = 100) -> List[Dict]:
    """
    Main function to search for leads on X.
    
    Args:
        keywords: List of keywords to search for
        days_back: How many days back to search
        limit: Maximum number of tweets to analyze
        
    Returns:
        List of analyzed lead dictionaries
    """
    finder = XScrapingLeadFinder()
    all_leads = []
    
    # Create search query from keywords
    query = ' OR '.join([f'"{keyword}"' for keyword in keywords])
    
    print(f"🔍 Searching X for: {query}")
    print(f"📅 Looking back {days_back} days")
    print(f"🎯 Limit: {limit} tweets")
    
    # Search for tweets
    tweets = finder.search_tweets(query, limit=limit, days_back=days_back)
    
    print(f"📊 Found {len(tweets)} tweets")
    
    # Analyze each tweet
    for tweet in tweets:
        lead = finder.analyze_tweet(tweet, keywords)
        all_leads.append(lead)
    
    # Sort by hotness score
    all_leads.sort(key=lambda x: x['hotness_score'], reverse=True)
    
    return all_leads


if __name__ == "__main__":
    # Example usage
    test_keywords = ["How do I market myself", "marketing help", "need marketing advice"]
    leads = search_x_leads(test_keywords, days_back=3, limit=50)
    
    print(f"\n✅ Found {len(leads)} potential leads")
    
    # Show top 5 results
    for i, lead in enumerate(leads[:5], 1):
        print(f"\n{i}. @{lead['username']}: {lead['content'][:100]}...")
        print(f"   Engagement: {lead['engagement_total']} | Confidence: {lead['confidence_score']:.2f}")
        print(f"   Keywords: {', '.join(lead['keywords_matched'])}")
        print(f"   URL: {lead['url']}")