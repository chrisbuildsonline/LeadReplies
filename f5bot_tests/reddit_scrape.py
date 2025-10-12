#!/usr/bin/env python3
"""
Reddit scraper based on F5Bot approach from https://intoli.com/blog/f5bot/
This implements the techniques described in the blog post for reliable Reddit scraping.
"""

import requests
import json
import time
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import urllib.parse
from dataclasses import dataclass

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
    matched_keywords: List[str]  # Keywords that matched this post

class F5BotRedditScraper:
    """
    Reddit scraper implementing F5Bot techniques for reliable data extraction.
    Based on the approach described at https://intoli.com/blog/f5bot/
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
        self.min_delay = 2
        self.max_delay = 5
        self.request_count = 0
        
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
        if self.request_count % 10 == 0:
            base_delay *= 1.5
            print(f"  🕐 Increased delay after {self.request_count} requests")
        
        time.sleep(base_delay)
        
    def search_reddit(self, keywords: List[str], limit: int = 100, time_filter: str = 'week') -> List[RedditPost]:
        """
        Search Reddit for posts containing any of the keywords using F5Bot techniques.
        
        Args:
            keywords: List of search terms
            limit: Maximum number of results
            time_filter: Time filter (hour, day, week, month, year, all)
        """
        print(f"🔍 Searching Reddit for {len(keywords)} keywords (F5Bot method)")
        print(f"� Kieywords: {', '.join(keywords)}")
        print(f"📊 Limit: {limit}, Time filter: {time_filter}")
        
        posts = []
        
        # F5Bot uses multiple search strategies
        search_methods = [
            self._search_via_json_api,
            self._search_via_rss_feeds,
            self._search_via_pushshift_api
        ]
        
        for i, search_method in enumerate(search_methods):
            try:
                print(f"\n🔄 Trying search method {i+1}/{len(search_methods)}: {search_method.__name__}")
                
                method_posts = search_method(keywords, limit, time_filter)
                
                if method_posts:
                    posts.extend(method_posts)
                    print(f"  ✅ Found {len(method_posts)} posts with this method")
                else:
                    print(f"  ℹ️  No results from this method")
                    
                # Don't try other methods if we have enough results
                if len(posts) >= limit:
                    break
                    
            except Exception as e:
                print(f"  ❌ Method failed: {str(e)}")
                continue
        
        # Remove duplicates and sort by relevance
        unique_posts = self._deduplicate_posts(posts)
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
            
            print(f"  📡 Query: {search_query}")
            print(f"  📡 Requesting: {url}")
            
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
                print(f"  ⚠️  Rate limited (429)")
                time.sleep(10)
            elif response.status_code == 403:
                print(f"  ⚠️  Forbidden (403)")
            else:
                print(f"  ⚠️  HTTP {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ JSON API error: {str(e)}")
        
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
            
            print(f"  📡 RSS Query: {search_query}")
            print(f"  📡 RSS Request: {url}")
            
            response = self.session.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                # Parse RSS/Atom feed
                posts = self._parse_rss_response(response.text, keywords)
                
            elif response.status_code == 429:
                print(f"  ⚠️  RSS Rate limited (429)")
                time.sleep(10)
            else:
                print(f"  ⚠️  RSS HTTP {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ RSS error: {str(e)}")
        
        # Smart delay
        self._smart_delay()
        
        return posts
    
    def _search_via_pushshift_api(self, keywords: List[str], limit: int, time_filter: str) -> List[RedditPost]:
        """Search using Pushshift API (F5Bot alternative method)."""
        posts = []
        
        try:
            # Rotate user agent
            self._rotate_user_agent()
            
            # Convert time filter to timestamp
            now = datetime.now()
            if time_filter == 'hour':
                after = now - timedelta(hours=1)
            elif time_filter == 'day':
                after = now - timedelta(days=1)
            elif time_filter == 'week':
                after = now - timedelta(weeks=1)
            elif time_filter == 'month':
                after = now - timedelta(days=30)
            elif time_filter == 'year':
                after = now - timedelta(days=365)
            else:
                after = now - timedelta(weeks=1)  # Default to week
            
            after_timestamp = int(after.timestamp())
            
            # Pushshift doesn't support OR queries well, so we'll search for all keywords combined
            search_query = " OR ".join(keywords)
            
            # Pushshift API URL
            url = "https://api.pushshift.io/reddit/search/submission/"
            
            params = {
                'q': search_query,
                'after': after_timestamp,
                'sort': 'desc',
                'sort_type': 'created_utc',
                'size': min(limit, 100)
            }
            
            print(f"  📡 Pushshift Query: {search_query}")
            print(f"  📡 Pushshift Request: {url}")
            
            response = self.session.get(url, params=params, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'data' in data:
                    for post_data in data['data']:
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
                                permalink=f"https://reddit.com/r/{post_data.get('subreddit', '')}/comments/{post_data.get('id', '')}",
                                matched_keywords=matched_keywords
                            )
                            
                            posts.append(post)
                        
            else:
                print(f"  ⚠️  Pushshift HTTP {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Pushshift error: {str(e)}")
        
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

def test_f5bot_scraper():
    """Test the F5Bot scraper with multiple keywords."""
    print("🤖 F5BOT REDDIT SCRAPER TEST - MULTIPLE KEYWORDS")
    print("=" * 60)
    print("Based on: https://intoli.com/blog/f5bot/")
    print("=" * 60)
    
    scraper = F5BotRedditScraper()
    
    # Test with multiple keywords as requested
    keywords = ["fishing gear", "self help", "seo tool"]
    
    start_time = time.time()
    
    try:
        posts = scraper.search_reddit(
            keywords=keywords,
            limit=100,
            time_filter='week'
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n📊 RESULTS SUMMARY")
        print("=" * 40)
        print(f"Keywords: {', '.join(keywords)}")
        print(f"Posts found: {len(posts)}")
        print(f"Time taken: {duration:.1f} seconds")
        print(f"Requests made: {scraper.request_count}")
        
        # Analyze keyword distribution
        keyword_counts = {}
        for post in posts:
            for kw in post.matched_keywords:
                keyword_counts[kw] = keyword_counts.get(kw, 0) + 1
        
        print(f"\n📈 KEYWORD DISTRIBUTION:")
        for kw, count in keyword_counts.items():
            print(f"  '{kw}': {count} posts")
        
        if posts:
            print(f"\n📝 TOP RESULTS:")
            print("-" * 40)
            
            for i, post in enumerate(posts[:5], 1):
                print(f"\n{i}. {post.title[:80]}...")
                print(f"   👤 u/{post.author} in r/{post.subreddit}")
                print(f"   📊 {post.score} upvotes, {post.num_comments} comments")
                print(f"   🎯 Matched keywords: {', '.join(post.matched_keywords)}")
                print(f"   🔗 {post.permalink}")
                
                if post.content:
                    content_preview = post.content[:150].replace('\n', ' ')
                    print(f"   💬 {content_preview}...")
        
        else:
            print("\n❌ No posts found")
            print("This could mean:")
            print("- The keywords are too specific")
            print("- Reddit is blocking requests")
            print("- No recent posts match the keywords")
        
        print(f"\n🎯 F5BOT TECHNIQUE ANALYSIS:")
        print(f"✅ User agent rotation: Implemented")
        print(f"✅ Smart delays: {scraper.min_delay}-{scraper.max_delay}s")
        print(f"✅ Multiple search methods: 3 methods tried")
        print(f"✅ Multi-keyword search: Single query for all keywords")
        print(f"✅ Keyword matching: Shows which keywords matched each post")
        print(f"✅ Relevance filtering: Applied")
        print(f"✅ Deduplication: Applied")
        
        return len(posts) > 0
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_f5bot_scraper()
    
    if success:
        print(f"\n🎉 F5BOT SCRAPER WORKING!")
    else:
        print(f"\n💡 Consider trying:")
        print("- Different keywords")
        print("- Longer time filters")
        print("- Running at different times")
        print("- Using VPN/proxy")