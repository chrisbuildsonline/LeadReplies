import requests
import xml.etree.ElementTree as ET
import time
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from urllib.parse import quote_plus
import json

class RedditLeadScraper:
    """
    Production-ready Reddit scraper that combines multiple approaches:
    1. RSS feeds (most reliable)
    2. JSON endpoints (when available)
    3. Single-query approach to avoid rate limiting
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, application/rss+xml, application/xml, text/xml',
            'Accept-Language': 'en-US,en;q=0.9',
        })
        self.base_delay = 2
    
    def search_leads(self, keywords: List[str], subreddits: List[str], days_back: int = 1) -> List[Dict]:
        """
        Main method to search for leads using the most reliable approach available.
        """
        print(f"🔍 Searching {len(subreddits)} subreddits for {len(keywords)} keywords...")
        print(f"📅 Looking back {days_back} days")
        
        all_leads = []
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        # Process subreddits in small batches to avoid overwhelming Reddit
        batch_size = 3
        for i in range(0, len(subreddits), batch_size):
            batch_subreddits = subreddits[i:i+batch_size]
            
            print(f"\n📦 Processing batch {i//batch_size + 1}: {', '.join([f'r/{s}' for s in batch_subreddits])}")
            
            for subreddit in batch_subreddits:
                try:
                    # Try RSS first (most reliable)
                    posts = self._get_posts_via_rss(subreddit, days_back)
                    
                    if not posts:
                        # Fallback to JSON if RSS fails
                        posts = self._get_posts_via_json(subreddit, days_back)
                    
                    if posts:
                        print(f"    📊 Got {len(posts)} raw posts")
                        # Filter by date and process
                        filtered_posts = self._filter_by_date(posts, cutoff_date)
                        print(f"    📅 {len(filtered_posts)} posts after date filtering")
                        leads = self._process_posts(filtered_posts, keywords)
                        print(f"    🔍 {len(leads)} leads after keyword matching")
                        all_leads.extend(leads)
                        
                        print(f"  ✅ r/{subreddit}: {len(leads)} leads from {len(filtered_posts)} posts")
                    else:
                        print(f"  ⚠️  r/{subreddit}: No posts retrieved")
                    
                    # Delay between subreddits
                    time.sleep(self.base_delay)
                    
                except Exception as e:
                    print(f"  ❌ r/{subreddit}: Error - {str(e)}")
                    continue
            
            # Longer delay between batches
            if i + batch_size < len(subreddits):
                print(f"  ⏳ Waiting before next batch...")
                time.sleep(5)
        
        return self._deduplicate_leads(all_leads)
    
    def _get_posts_via_rss(self, subreddit: str, days_back: int, limit: int = 25) -> List[Dict]:
        """Get posts using RSS feeds - most reliable method"""
        try:
            # Try different RSS endpoints
            rss_urls = [
                f"https://www.reddit.com/r/{subreddit}/new/.rss?limit={limit}",
                f"https://www.reddit.com/r/{subreddit}/.rss?limit={limit}",
            ]
            
            for rss_url in rss_urls:
                try:
                    response = self.session.get(rss_url, timeout=10)
                    
                    if response.status_code == 200:
                        posts = self._parse_rss_feed(response.text, subreddit)
                        if posts:
                            return posts
                    elif response.status_code == 403:
                        continue  # Try next URL
                    
                except Exception:
                    continue
            
            return []
            
        except Exception as e:
            print(f"    RSS error for r/{subreddit}: {str(e)}")
            return []
    
    def _get_posts_via_json(self, subreddit: str, days_back: int, limit: int = 25) -> List[Dict]:
        """Fallback: Get posts using JSON endpoints"""
        try:
            json_urls = [
                f"https://www.reddit.com/r/{subreddit}/new/.json?limit={limit}",
                f"https://www.reddit.com/r/{subreddit}/.json?limit={limit}",
            ]
            
            for json_url in json_urls:
                try:
                    response = self.session.get(json_url, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('data', {}).get('children'):
                            posts = [post['data'] for post in data['data']['children']]
                            return posts
                    elif response.status_code == 403:
                        continue
                    
                except Exception:
                    continue
            
            return []
            
        except Exception as e:
            print(f"    JSON error for r/{subreddit}: {str(e)}")
            return []
    
    def _parse_rss_feed(self, rss_content: str, subreddit: str) -> List[Dict]:
        """Parse RSS/Atom feed content into post dictionaries"""
        posts = []
        
        try:
            root = ET.fromstring(rss_content)
            
            # Handle Atom feeds (what Reddit actually uses)
            entries = root.findall('.//{http://www.w3.org/2005/Atom}entry')
            
            # Fallback to RSS if no Atom entries found
            if not entries:
                entries = root.findall('.//item')
            
            print(f"    📊 Found {len(entries)} entries in feed")
            
            for entry in entries:
                try:
                    # Handle Atom format (Reddit uses this)
                    atom_ns = '{http://www.w3.org/2005/Atom}'
                    
                    title_elem = entry.find(f'{atom_ns}title')
                    link_elem = entry.find(f'{atom_ns}link')
                    content_elem = entry.find(f'{atom_ns}content')
                    date_elem = entry.find(f'{atom_ns}published')
                    if date_elem is None:
                        date_elem = entry.find(f'{atom_ns}updated')
                    
                    # Author is nested
                    author_elem = entry.find(f'{atom_ns}author')
                    if author_elem is not None:
                        author_name_elem = author_elem.find(f'{atom_ns}name')
                        author = author_name_elem.text if author_name_elem is not None else "unknown"
                    else:
                        author = "unknown"
                    
                    if title_elem is None:
                        print(f"    ❌ No title found for entry")
                        continue
                    
                    title = title_elem.text or ""
                    
                    # Get link
                    link = ""
                    if link_elem is not None:
                        link = link_elem.text or link_elem.get('href', '')
                    
                    if not link:
                        print(f"    ❌ No link found for entry: {title[:30]}...")
                        continue
                    
                    # Get content
                    content = ""
                    if content_elem is not None:
                        content = content_elem.text or ""
                    
                    # Author was handled above
                    
                    # Extract Reddit post ID from URL
                    post_id = self._extract_post_id_from_url(link)
                    
                    # Parse date
                    pub_date = datetime.now()
                    if date_elem is not None and date_elem.text:
                        try:
                            date_str = date_elem.text
                            # Try different date formats
                            for fmt in ['%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%dT%H:%M:%SZ', '%a, %d %b %Y %H:%M:%S %z']:
                                try:
                                    pub_date = datetime.strptime(date_str, fmt)
                                    break
                                except ValueError:
                                    continue
                        except:
                            pass
                    
                    # Clean content (remove HTML tags)
                    clean_content = re.sub(r'<[^>]+>', '', content)
                    clean_content = re.sub(r'&[a-zA-Z0-9#]+;', ' ', clean_content)
                    clean_content = clean_content.strip()
                    
                    post = {
                        'id': post_id or f"atom_{abs(hash(link))}",
                        'title': title.strip(),
                        'selftext': clean_content[:1000],
                        'url': link,
                        'author': author,
                        'subreddit': subreddit,
                        'created_utc': pub_date.timestamp(),
                        'score': 1,
                        'num_comments': 0,
                        'permalink': self._extract_permalink_from_url(link),
                    }
                    
                    posts.append(post)
                    
                except Exception as e:
                    print(f"    ⚠️  Error parsing entry: {e}")
                    continue
            
        except ET.ParseError as e:
            print(f"    ❌ XML Parse Error: {e}")
        except Exception as e:
            print(f"    ❌ Feed parsing error: {e}")
        
        return posts
    
    def _extract_post_id_from_url(self, url: str) -> Optional[str]:
        """Extract Reddit post ID from URL"""
        try:
            match = re.search(r'/comments/([a-zA-Z0-9]+)/', url)
            if match:
                return match.group(1)
        except:
            pass
        return None
    
    def _extract_permalink_from_url(self, url: str) -> str:
        """Extract permalink from full URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.path
        except:
            return url
    
    def _filter_by_date(self, posts: List[Dict], cutoff_date: datetime) -> List[Dict]:
        """Filter posts by creation date"""
        filtered = []
        
        for post in posts:
            try:
                created_utc = post.get('created_utc', 0)
                created_date = datetime.fromtimestamp(created_utc)
                
                # Remove timezone info from cutoff_date for comparison
                cutoff_naive = cutoff_date.replace(tzinfo=None)
                created_naive = created_date.replace(tzinfo=None)
                
                if created_naive >= cutoff_naive:
                    filtered.append(post)
            except Exception as e:
                # If date parsing fails, include the post to be safe
                print(f"    ⚠️  Date filtering error: {e}")
                filtered.append(post)
        
        return filtered
    
    def _process_posts(self, posts: List[Dict], keywords: List[str]) -> List[Dict]:
        """Process posts and find keyword matches"""
        leads = []
        
        for post in posts:
            try:
                title = post.get('title', '')
                selftext = post.get('selftext', '')
                full_text = f"{title} {selftext}".lower()
                
                # Find matching keywords
                matched_keywords = []
                for keyword in keywords:
                    if keyword.lower() in full_text:
                        matched_keywords.append(keyword)
                    else:
                        # Check for multi-word keywords
                        keyword_words = keyword.lower().split()
                        if len(keyword_words) > 1 and all(word in full_text for word in keyword_words):
                            matched_keywords.append(keyword)
                
                if not matched_keywords:
                    continue
                
                # Calculate relevance score
                relevance_score = self._calculate_relevance_score(full_text, matched_keywords, post)
                
                lead = {
                    "reddit_id": post['id'],
                    "service": "reddit",
                    "title": title,
                    "content": selftext[:1000],
                    "url": post.get('url', ''),
                    "author": post.get('author', 'unknown'),
                    "subreddit": post.get('subreddit', ''),
                    "type": "post",
                    "keywords_matched": matched_keywords,
                    "hotness_score": relevance_score,
                    "upvotes": post.get('score', 0),
                    "num_comments": post.get('num_comments', 0),
                    "created_date": datetime.fromtimestamp(post.get('created_utc', 0)),
                    "raw_data": post
                }
                
                leads.append(lead)
                
            except Exception as e:
                continue
        
        return leads
    
    def _calculate_relevance_score(self, text: str, keywords: List[str], post: Dict) -> int:
        """Calculate relevance score for a post"""
        base_score = len(keywords) * 25
        
        # Question indicators
        question_indicators = ["how", "what", "where", "when", "why", "which", "?", "help", "advice", "recommend"]
        if any(indicator in text for indicator in question_indicators):
            base_score += 30
        
        # Problem indicators
        problem_indicators = ["problem", "issue", "trouble", "struggling", "difficult", "challenge", "need"]
        if any(indicator in text for indicator in problem_indicators):
            base_score += 25
        
        # Solution-seeking language
        solution_indicators = ["looking for", "alternative", "better", "tool", "software", "solution", "platform"]
        if any(indicator in text for indicator in solution_indicators):
            base_score += 35
        
        # Engagement boost
        score = post.get('score', 0)
        if score > 5:
            base_score += min(15, score // 2)
        
        num_comments = post.get('num_comments', 0)
        if num_comments > 3:
            base_score += min(15, num_comments)
        
        # Recency boost
        created_utc = post.get('created_utc', 0)
        hours_old = (time.time() - created_utc) / 3600
        if hours_old < 24:
            base_score += 15
        elif hours_old < 72:
            base_score += 10
        
        return min(100, max(1, base_score))
    
    def _deduplicate_leads(self, leads: List[Dict]) -> List[Dict]:
        """Remove duplicate leads"""
        seen_ids = set()
        unique_leads = []
        
        for lead in leads:
            reddit_id = lead.get("reddit_id")
            if reddit_id and reddit_id not in seen_ids:
                seen_ids.add(reddit_id)
                unique_leads.append(lead)
        
        return unique_leads