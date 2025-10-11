import json
import time
import re
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

class RedditScrapingLeadFinder:
    """
    Reddit scraper using F5Bot methodology - direct JSON API access.
    No official API keys needed, bypasses rate limits and costs.
    """
    
    def __init__(self):
        self.processed_ids: Set[str] = set()
        self.session = requests.Session()
        # F5Bot-style headers to avoid detection
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        self.base_delay = 2  # Increased delay to avoid rate limits
        self.lock = threading.Lock()
    
    def search_leads(self, 
                    keywords: List[str], 
                    subreddits: List[str] = ["all"], 
                    limit: int = 1000,
                    days_back: int = 7) -> List[Dict]:
        """
        Search for leads using F5Bot methodology - direct JSON scraping with better efficiency.
        
        Args:
            keywords: List of keywords to search for
            subreddits: List of subreddit names (without r/)
            limit: Total number of posts/comments to check
            days_back: Number of days to look back (default: 7)
        """
        all_leads = []
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        print(f"🔍 Searching {len(subreddits)} subreddits with F5Bot methodology...")
        
        # Process subreddits in smaller batches to avoid overwhelming Reddit
        batch_size = 5
        for i in range(0, len(subreddits), batch_size):
            batch_subreddits = subreddits[i:i+batch_size]
            
            print(f"Processing batch {i//batch_size + 1}: {', '.join([f'r/{s}' for s in batch_subreddits])}")
            
            for subreddit_name in batch_subreddits:
                try:
                    print(f"  📡 Fetching from r/{subreddit_name}...")
                    
                    # Get posts from this subreddit (focus on posts first as they're more valuable)
                    posts_per_sub = max(10, limit // len(subreddits))
                    posts = self._get_recent_posts(subreddit_name, posts_per_sub)
                    
                    if posts:
                        # Filter posts by date
                        filtered_posts = self._filter_by_date(posts, cutoff_date)
                        post_leads = self._process_posts(filtered_posts, keywords)
                        all_leads.extend(post_leads)
                        print(f"    ✅ Found {len(post_leads)} post leads")
                    else:
                        print(f"    ⚠️  No posts retrieved from r/{subreddit_name}")
                    
                    # Only get comments if we successfully got posts (indicates subreddit is accessible)
                    if posts:
                        comments_per_sub = max(5, limit // (len(subreddits) * 2))  # Fewer comments
                        comments = self._get_recent_comments(subreddit_name, comments_per_sub)
                        
                        if comments:
                            filtered_comments = self._filter_by_date(comments, cutoff_date)
                            comment_leads = self._process_comments(filtered_comments, keywords)
                            all_leads.extend(comment_leads)
                            print(f"    ✅ Found {len(comment_leads)} comment leads")
                    
                    # Longer delay between subreddits to avoid rate limits
                    time.sleep(self.base_delay + 1)
                    
                except Exception as e:
                    print(f"    ❌ Error searching r/{subreddit_name}: {str(e)}")
                    continue
            
            # Longer delay between batches
            if i + batch_size < len(subreddits):
                print(f"  ⏳ Waiting before next batch...")
                time.sleep(5)
        
        return self._deduplicate_leads(all_leads)
    
    def _get_recent_posts(self, subreddit: str, limit: int) -> List[Dict]:
        """Get recent posts using Reddit's JSON API (F5Bot method)."""
        posts = []
        
        try:
            # F5Bot uses multiple endpoints and randomizes approach
            endpoints = [
                f"https://www.reddit.com/r/{subreddit}/new/.json",
                f"https://www.reddit.com/r/{subreddit}/hot/.json",
                f"https://www.reddit.com/r/{subreddit}/.json"
            ]
            
            # Try different endpoints if one fails
            for endpoint in endpoints:
                try:
                    # Add random delay to mimic human behavior
                    time.sleep(self.base_delay + (time.time() % 1))
                    
                    url = f"{endpoint}?limit=25"  # Smaller batches to avoid detection
                    response = self.session.get(url, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('data', {}).get('children'):
                            batch_posts = data['data']['children']
                            posts.extend([post['data'] for post in batch_posts])
                            break
                    elif response.status_code == 403:
                        print(f"Rate limited on r/{subreddit}, trying different approach...")
                        time.sleep(5)  # Wait longer on rate limit
                        continue
                    else:
                        continue
                        
                except requests.exceptions.RequestException as e:
                    print(f"Request failed for r/{subreddit}: {str(e)}")
                    continue
            
            # If we got some posts, try to get more with pagination
            if posts and len(posts) < limit:
                try:
                    after = None
                    for _ in range(3):  # Max 3 additional pages
                        time.sleep(self.base_delay + 1)
                        
                        if after:
                            url = f"https://www.reddit.com/r/{subreddit}/new/.json?limit=25&after={after}"
                        else:
                            url = f"https://www.reddit.com/r/{subreddit}/new/.json?limit=25"
                        
                        response = self.session.get(url, timeout=10)
                        if response.status_code != 200:
                            break
                            
                        data = response.json()
                        if not data.get('data', {}).get('children'):
                            break
                        
                        batch_posts = data['data']['children']
                        posts.extend([post['data'] for post in batch_posts])
                        
                        after = data['data'].get('after')
                        if not after or len(posts) >= limit:
                            break
                            
                except Exception:
                    pass  # Continue with what we have
            
        except Exception as e:
            print(f"Error fetching posts from r/{subreddit}: {str(e)}")
        
        return posts[:limit]
    
    def _filter_by_date(self, items: List[Dict], cutoff_date: datetime) -> List[Dict]:
        """Filter posts/comments by creation date."""
        filtered_items = []
        
        for item in items:
            try:
                created_utc = item.get('created_utc', 0)
                created_date = datetime.fromtimestamp(created_utc)
                
                if created_date >= cutoff_date:
                    filtered_items.append(item)
                    
            except Exception as e:
                # If we can't parse the date, include the item to be safe
                filtered_items.append(item)
                continue
        
        return filtered_items
    
    def _get_recent_comments(self, subreddit: str, limit: int) -> List[Dict]:
        """Get recent comments using Reddit's JSON API."""
        comments = []
        
        try:
            # F5Bot approach: try comments endpoint with careful rate limiting
            time.sleep(self.base_delay + (time.time() % 2))  # Random delay
            
            url = f"https://www.reddit.com/r/{subreddit}/comments/.json?limit=25"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('data', {}).get('children'):
                    batch_comments = data['data']['children']
                    comments.extend([comment['data'] for comment in batch_comments])
            elif response.status_code == 403:
                print(f"Comments endpoint blocked for r/{subreddit}, skipping...")
                return []
            
            # Try to get more comments if needed and first request succeeded
            if comments and len(comments) < limit:
                try:
                    after = None
                    for _ in range(2):  # Max 2 additional pages for comments
                        time.sleep(self.base_delay + 2)
                        
                        if after:
                            url = f"https://www.reddit.com/r/{subreddit}/comments/.json?limit=25&after={after}"
                        else:
                            continue  # We already got the first page
                        
                        response = self.session.get(url, timeout=10)
                        if response.status_code != 200:
                            break
                            
                        data = response.json()
                        if not data.get('data', {}).get('children'):
                            break
                        
                        batch_comments = data['data']['children']
                        comments.extend([comment['data'] for comment in batch_comments])
                        
                        after = data['data'].get('after')
                        if not after or len(comments) >= limit:
                            break
                            
                except Exception:
                    pass  # Continue with what we have
            
        except Exception as e:
            print(f"Error fetching comments from r/{subreddit}: {str(e)}")
        
        return comments[:limit]
    
    def _process_posts(self, posts: List[Dict], keywords: List[str]) -> List[Dict]:
        """Process Reddit posts and check for keyword matches."""
        leads = []
        
        for post in posts:
            try:
                # Combine title and selftext for matching
                title = post.get('title', '')
                selftext = post.get('selftext', '')
                full_text = f"{title} {selftext}".lower()
                
                matched_keywords = self._find_matching_keywords(full_text, keywords)
                if not matched_keywords:
                    continue
                
                # Calculate relevance score
                relevance_score = self._calculate_post_relevance_score(
                    full_text, matched_keywords, post
                )
                
                lead = {
                    "id": f"post_{post['id']}",
                    "source_method": "scrape_json",
                    "title": title,
                    "content": selftext[:500],  # Limit content length
                    "url": f"https://reddit.com{post.get('permalink', '')}",
                    "author": post.get('author', '[deleted]'),
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
                        "upvote_ratio": post.get('upvote_ratio', 0),
                        "is_self": post.get('is_self', False),
                        "domain": post.get('domain', ''),
                        "url": post.get('url', '')
                    }
                }
                
                leads.append(lead)
                
            except Exception as e:
                print(f"Error processing post {post.get('id', 'unknown')}: {str(e)}")
                continue
        
        return leads
    
    def _process_comments(self, comments: List[Dict], keywords: List[str]) -> List[Dict]:
        """Process Reddit comments and check for keyword matches."""
        leads = []
        
        for comment in comments:
            try:
                body = comment.get('body', '')
                if not body or body in ['[deleted]', '[removed]']:
                    continue
                
                matched_keywords = self._find_matching_keywords(body.lower(), keywords)
                if not matched_keywords:
                    continue
                
                relevance_score = self._calculate_comment_relevance_score(
                    body, matched_keywords, comment
                )
                
                # Try to get parent post title for context
                parent_title = "Unknown Post"
                link_id = comment.get('link_id', '').replace('t3_', '')
                if link_id:
                    parent_title = f"Post ID: {link_id}"
                
                lead = {
                    "id": f"comment_{comment['id']}",
                    "source_method": "scrape_json",
                    "title": f"Comment in: {parent_title[:100]}...",
                    "content": body[:500],
                    "url": f"https://reddit.com{comment.get('permalink', '')}",
                    "author": comment.get('author', '[deleted]'),
                    "subreddit": comment.get('subreddit', ''),
                    "type": "comment",
                    "hotness_score": relevance_score,
                    "keywords_matched": matched_keywords,
                    "created_date": datetime.fromtimestamp(comment.get('created_utc', 0)).isoformat(),
                    "confidence_score": len(matched_keywords) / len(keywords),
                    "upvotes": comment.get('score', 0),
                    "raw_data": {
                        "reddit_id": comment['id'],
                        "parent_id": comment.get('parent_id', ''),
                        "link_id": comment.get('link_id', '')
                    }
                }
                
                leads.append(lead)
                
            except Exception as e:
                print(f"Error processing comment {comment.get('id', 'unknown')}: {str(e)}")
                continue
        
        return leads
    
    def _find_matching_keywords(self, text: str, keywords: List[str]) -> List[str]:
        """Find which keywords match in the given text with context awareness."""
        matched = []
        
        for keyword in keywords:
            # Simple keyword matching
            if keyword.lower() in text:
                matched.append(keyword)
                continue
            
            # Fuzzy matching for multi-word keywords
            keyword_words = keyword.lower().split()
            if len(keyword_words) > 1:
                if all(word in text for word in keyword_words):
                    matched.append(keyword)
        
        return matched
    
    def _calculate_post_relevance_score(self, text: str, keywords: List[str], post: Dict) -> int:
        """Calculate relevance score for a post based on various factors."""
        base_score = len(keywords) * 20  # Base score from keyword matches
        
        # Boost for question indicators
        question_indicators = ["how", "what", "where", "when", "why", "which", "?", "help", "advice"]
        if any(indicator in text for indicator in question_indicators):
            base_score += 20
        
        # Boost for problem indicators
        problem_indicators = ["problem", "issue", "trouble", "struggling", "difficult", "challenge"]
        if any(indicator in text for indicator in problem_indicators):
            base_score += 15
        
        # Boost for solution-seeking language
        solution_indicators = ["recommend", "suggestion", "alternative", "better", "tool", "software"]
        if any(indicator in text for indicator in solution_indicators):
            base_score += 25
        
        # Factor in Reddit engagement
        score = post.get('score', 0)
        if score > 10:
            base_score += min(10, score // 5)
        
        num_comments = post.get('num_comments', 0)
        if num_comments > 5:
            base_score += min(10, num_comments // 2)
        
        # Boost for recent posts (within last 24 hours)
        created_utc = post.get('created_utc', 0)
        hours_old = (time.time() - created_utc) / 3600
        if hours_old < 24:
            base_score += 10
        
        return min(100, max(1, base_score))
    
    def _calculate_comment_relevance_score(self, text: str, keywords: List[str], comment: Dict) -> int:
        """Calculate relevance score for a comment."""
        base_score = len(keywords) * 15
        
        # Comments are generally less valuable than posts
        question_indicators = ["how", "what", "help", "advice", "recommend"]
        if any(indicator in text.lower() for indicator in question_indicators):
            base_score += 15
        
        # Factor in comment engagement
        score = comment.get('score', 0)
        if score > 5:
            base_score += min(10, score // 2)
        
        # Boost for recent comments
        created_utc = comment.get('created_utc', 0)
        hours_old = (time.time() - created_utc) / 3600
        if hours_old < 12:
            base_score += 5
        
        return min(100, max(1, base_score))
    
    def _deduplicate_leads(self, leads: List[Dict]) -> List[Dict]:
        """Remove duplicate leads based on URL and content similarity."""
        seen_urls = set()
        unique_leads = []
        
        for lead in leads:
            if lead["url"] not in seen_urls:
                seen_urls.add(lead["url"])
                unique_leads.append(lead)
        
        return unique_leads
    
    def get_posts_by_ids(self, post_ids: List[str]) -> List[Dict]:
        """
        Get specific posts by their IDs using F5Bot batch method.
        This is more efficient for continuous monitoring.
        """
        posts = []
        
        # Process in batches of 100 (Reddit's limit)
        for i in range(0, len(post_ids), 100):
            batch_ids = post_ids[i:i+100]
            
            # Format IDs with t3_ prefix
            formatted_ids = [f"t3_{pid}" if not pid.startswith('t3_') else pid for pid in batch_ids]
            ids_param = ','.join(formatted_ids)
            
            try:
                url = f"https://api.reddit.com/api/info.json?id={ids_param}"
                response = self.session.get(url)
                response.raise_for_status()
                
                data = response.json()
                batch_posts = data.get('data', {}).get('children', [])
                posts.extend([post['data'] for post in batch_posts])
                
                time.sleep(0.5)  # Small delay between batches
                
            except Exception as e:
                print(f"Error fetching batch of posts: {str(e)}")
                continue
        
        return posts
    
    def monitor_continuous(self, 
                          keywords: List[str], 
                          subreddits: List[str],
                          interval_minutes: int = 5,
                          days_back: int = 1,
                          callback=None):
        """
        Continuously monitor Reddit for new leads using F5Bot methodology.
        More efficient than repeated searches - tracks latest IDs and fetches new content.
        
        Args:
            keywords: Keywords to monitor
            subreddits: Subreddits to monitor
            interval_minutes: How often to check for new content
            days_back: Only process content from this many days back
            callback: Function to call when new leads are found
        """
        print(f"Starting F5Bot-style continuous monitoring for keywords: {keywords}")
        print(f"Monitoring subreddits: {subreddits}")
        print(f"Check interval: {interval_minutes} minutes")
        
        # Track latest IDs for each subreddit
        latest_post_ids = {}
        latest_comment_ids = {}
        
        # Initialize with current latest IDs
        for subreddit in subreddits:
            try:
                recent_posts = self._get_recent_posts(subreddit, 1)
                if recent_posts:
                    latest_post_ids[subreddit] = recent_posts[0]['id']
                
                recent_comments = self._get_recent_comments(subreddit, 1)
                if recent_comments:
                    latest_comment_ids[subreddit] = recent_comments[0]['id']
                    
            except Exception as e:
                print(f"Error initializing monitoring for r/{subreddit}: {str(e)}")
        
        while True:
            try:
                all_new_leads = []
                cutoff_date = datetime.now() - timedelta(days=days_back)
                
                for subreddit in subreddits:
                    # Check for new posts since last check
                    new_posts = self._get_new_posts_since(subreddit, latest_post_ids.get(subreddit))
                    if new_posts:
                        # Filter by date
                        filtered_posts = self._filter_by_date(new_posts, cutoff_date)
                        if filtered_posts:
                            latest_post_ids[subreddit] = new_posts[0]['id']
                            post_leads = self._process_posts(filtered_posts, keywords)
                            all_new_leads.extend(post_leads)
                    
                    # Check for new comments since last check
                    new_comments = self._get_new_comments_since(subreddit, latest_comment_ids.get(subreddit))
                    if new_comments:
                        # Filter by date
                        filtered_comments = self._filter_by_date(new_comments, cutoff_date)
                        if filtered_comments:
                            latest_comment_ids[subreddit] = new_comments[0]['id']
                            comment_leads = self._process_comments(filtered_comments, keywords)
                            all_new_leads.extend(comment_leads)
                    
                    time.sleep(1)  # Small delay between subreddits
                
                if all_new_leads:
                    print(f"Found {len(all_new_leads)} new leads")
                    
                    # Call callback if provided
                    if callback:
                        callback(all_new_leads)
                    else:
                        # Default: save to file
                        self._save_leads_to_file(all_new_leads, "continuous_leads.json")
                
                # Wait before next check
                time.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                print("Monitoring stopped by user")
                break
            except Exception as e:
                print(f"Error in continuous monitoring: {str(e)}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    def _get_new_posts_since(self, subreddit: str, last_id: Optional[str]) -> List[Dict]:
        """Get new posts since the last known ID."""
        if not last_id:
            return self._get_recent_posts(subreddit, 25)
        
        try:
            url = f"https://www.reddit.com/r/{subreddit}/new/.json?limit=100"
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            posts = [post['data'] for post in data.get('data', {}).get('children', [])]
            
            # Find posts newer than last_id
            new_posts = []
            for post in posts:
                if post['id'] == last_id:
                    break
                new_posts.append(post)
            
            return new_posts
            
        except Exception as e:
            print(f"Error getting new posts from r/{subreddit}: {str(e)}")
            return []
    
    def _get_new_comments_since(self, subreddit: str, last_id: Optional[str]) -> List[Dict]:
        """Get new comments since the last known ID."""
        if not last_id:
            return self._get_recent_comments(subreddit, 25)
        
        try:
            url = f"https://www.reddit.com/r/{subreddit}/comments/.json?limit=100"
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            comments = [comment['data'] for comment in data.get('data', {}).get('children', [])]
            
            # Find comments newer than last_id
            new_comments = []
            for comment in comments:
                if comment['id'] == last_id:
                    break
                new_comments.append(comment)
            
            return new_comments
            
        except Exception as e:
            print(f"Error getting new comments from r/{subreddit}: {str(e)}")
            return []
    
    def _save_leads_to_file(self, leads: List[Dict], filename: str):
        """Save leads to a JSON file."""
        try:
            # Load existing leads if file exists
            existing_leads = []
            try:
                with open(filename, "r") as f:
                    existing_leads = json.load(f)
            except FileNotFoundError:
                pass
            
            # Append new leads
            all_leads = existing_leads + leads
            
            # Save back to file
            with open(filename, "w") as f:
                json.dump(all_leads, f, indent=2)
                
            print(f"Saved {len(leads)} new leads to {filename}")
            
        except Exception as e:
            print(f"Error saving leads to file: {str(e)}")

def search_reddit_leads(keywords: List[str], 
                       subreddits: List[str], 
                       days_back: int = 7, 
                       limit: int = 500) -> List[Dict]:
    """
    Convenient function to search Reddit leads with custom parameters.
    
    Args:
        keywords: List of keywords to search for
        subreddits: List of subreddit names (without r/)
        days_back: Number of days to look back (default: 7)
        limit: Maximum number of posts/comments to check (default: 500)
    
    Returns:
        List of lead dictionaries
    
    Example:
        leads = search_reddit_leads(
            keywords=["SaaS", "marketing tool", "CRM"],
            subreddits=["entrepreneur", "startups", "marketing"],
            days_back=4,
            limit=1000
        )
    """
    finder = RedditScrapingLeadFinder()
    return finder.search_leads(keywords, subreddits, limit, days_back)

def main():
    """Example usage of the F5Bot-style Reddit Scraper with customizable parameters."""
    finder = RedditScrapingLeadFinder()
    
    # Customizable configuration
    keywords = [
        "SaaS", "marketing tool", "email automation", "CRM", 
        "analytics", "lead generation", "customer acquisition",
        "growth hacking", "B2B software", "subscription service"
    ]
    
    # Specific subreddits to target
    subreddits = [
        "entrepreneur", "startups", "marketing", "SaaS", 
        "smallbusiness", "digitalnomad", "webdev", "business"
    ]
    
    # Customizable days to look back (change this value as needed)
    days_back = 4  # Look back 4 days as requested
    
    print("F5Bot-style Reddit scraping - no API keys needed!")
    print(f"Searching for leads using direct JSON endpoints...")
    print(f"Keywords: {', '.join(keywords)}")
    print(f"Subreddits: {', '.join([f'r/{sub}' for sub in subreddits])}")
    print(f"Looking back: {days_back} days")
    
    # Search with custom parameters
    leads = finder.search_leads(
        keywords=keywords, 
        subreddits=subreddits, 
        limit=500,
        days_back=days_back
    )
    
    print(f"\nFound {len(leads)} leads using JSON scraping:")
    for lead in leads[:5]:  # Show first 5
        created_date = datetime.fromisoformat(lead['created_date'].replace('Z', '+00:00'))
        days_ago = (datetime.now() - created_date.replace(tzinfo=None)).days
        print(f"- {lead['title'][:60]}... (Score: {lead['hotness_score']}) - r/{lead['subreddit']} ({days_ago}d ago)")
    
    # Save to file
    with open("scraping_leads.json", "w") as f:
        json.dump(leads, f, indent=2)
    
    print(f"\nAll leads saved to scraping_leads.json")
    
    # Show keyword match statistics
    keyword_stats = {}
    for lead in leads:
        for keyword in lead['keywords_matched']:
            keyword_stats[keyword] = keyword_stats.get(keyword, 0) + 1
    
    if keyword_stats:
        print(f"\nKeyword match statistics:")
        for keyword, count in sorted(keyword_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"  {keyword}: {count} matches")
    
    # Demonstrate continuous monitoring
    print("\nTo start continuous F5Bot-style monitoring, uncomment the line below:")
    print("# finder.monitor_continuous(keywords, subreddits, interval_minutes=5)")
    
    # Example of getting specific posts by ID (F5Bot method)
    if leads:
        print(f"\nDemonstrating F5Bot batch ID fetching...")
        sample_ids = [lead['raw_data']['reddit_id'] for lead in leads[:3]]
        batch_posts = finder.get_posts_by_ids(sample_ids)
        print(f"Successfully fetched {len(batch_posts)} posts by ID")

if __name__ == "__main__":
    main()