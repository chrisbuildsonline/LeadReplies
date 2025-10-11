"""Example usage of the Reddit leads finder."""
from reddit_leads.api import RedditLeadsAPI
from reddit_leads.main import save_leads_to_file
import json

def example_basic_search():
    """Example of basic lead search."""
    api = RedditLeadsAPI()
    
    # Define search parameters
    subreddits = ['entrepreneur', 'smallbusiness', 'startups']
    keywords = ['need help with', 'looking for', 'advice needed']
    
    # Search for leads
    results = api.search_leads(
        subreddits=subreddits,
        keywords=keywords,
        max_results=20,
        min_score=2
    )
    
    if results['success']:
        print(f"Found {results['total_leads']} leads")
        
        # Display first few leads
        for i, lead in enumerate(results['leads'][:5], 1):
            print(f"\n{i}. {lead['title']}")
            print(f"   Subreddit: r/{lead['subreddit']}")
            print(f"   Score: {lead['score']}")
            print(f"   Keywords: {', '.join(lead['matched_keywords'])}")
            print(f"   URL: {lead['url']}")
        
        # Save to file
        leads_data = [lead for lead in results['leads']]
        filename = save_leads_to_file(leads_data)
        print(f"\nLeads saved to: {filename}")
    
    else:
        print(f"Error: {results['error']}")

def example_advanced_search():
    """Example of advanced lead search with filtering."""
    api = RedditLeadsAPI()
    
    # Search with more specific parameters
    results = api.search_leads(
        subreddits=['webdev', 'freelance', 'digitalnomad'],
        keywords=['web developer', 'need a developer', 'hire someone'],
        max_results=30,
        time_filter='week',
        sort='top',
        min_score=5,
        exclude_keywords=['free', 'no budget', 'exposure']
    )
    
    if results['success']:
        print(f"Found {results['total_leads']} high-quality leads")
        
        # Further filter the results
        filtered_leads = api.filter_leads(
            results['leads'],
            min_score=10,
            max_age_days=3,
            exclude_authors=['AutoModerator', 'deleted']
        )
        
        print(f"After filtering: {len(filtered_leads)} premium leads")
        
        for lead in filtered_leads:
            print(f"\n• {lead['title']}")
            print(f"  r/{lead['subreddit']} | Score: {lead['score']} | Author: u/{lead['author']}")
    
    else:
        print(f"Error: {results['error']}")

def example_user_research():
    """Example of researching a potential lead's profile."""
    api = RedditLeadsAPI()
    
    username = "example_user"  # Replace with actual username
    user_info = api.get_user_info(username)
    
    if 'error' not in user_info:
        print(f"User: u/{user_info['name']}")
        print(f"Comment Karma: {user_info['comment_karma']}")
        print(f"Link Karma: {user_info['link_karma']}")
        print(f"Account Age: {user_info['created_utc']}")
        print(f"Verified: {user_info['is_verified']}")
    else:
        print(f"Error getting user info: {user_info['error']}")

if __name__ == "__main__":
    print("=== Basic Search Example ===")
    example_basic_search()
    
    print("\n=== Advanced Search Example ===")
    example_advanced_search()
    
    print("\n=== User Research Example ===")
    example_user_research()