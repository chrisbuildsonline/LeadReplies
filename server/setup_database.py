#!/usr/bin/env python3
"""
Database setup script for Reddit Lead Finder MVP.
Run this first to initialize the database and add initial data.
"""

from database import Database

def setup_initial_data():
    """Setup initial keywords and subreddits"""
    db = Database()
    
    print("🔧 Setting up initial data...")
    
    # Initial keywords for SaaS/business tools
    initial_keywords = [
        # Direct tool searches
        "SaaS", "software as a service", "business tool", "marketing tool",
        "CRM", "customer relationship management", "email automation",
        "marketing automation", "lead generation", "analytics tool",
        
        # Problem-based keywords
        "struggling with", "need help with", "looking for", "recommend",
        "alternative to", "better than", "replacement for",
        "automate", "streamline", "efficiency", "productivity",
        
        # Business pain points
        "manual process", "time consuming", "difficult to track",
        "losing customers", "poor conversion", "need to scale",
        "growing business", "startup tools", "small business software"
    ]
    
    # Target subreddits
    initial_subreddits = [
        # Business & Entrepreneurship
        "entrepreneur", "startups", "smallbusiness", "business",
        "EntrepreneurRideAlong", "sweatystartup",
        
        # Marketing & Sales
        "marketing", "digitalmarketing", "emailmarketing", "sales",
        "PPC", "SEO", "socialmedia", "content_marketing",
        
        # Tech & SaaS
        "SaaS", "webdev", "programming", "technology",
        "digitalnomad", "remotework",
        
        # Industry Specific
        "ecommerce", "shopify", "amazon", "dropshipping",
        "realestate", "investing", "personalfinance"
    ]
    
    # Add keywords
    print(f"📝 Adding {len(initial_keywords)} keywords...")
    for keyword in initial_keywords:
        db.add_keyword(keyword)
    
    # Add subreddits
    print(f"📝 Adding {len(initial_subreddits)} subreddits...")
    for subreddit in initial_subreddits:
        db.add_subreddit(subreddit)
    
    print("✅ Initial data setup complete!")
    
    # Show summary
    active_keywords = db.get_active_keywords()
    active_subreddits = db.get_active_subreddits()
    
    print(f"\n📊 Summary:")
    print(f"   Keywords: {len(active_keywords)}")
    print(f"   Subreddits: {len(active_subreddits)}")
    
    print(f"\n🔍 Sample keywords: {', '.join(active_keywords[:5])}...")
    print(f"🎯 Sample subreddits: {', '.join([f'r/{s}' for s in active_subreddits[:5]])}...")

def main():
    """Main setup function"""
    print("🚀 Reddit Lead Finder MVP - Database Setup")
    print("=" * 50)
    
    try:
        # Initialize database
        db = Database()
        print("📊 Initializing database tables...")
        db.init_database()
        
        # Setup initial data
        setup_initial_data()
        
        print(f"\n✅ Setup complete! You can now:")
        print(f"   1. Run the scheduler: python scheduler.py")
        print(f"   2. Test once: python scheduler.py once")
        print(f"   3. View leads: python view_leads.py")
        
    except Exception as e:
        print(f"❌ Setup failed: {str(e)}")
        print(f"\nMake sure PostgreSQL is running and check your .env file:")
        print(f"   DB_HOST=localhost")
        print(f"   DB_NAME=reddit_leads")
        print(f"   DB_USER=postgres")
        print(f"   DB_PASSWORD=your_password")
        print(f"   DB_PORT=5432")

if __name__ == "__main__":
    main()