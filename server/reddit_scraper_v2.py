import requests
import time
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from urllib.parse import quote_plus

class EfficientRedditScraper:
    """
    Efficient Reddit scraper that uses search API to query multiple subreddits in one request.
    Avoids rate limiting by making fewer, more targeted requests.
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
        })
        self.base_delay = 3  # Longer delay to avoid rate limits
    
    def search_leads(self, keywords: List[str], subreddits: List[str], days_back: int = 7) -> List[Dict]:
        """
        Search for leads using Reddit's search API with multiple subreddits in one query.
        Much more efficient than individual subreddit requests.
        """
        all_leads = []
        
        # Create subreddit filter for search
        subreddit_filter = "+".join([f"subreddit:{sub}" for sub in subreddits])
        
        print(f"🔍 Searching {len(subreddits)} subreddits with single query approach...")
        print(f"Subreddits: {', '.join([f'r/{s}' for s in subreddits[:5]])}{'...' if len(subreddits) > 5 else ''}")
        
        # Search for each keyword across all subreddits
        for keyword in keywords:
            try:
                print(f"  🔎 Searching for: '{keyword}'")
                
                # Build search query
                search_query = f'"{keyword}" ({subreddit_filter})'
                
                # Search posts
                posts = self._search_posts(search_query, days_back)
                if posts:
                    post_leads = self._process_posts(posts, [keyword])
                    all_leads.extend(post_leads)
                    print(f"    ✅ Found {len(post_leads)} post leads")
                
                # Add delay between keyword searches
                time.sleep(self.base_delay)
                
            except Exception as e:
                print(f"    ❌ Error searching keyword '{keyword}': {str(e)}")
                continue
        
        return self._deduplicate_leads(all_leads)
    
    def _search_posts(self, query: str, days_back: int, limit: int = 100) -> List[Dict]:
        """Search posts using Reddit's search API"""
        posts = []
        
        try:
            # Calculate time filter
            cutoff_timestamp = int((datetime.now() - timedelta(days=days_back)).timestamp())
            
            # Use Reddit search API
            url = "https://www.reddit.com/search.json"
            params = {
                'q': query,
                'sort': 'new',
                'limit': min(limit, 100),  # Reddit's max limit
                't': 'week' if days_back <= 7 else 'month',
                'type': 'link'
            }
            
            response = self.session.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('data', {}).get('children'):
                    raw_posts = data['data']['children']
                    
                    for post_wrapper in raw_posts:
                        post_data = post_wrapper.get('data', {})
                        
                        # Filter by date
                        created_utc = post_data.get('created_utc', 0)
                        if created_utc >= cutoff_timestamp:
                            posts.append(post_data)
                    
                    print(f"      📊 Retrieved {len(posts)} recent posts")
                else:
                    print(f"      ⚠️  No posts found for query")
            
            elif response.status_code == 429:
                print(f"      ⚠️  Rate limited, waiting...")
                time.sleep(10)
                return []
            else:
                print(f"      ⚠️  Search failed with status {response.status_code}")
                return []
                
        except Exception as e:
            print(f"      ❌ Search error: {str(e)}")
            return []
        
        return posts
    
    def _process_posts(self, posts: List[Dict], keywords: List[str]) -> List[Dict]:
        """Process Reddit posts and create lead objects"""
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
                
                if not matched_keywords:
                    continue
                
                # Calculate relevance score
                relevance_score = self._calculate_relevance_score(full_text, matched_keywords, post)
                
                # Create lead object
                lead = {
                    "reddit_id": post['id'],
                    "service": "reddit",
                    "title": title,
                    "content": selftext[:1000],  # Limit content length
                    "url": f"https://reddit.com{post.get('permalink', '')}",
                    "author": post.get('author', '[deleted]'),
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
                print(f"      ⚠️  Error processing post: {str(e)}")
                continue
        
        return leads
    
    def _calculate_relevance_score(self, text: str, keywords: List[str], post: Dict) -> int:
        """Calculate relevance score for a post"""
        base_score = len(keywords) * 25
        
        # Boost for question indicators
        question_indicators = ["how", "what", "where", "when", "why", "which", "?", "help", "advice", "recommend"]
        if any(indicator in text for indicator in question_indicators):
            base_score += 30
        
        # Boost for problem indicators
        problem_indicators = ["problem", "issue", "trouble", "struggling", "difficult", "challenge", "need"]
        if any(indicator in text for indicator in problem_indicators):
            base_score += 25
        
        # Boost for solution-seeking language
        solution_indicators = ["looking for", "alternative", "better", "tool", "software", "solution", "platform"]
        if any(indicator in text for indicator in solution_indicators):
            base_score += 35
        
        # Factor in Reddit engagement
        score = post.get('score', 0)
        if score > 5:
            base_score += min(15, score // 2)
        
        num_comments = post.get('num_comments', 0)
        if num_comments > 3:
            base_score += min(15, num_comments)
        
        # Boost for recent posts
        created_utc = post.get('created_utc', 0)
        hours_old = (time.time() - created_utc) / 3600
        if hours_old < 24:
            base_score += 15
        elif hours_old < 72:
            base_score += 10
        
        return min(100, max(1, base_score))
    
    def _deduplicate_leads(self, leads: List[Dict]) -> List[Dict]:
        """Remove duplicate leads based on Reddit ID"""
        seen_ids = set()
        unique_leads = []
        
        for lead in leads:
            reddit_id = lead.get("reddit_id")
            if reddit_id and reddit_id not in seen_ids:
                seen_ids.add(reddit_id)
                unique_leads.append(lead)
        
        return unique_leads
    
    def search_by_keyword_batch(self, keywords: List[str], subreddits: List[str], days_back: int = 7) -> List[Dict]:
        """
        Alternative method: Search using combined keyword queries for even better efficiency
        """
        all_leads = []
        
        # Create subreddit filter
        subreddit_filter = "+".join([f"subreddit:{sub}" for sub in subreddits])
        
        # Group keywords into batches to create compound queries
        keyword_batches = [keywords[i:i+3] for i in range(0, len(keywords), 3)]  # Batch of 3 keywords
        
        print(f"🔍 Using batch search with {len(keyword_batches)} keyword batches...")
        
        for batch_idx, keyword_batch in enumerate(keyword_batches):
            try:
                # Create OR query for keywords in this batch
                keyword_query = " OR ".join([f'"{kw}"' for kw in keyword_batch])
                search_query = f'({keyword_query}) ({subreddit_filter})'
                
                print(f"  🔎 Batch {batch_idx + 1}: {', '.join(keyword_batch)}")
                
                posts = self._search_posts(search_query, days_back, limit=150)
                if posts:
                    # Process with all original keywords for matching
                    post_leads = self._process_posts(posts, keywords)
                    all_leads.extend(post_leads)
                    print(f"    ✅ Found {len(post_leads)} leads")
                
                # Longer delay between batches
                time.sleep(self.base_delay + 2)
                
            except Exception as e:
                print(f"    ❌ Error with batch {batch_idx + 1}: {str(e)}")
                continue
        
        return self._deduplicate_leads(all_leads)