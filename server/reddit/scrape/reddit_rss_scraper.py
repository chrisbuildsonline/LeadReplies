#!/usr/bin/env python3
"""
Alternative Reddit scraper using RSS feeds - F5Bot style but more reliable.
RSS feeds are less likely to be blocked and don't require API keys.
"""

import requests
import xml.etree.ElementTree as ET
import time
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from urllib.parse import urlparse, parse_qs
import json

class RedditRSSScaper:
    """
    F5Bot-style Reddit scraper using RSS feeds instead of JSON API.
    More reliable and less likely to be blocked.
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/rss+xml, application/xml, text/xml',
            'Accept-Language': 'en-US,en;q=0.9',
        })
        self.base_delay = 1
    
    def search_leads(self, 
                    keywords: List[str], 
                    subreddits: List[str], 
                    days_back: int = 7,
                    limit_per_sub: int = 50) -> List[Dict]:
        """
        Search for leads using RSS feeds from multiple subreddits.
        
        Args:
            keywords: List of keywords to search for
            subreddits: List of subreddit names (without r/)
            days_back: Number of days to look back
            limit_per_sub: Max items to fetch per subreddit
        """
        all_leads = []
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        print(f"🔍 F5Bot-style RSS scraping from {len(subreddits)} subreddits...")
        
        for subreddit in subreddits:
            try:
                print(f"  📡 Fetching RSS from r/{subreddit}...")
                
                # Try multiple RSS endpoints
                rss_urls = [
                    f"https://www.reddit.com/r/{subreddit}/new/.rss?limit={min(limit_per_sub, 100)}",
                    f"https://www.reddit.com/r/{subreddit}/.rss?limit={min(limit_per_sub, 100)}",
                    f"https://www.reddit.com/r/{subreddit}/hot/.rss?limit={min(limit_per_sub, 100)}"
                ]
                
                posts = []
                for rss_url in rss_urls:
                    try:
                        time.sleep(self.base_delay)
                        response = self.session.get(rss_url, timeout=10)
                        
                        if response.status_code == 200:
                            posts = self._parse_rss_feed(response.text, subreddit)
                            if posts:
                                print(f"    ✅ Got {len(posts)} posts from RSS")
                                break
                        elif response.status_code == 403:
                            print(f"    ⚠️  RSS blocked for r/{subreddit}")
                            continue
                    except Exception as e:
                        continue
                
                if posts:
                    # Filter by date and process
                    filtered_posts = self._filter_by_date(posts, cutoff_date)
                    leads = self._process_posts(filtered_posts, keywords)
                    all_leads.extend(leads)
                    print(f"    ✅ Found {len(leads)} leads")
                else:
                    print(f"    ❌ No posts retrieved from r/{subreddit}")
                
            except Exception as e:
                print(f"    ❌ Error with r/{subreddit}: {str(e)}")
                continue
        
        return self._deduplicate_leads(all_leads)
    
    def _parse_rss_feed(self, rss_content: str, subreddit: str) -> List[Dict]:
        """Parse RSS feed content into post dictionaries."""
        posts = []
        
        try:
            root = ET.fromstring(rss_content)
            
            # Handle both RSS and Atom feeds
            items = root.findall('.//item') or root.findall('.//{http://www.w3.org/2005/Atom}entry')
            
            for item in items:
                try:
                    # Extract post data from RSS
                    title_elem = item.find('title') or item.find('.//{http://www.w3.org/2005/Atom}title')
                    link_elem = item.find('link') or item.find('.//{http://www.w3.org/2005/Atom}link')
                    desc_elem = item.find('description') or item.find('.//{http://www.w3.org/2005/Atom}content')
                    date_elem = item.find('pubDate') or item.find('.//{http://www.w3.org/2005/Atom}published')
                    author_elem = item.find('.//{http://purl.org/dc/elements/1.1/}creator') or item.find('.//{http://www.w3.org/2005/Atom}author')
                    
                    if not title_elem or not link_elem:
                        continue
                    
                    title = title_elem.text or ""
                    link = link_elem.text or (link_elem.get('href') if link_elem.get('href') else "")
                    description = desc_elem.text or "" if desc_elem is not None else ""
                    
                    # Extract Reddit post ID from URL
                    post_id = self._extract_post_id_from_url(link)
                    
                    # Parse date
                    pub_date = None
                    if date_elem is not None and date_elem.text:
                        try:
                            # Try different date formats
                            date_str = date_elem.text
                            for fmt in ['%a, %d %b %Y %H:%M:%S %z', '%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%dT%H:%M:%SZ']:
                                try:
                                    pub_date = datetime.strptime(date_str, fmt)
                                    break
                                except ValueError:
                                    continue
                        except:
                            pub_date = datetime.now()
                    
                    # Extract author
                    author = "unknown"
                    if author_elem is not None:
                        author = author_elem.text or "unknown"
                    
                    # Clean up description (remove HTML tags)
                    clean_description = re.sub(r'<[^>]+>', '', description)
                    clean_description = re.sub(r'&[a-zA-Z0-9#]+;', ' ', clean_description)
                    
                    post = {
                        'id': post_id or f"rss_{hash(link)}",
                        'title': title,
                        'selftext': clean_description[:1000],  # Limit length
                        'url': link,
                        'author': author,
                        'subreddit': subreddit,
                        'created_utc': pub_date.timestamp() if pub_date else time.time(),
                        'score': 1,  # Default score for RSS items
                        'num_comments': 0,  # Not available in RSS
                        'permalink': self._extract_permalink_from_url(link),
                        'upvote_ratio': 0.5,  # Default
                        'is_self': True,
                        'domain': 'reddit.com'
                    }
                    
                    posts.append(post)
                    
                except Exception as e:
                    continue
            
        except ET.ParseError as e:
            print(f"    ⚠️  RSS parse error: {str(e)}")
        except Exception as e:
            print(f"    ⚠️  RSS processing error: {str(e)}")
        
        return posts
    
    def _extract_post_id_from_url(self, url: str) -> Optional[str]:
        """Extract Reddit post ID from URL."""
        try:
            # Reddit URLs typically have format: /r/subreddit/comments/POST_ID/title/
            match = re.search(r'/comments/([a-zA-Z0-9]+)/', url)
            if match:
                return match.group(1)
        except:
            pass
        return None
    
    def _extract_permalink_from_url(self, url: str) -> str:
        """Extract permalink from full URL."""
        try:
            parsed = urlparse(url)
            return parsed.path
        except:
            return url
    
    def _filter_by_date(self, posts: List[Dict], cutoff_date: datetime) -> List[Dict]:
        """Filter posts by creation date."""
        filtered = []
        
        for post in posts:
            try:
                created_utc = post.get('created_utc', 0)
                created_date = datetime.fromtimestamp(created_utc)
                
                if created_date >= cutoff_date:
                    filtered.append(post)
            except:
                # If date parsing fails, include the post
                filtered.append(post)
        
        return filtered
    
    def _process_posts(self, posts: List[Dict], keywords: List[str]) -> List[Dict]:
        """Process posts and find keyword matches."""
        leads = []
        
        for post in posts:
            try:
                title = post.get('title', '')
                selftext = post.get('selftext', '')
                full_text = f"{title} {selftext}".lower()
                
                matched_keywords = self._find_matching_keywords(full_text, keywords)
                if not matched_keywords:
                    continue
                
                # Calculate relevance score
                relevance_score = self._calculate_relevance_score(full_text, matched_keywords, post)
                
                lead = {
                    "id": f"rss_post_{post['id']}",
                    "source_method": "rss_scrape",
                    "title": title,
                    "content": selftext[:500],
                    "url": post.get('url', ''),
                    "author": post.get('author', 'unknown'),
                    "subreddit": post.get('subreddit', ''),
                    "type": "post",
                    "hotness_score": relevance_score,
                    "keywords_matched": matched_keywords,
                    "created_date": datetime.fromtimestamp(post.get('created_utc', 0)).isoformat(),
                    "confidence_score": len(matched_keywords) / len(keywords),
                    "upvotes": post.get('score', 0),
                    "num_comments": post.get('num_comments', 0),
                    "raw_data": {
                        "reddit_id": post['id'],
                        "permalink": post.get('permalink', ''),
                        "domain": post.get('domain', ''),
                        "is_self": post.get('is_self', True)
                    }
                }
                
                leads.append(lead)
                
            except Exception as e:
                continue
        
        return leads
    
    def _find_matching_keywords(self, text: str, keywords: List[str]) -> List[str]:
        """Find matching keywords in text."""
        matched = []
        
        for keyword in keywords:
            if keyword.lower() in text:
                matched.append(keyword)
                continue
            
            # Multi-word keyword matching
            keyword_words = keyword.lower().split()
            if len(keyword_words) > 1:
                if all(word in text for word in keyword_words):
                    matched.append(keyword)
        
        return matched
    
    def _calculate_relevance_score(self, text: str, keywords: List[str], post: Dict) -> int:
        """Calculate relevance score for a post."""
        base_score = len(keywords) * 20
        
        # Question indicators
        question_indicators = ["how", "what", "where", "when", "why", "which", "?", "help", "advice"]
        if any(indicator in text for indicator in question_indicators):
            base_score += 20
        
        # Problem indicators
        problem_indicators = ["problem", "issue", "trouble", "struggling", "difficult", "challenge"]
        if any(indicator in text for indicator in problem_indicators):
            base_score += 15
        
        # Solution-seeking language
        solution_indicators = ["recommend", "suggestion", "alternative", "better", "tool", "software"]
        if any(indicator in text for indicator in solution_indicators):
            base_score += 25
        
        # Recent posts get boost
        created_utc = post.get('created_utc', 0)
        hours_old = (time.time() - created_utc) / 3600
        if hours_old < 24:
            base_score += 10
        
        return min(100, max(1, base_score))
    
    def _deduplicate_leads(self, leads: List[Dict]) -> List[Dict]:
        """Remove duplicate leads."""
        seen_urls = set()
        unique_leads = []
        
        for lead in leads:
            url = lead.get("url", "")
            if url not in seen_urls:
                seen_urls.add(url)
                unique_leads.append(lead)
        
        return unique_leads

def search_reddit_leads_rss(keywords: List[str], 
                           subreddits: List[str], 
                           days_back: int = 7, 
                           limit_per_sub: int = 50) -> List[Dict]:
    """
    Convenient function to search Reddit leads using RSS feeds.
    More reliable than JSON API scraping.
    
    Args:
        keywords: List of keywords to search for
        subreddits: List of subreddit names (without r/)
        days_back: Number of days to look back
        limit_per_sub: Max items per subreddit
    
    Returns:
        List of lead dictionaries
    """
    scraper = RedditRSSScaper()
    return scraper.search_leads(keywords, subreddits, days_back, limit_per_sub)

if __name__ == "__main__":
    # Test the RSS scraper
    keywords = ["SaaS", "marketing tool", "CRM", "automation"]
    subreddits = ["entrepreneur", "startups", "marketing", "SaaS"]
    
    print("Testing F5Bot-style RSS scraper...")
    leads = search_reddit_leads_rss(keywords, subreddits, days_back=3, limit_per_sub=25)
    
    print(f"\nFound {len(leads)} leads using RSS scraping:")
    for lead in leads[:5]:
        print(f"- {lead['title'][:60]}... (Score: {lead['hotness_score']}) - r/{lead['subreddit']}")
    
    # Save results
    with open("rss_leads.json", "w") as f:
        json.dump(leads, f, indent=2)
    
    print(f"\nResults saved to rss_leads.json")