#!/usr/bin/env python3
"""
Setup script for Reddit Lead Finder v2 with multi-tenant SQLite database
"""

import os
import sys
from database import Database
from deepseek_analyzer import DeepSeekAnalyzer

def setup_database():
    """Initialize the database"""
    print("🗄️  Setting up SQLite database...")
    
    try:
        db = Database()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def test_ai_connection():
    """Test DeepSeek AI connection"""
    print("🤖 Testing DeepSeek AI connection...")
    
    try:
        ai = DeepSeekAnalyzer()
        
        # Test with a simple analysis
        test_result = ai.analyze_website_for_keywords(
            "https://example.com", 
            "Test Company"
        )
        
        if test_result:
            print("✅ DeepSeek AI connection successful")
            return True
        else:
            print("⚠️  DeepSeek AI returned empty result")
            return False
            
    except Exception as e:
        print(f"❌ DeepSeek AI connection failed: {e}")
        return False

def create_sample_data():
    """Create sample user and business for testing"""
    print("👤 Creating sample data...")
    
    try:
        db = Database()
        
        # Create sample user
        user_id = db.create_user("test@example.com", "password123")
        if user_id:
            print(f"✅ Sample user created with ID: {user_id}")
            
            # Create sample business
            business_id = db.create_business(
                user_id=user_id,
                name="Sample Business",
                website="https://example.com",
                description="A sample business for testing"
            )
            
            if business_id:
                print(f"✅ Sample business created with ID: {business_id}")
                
                # Add sample keywords
                sample_keywords = [
                    "marketing automation",
                    "lead generation", 
                    "customer acquisition",
                    "sales funnel",
                    "conversion optimization"
                ]
                
                for keyword in sample_keywords:
                    db.add_keyword(business_id, keyword, "manual")
                
                print(f"✅ Added {len(sample_keywords)} sample keywords")
                
                # Add sample subreddits
                sample_subreddits = [
                    "entrepreneur",
                    "marketing",
                    "startups",
                    "smallbusiness",
                    "sales"
                ]
                
                for subreddit in sample_subreddits:
                    db.add_subreddit(business_id, subreddit, "manual")
                
                print(f"✅ Added {len(sample_subreddits)} sample subreddits")
                
                return True
        
        return False
        
    except Exception as e:
        print(f"❌ Sample data creation failed: {e}")
        return False

def check_environment():
    """Check environment variables"""
    print("🔧 Checking environment variables...")
    
    required_vars = [
        "DEEPSEEK_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("   Please check your .env file")
        return False
    else:
        print("✅ All required environment variables found")
        return True

def main():
    """Main setup function"""
    print("🚀 Reddit Lead Finder v2 Setup")
    print("=" * 50)
    
    success = True
    
    # Check environment
    if not check_environment():
        success = False
    
    # Setup database
    if not setup_database():
        success = False
    
    # Test AI connection
    if not test_ai_connection():
        print("⚠️  AI connection failed - you may need to update DEEPSEEK_API_KEY in .env")
        success = False
    
    # Create sample data
    if success:
        create_sample = input("\n📝 Create sample data for testing? (y/n): ").lower().strip()
        if create_sample == 'y':
            create_sample_data()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Setup completed successfully!")
        print("\n🎯 Next steps:")
        print("   1. Run the start script: ./start-app.sh")
        print("   2. Visit http://localhost:3050 to access the app")
        print("\n📚 Sample login credentials:")
        print("   Email: test@example.com")
        print("   Password: password123")
    else:
        print("❌ Setup completed with errors")
        print("   Please fix the issues above and run setup again")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)