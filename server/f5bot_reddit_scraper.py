#!/usr/bin/env python3
"""
F5Bot Reddit scraper integrated with the lead generation database system.
Based on F5Bot techniques from https://intoli.com/blog/f5bot/
"""

import requests
import json
import time
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import urllib.parse
from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class RedditPost:
    """Data structure for Reddit posts."""
    id: str
    title: str
    content: str
    author: str
    subreddit: str
    url: str
    score: int
    num_comments: int
    created_utc: float
    permalink: str
    matched_keywords: List[str]

class F5BotRedditScraper:
    """
    F5Bot Reddit scraper integrated with database system.
    """
    
    def __init__(self):
        self.session = requests.Session()
        
        # Rotate user agents to avoid detection (F5Bot technique)
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0'
        ]
        
        self._setup_session()
        
        # Rate limiting parameters (F5Bot uses conservative delays)
        self.min_delay = 3
        self.max_delay = 7
        self.request_count = 0
        
        # Keyword batching parameters for optimal performance
        self.max_keywords_per_batch = 12  # Optimal batch size for Reddit API
        self.max_query_length = 1800  # Conservative URL length limit
        
    def _setup_session(self):
        """Setup session with headers that mimic a real browser."""
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
        
    def _rotate_user_agent(self):
        """Rotate user agent for each request (F5Bot technique)."""
        user_agent = random.choice(self.user_agents)
        self.session.headers.update({'User-Agent': user_agent})
        
    def _smart_delay(self):
        """Implement smart delays to avoid rate limiting (F5Bot approach)."""
        self.request_count += 1
        
        # Base delay with jitter
        base_delay = random.uniform(self.min_delay, self.max_delay)
        
        # Increase delay after multiple requests
        if self.request_count % 5 == 0:
            base_delay *= 1.5
            print(f"  🕐 Increased delay after {self.request_count} requests")
        
        time.sleep(base_delay)
        
    def search_reddit_for_keywords(self, keywords: List[str], limit: int = 100, time_filter: str = 'week') -> List[RedditPost]:
        """
        Search Reddit for posts containing any of the keywords using F5Bot techniques.
        Automatically splits large keyword lists into optimal batches.
        
        Args:
            keywords: List of search terms from database
            limit: Maximum number of results
            time_filter: Time filter (hour, day, week, month, year, all)
        """
        if not keywords:
            print("⚠️  No keywords provided")
            return []
            
        print(f"🔍 F5Bot Reddit Search: {len(keywords)} keywords")
        print(f"📝 Keywords: {', '.join(keywords[:5])}{'...' if len(keywords) > 5 else ''}")
        print(f"📊 Limit: {limit}, Time filter: {time_filter}")
        
        # Split keywords into optimal batches for large lists
        keyword_batches = self._split_keywords_into_batches(keywords)
        print(f"📦 Split into {len(keyword_batches)} batches for optimal performance")
        
        all_posts = []
        
        # F5Bot uses multiple search strategies
        search_methods = [
            self._search_via_json_api,
            self._search_via_rss_feeds
        ]
        
        for batch_num, keyword_batch in enumerate(keyword_batches, 1):
            print(f"\n🔄 Processing batch {batch_num}/{len(keyword_batches)} ({len(keyword_batch)} keywords)")
            
            batch_posts = []
            
            for i, search_method in enumerate(search_methods):
                try:
                    print(f"  Method {i+1}/{len(search_methods)}: {search_method.__name__}")
                    
                    method_posts = search_method(keyword_batch, limit // len(keyword_batches), time_filter)
                    
                    if method_posts:
                        batch_posts.extend(method_posts)
                        print(f"    ✅ Found {len(method_posts)} posts")
                    else:
                        print(f"    ℹ️  No results from this method")
                        
                except Exception as e:
                    print(f"    ❌ Method failed: {str(e)}")
                    continue
            
            all_posts.extend(batch_posts)
            print(f"  📊 Batch {batch_num} total: {len(batch_posts)} posts")
            
            # Stop if we have enough results
            if len(all_posts) >= limit:
                print(f"  🎯 Reached target limit, stopping early")
                break
        
        # Remove duplicates and sort by relevance
        unique_posts = self._deduplicate_posts(all_posts)
        unique_posts = self._filter_by_keywords_relevance(unique_posts, keywords)
        
        print(f"\n✅ Total unique posts found: {len(unique_posts)}")
        return unique_posts[:limit]
    
    def _search_via_json_api(self, keywords: List[str], limit: int, time_filter: str) -> List[RedditPost]:
        """Search using Reddit's JSON API (F5Bot primary method)."""
        posts = []
        
        try:
            # Rotate user agent
            self._rotate_user_agent()
            
            # Build combined search query using OR operator
            # Reddit supports: (keyword1 OR keyword2 OR keyword3)
            search_query = "(" + " OR ".join([f'"{kw}"' for kw in keywords]) + ")"
            
            url = f"https://www.reddit.com/search.json"
            
            params = {
                'q': search_query,
                'sort': 'new',
                't': time_filter,
                'limit': min(limit, 100),  # Reddit API limit
                'type': 'link'
            }
            
            print(f"    📡 Searching {len(keywords)} keywords via JSON API")
            
            response = self.session.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'data' in data and 'children' in data['data']:
                    for item in data['data']['children']:
                        post_data = item['data']
                        
                        # Determine which keywords match this post
                        title = post_data.get('title', '').lower()
                        content = post_data.get('selftext', '').lower()
                        full_text = f"{title} {content}"
                        
                        matched_keywords = []
                        for keyword in keywords:
                            if keyword.lower() in full_text:
                                matched_keywords.append(keyword)
                        
                        # Only include posts that actually match our keywords
                        if matched_keywords:
                            post = RedditPost(
                                id=post_data.get('id', ''),
                                title=post_data.get('title', ''),
                                content=post_data.get('selftext', ''),
                                author=post_data.get('author', ''),
                                subreddit=post_data.get('subreddit', ''),
                                url=post_data.get('url', ''),
                                score=post_data.get('score', 0),
                                num_comments=post_data.get('num_comments', 0),
                                created_utc=post_data.get('created_utc', 0),
                                permalink=f"https://reddit.com{post_data.get('permalink', '')}",
                                matched_keywords=matched_keywords
                            )
                            
                            posts.append(post)
                        
            elif response.status_code == 429:
                print(f"    ⚠️  Rate limited (429)")
                time.sleep(15)
            elif response.status_code == 403:
                print(f"    ⚠️  Forbidden (403)")
            else:
                print(f"    ⚠️  HTTP {response.status_code}")
                
        except Exception as e:
            print(f"    ❌ JSON API error: {str(e)}")
        
        # Smart delay between requests
        self._smart_delay()
        
        return posts
    
    def _search_via_rss_feeds(self, keywords: List[str], limit: int, time_filter: str) -> List[RedditPost]:
        """Search using RSS feeds (F5Bot fallback method)."""
        posts = []
        
        try:
            # Rotate user agent
            self._rotate_user_agent()
            
            # Build combined RSS search query
            search_query = "(" + " OR ".join([f'"{kw}"' for kw in keywords]) + ")"
            
            url = f"https://www.reddit.com/search.rss"
            
            params = {
                'q': search_query,
                'sort': 'new',
                't': time_filter,
                'limit': min(limit, 100)
            }
            
            print(f"    📡 Searching {len(keywords)} keywords via RSS")
            
            response = self.session.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                # Parse RSS/Atom feed
                posts = self._parse_rss_response(response.text, keywords)
                
            elif response.status_code == 429:
                print(f"    ⚠️  RSS Rate limited (429)")
                time.sleep(15)
            else:
                print(f"    ⚠️  RSS HTTP {response.status_code}")
                
        except Exception as e:
            print(f"    ❌ RSS error: {str(e)}")
        
        # Smart delay
        self._smart_delay()
        
        return posts
    
    def _parse_rss_response(self, rss_content: str, keywords: List[str]) -> List[RedditPost]:
        """Parse RSS/Atom response into RedditPost objects."""
        posts = []
        
        try:
            import xml.etree.ElementTree as ET
            import html
            import re
            
            root = ET.fromstring(rss_content)
            
            # Handle both RSS and Atom formats
            entries = root.findall('.//{http://www.w3.org/2005/Atom}entry')
            if not entries:
                entries = root.findall('.//item')
            
            for entry in entries:
                try:
                    # Extract title
                    title_elem = entry.find('{http://www.w3.org/2005/Atom}title')
                    if title_elem is None:
                        title_elem = entry.find('title')
                    title = html.unescape(title_elem.text) if title_elem is not None else ""
                    
                    # Extract content
                    content_elem = entry.find('{http://www.w3.org/2005/Atom}content')
                    if content_elem is None:
                        content_elem = entry.find('description')
                    content = html.unescape(content_elem.text) if content_elem is not None else ""
                    
                    # Clean HTML tags
                    content = re.sub(r'<[^>]+>', '', content)
                    
                    # Determine which keywords match this post
                    full_text = f"{title} {content}".lower()
                    matched_keywords = []
                    for keyword in keywords:
                        if keyword.lower() in full_text:
                            matched_keywords.append(keyword)
                    
                    # Only include posts that match our keywords
                    if matched_keywords:
                        # Extract URL
                        link_elem = entry.find('{http://www.w3.org/2005/Atom}link')
                        if link_elem is not None:
                            url = link_elem.get('href', '')
                        else:
                            link_elem = entry.find('link')
                            url = link_elem.text if link_elem is not None else ""
                        
                        # Extract subreddit from URL
                        subreddit = ""
                        if "/r/" in url:
                            try:
                                subreddit = url.split("/r/")[1].split("/")[0]
                            except:
                                pass
                        
                        # Extract post ID from URL
                        post_id = ""
                        if "/comments/" in url:
                            try:
                                post_id = url.split("/comments/")[1].split("/")[0]
                            except:
                                post_id = f"rss_{hash(url)}"
                        
                        post = RedditPost(
                            id=post_id,
                            title=title,
                            content=content,
                            author="unknown",  # RSS doesn't always include author
                            subreddit=subreddit,
                            url=url,
                            score=0,  # RSS doesn't include scores
                            num_comments=0,
                            created_utc=time.time(),  # Approximate
                            permalink=url,
                            matched_keywords=matched_keywords
                        )
                        
                        posts.append(post)
                    
                except Exception as e:
                    print(f"    ⚠️  Error parsing RSS entry: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"  ❌ RSS parsing error: {str(e)}")
        
        return posts
    
    def _deduplicate_posts(self, posts: List[RedditPost]) -> List[RedditPost]:
        """Remove duplicate posts based on ID and URL."""
        seen_ids = set()
        seen_urls = set()
        unique_posts = []
        
        for post in posts:
            # Check for duplicates
            if post.id and post.id in seen_ids:
                continue
            if post.url and post.url in seen_urls:
                continue
            
            # Add to seen sets
            if post.id:
                seen_ids.add(post.id)
            if post.url:
                seen_urls.add(post.url)
            
            unique_posts.append(post)
        
        return unique_posts
    
    def _filter_by_keywords_relevance(self, posts: List[RedditPost], keywords: List[str]) -> List[RedditPost]:
        """Filter and sort posts by keywords relevance (F5Bot technique)."""
        
        def calculate_relevance(post: RedditPost) -> float:
            """Calculate relevance score for a post."""
            score = 0.0
            
            title_lower = post.title.lower()
            content_lower = post.content.lower()
            
            # Score based on matched keywords
            for keyword in post.matched_keywords:
                keyword_lower = keyword.lower()
                
                # Title matches are more important
                if keyword_lower in title_lower:
                    score += 10.0
                    # Exact phrase match in title
                    if keyword_lower == title_lower.strip():
                        score += 5.0
                
                # Content matches
                if keyword_lower in content_lower:
                    score += 5.0
                
                # Word boundary matches are better than partial matches
                import re
                if re.search(r'\b' + re.escape(keyword_lower) + r'\b', title_lower):
                    score += 3.0
                if re.search(r'\b' + re.escape(keyword_lower) + r'\b', content_lower):
                    score += 2.0
            
            # Boost score based on number of matched keywords
            score += len(post.matched_keywords) * 2.0
            
            # Boost score based on Reddit metrics
            score += min(post.score / 10.0, 5.0)  # Max 5 points from upvotes
            score += min(post.num_comments / 5.0, 3.0)  # Max 3 points from comments
            
            return score
        
        # Calculate relevance for each post
        posts_with_relevance = []
        for post in posts:
            relevance = calculate_relevance(post)
            if relevance > 0:  # Only include posts with some relevance
                posts_with_relevance.append((post, relevance))
        
        # Sort by relevance (highest first)
        posts_with_relevance.sort(key=lambda x: x[1], reverse=True)
        
        return [post for post, relevance in posts_with_relevance]
    
    def _split_keywords_into_batches(self, keywords: List[str]) -> List[List[str]]:
        """
        Split keywords into optimal batches for Reddit API.
        Considers both keyword count and URL length limits.
        """
        if len(keywords) <= self.max_keywords_per_batch:
            return [keywords]
        
        batches = []
        current_batch = []
        current_query_length = 0
        
        for keyword in keywords:
            # Estimate query length for this keyword (with quotes and OR operator)
            keyword_length = len(f'"{keyword}" OR ')
            
            # Check if adding this keyword would exceed limits
            would_exceed_count = len(current_batch) >= self.max_keywords_per_batch
            would_exceed_length = current_query_length + keyword_length > self.max_query_length
            
            if (would_exceed_count or would_exceed_length) and current_batch:
                # Start new batch
                batches.append(current_batch)
                current_batch = [keyword]
                current_query_length = keyword_length
            else:
                # Add to current batch
                current_batch.append(keyword)
                current_query_length += keyword_length
        
        # Add the last batch if it has keywords
        if current_batch:
            batches.append(current_batch)
        
        return batches


# Function to maintain compatibility with existing background service
def search_reddit_leads_efficient(keywords: List[str], 
                                 subreddits: List[str] = None, 
                                 days_back: int = 7,
                                 limit: int = 100) -> List[Dict]:
    """
    Main function for background service integration.
    Converts F5Bot results to the expected format.
    """
    print("🤖 Using F5Bot Reddit scraper...")
    
    try:
        scraper = F5BotRedditScraper()
        
        # Convert days_back to time_filter
        if days_back <= 1:
            time_filter = 'day'
        elif days_back <= 7:
            time_filter = 'week'
        elif days_back <= 30:
            time_filter = 'month'
        else:
            time_filter = 'year'
        
        posts = scraper.search_reddit_for_keywords(keywords, limit, time_filter)
        
        # Convert to expected format for database storage
        leads = []
        for post in posts:
            lead = {
                "id": f"f5bot_{post.id}",
                "source_method": "f5bot_api",
                "title": post.title,
                "content": post.content,
                "url": post.permalink,
                "subreddit": post.subreddit,
                "author": post.author,
                "upvotes": post.score,
                "comments": post.num_comments,
                "created_date": datetime.fromtimestamp(post.created_utc) if post.created_utc else datetime.now(),
                "matched_keywords": post.matched_keywords,
                "score": len(post.matched_keywords) * 10 + min(post.score, 50),  # Simple scoring
                "hotness_score": len(post.matched_keywords) * 10 + min(post.score, 50)
            }
            leads.append(lead)
        
        print(f"✅ F5Bot scraper found {len(leads)} leads")
        return leads
        
    except Exception as e:
        print(f"❌ F5Bot scraper failed: {str(e)}")
        return []