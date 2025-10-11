#!/usr/bin/env python3
"""
Complete installation and setup script for Reddit Lead Finder MVP.
This script will guide you through the entire setup process.
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🚀 {title}")
    print(f"{'='*60}")

def print_step(step, description):
    """Print a formatted step"""
    print(f"\n📋 Step {step}: {description}")
    print("-" * 40)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ is required. Please upgrade Python.")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} detected")

def install_requirements():
    """Install Python requirements"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Python packages installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install Python packages")
        return False

def check_postgresql():
    """Check if PostgreSQL is available"""
    try:
        import psycopg2
        print("✅ psycopg2 package available")
        return True
    except ImportError:
        print("❌ psycopg2 not available. Install with: pip install psycopg2-binary")
        return False

def setup_env_file():
    """Setup environment file"""
    env_file = Path(".env")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    print("📝 Creating .env file...")
    
    # Get API key
    anthropic_key = input("Enter your Anthropic API key (or press Enter to skip): ").strip()
    if not anthropic_key:
        anthropic_key = "your_anthropic_api_key_here"
    
    # Get database settings
    print("\n📊 Database Configuration:")
    db_host = input("Database host (default: localhost): ").strip() or "localhost"
    db_name = input("Database name (default: reddit_leads): ").strip() or "reddit_leads"
    db_user = input("Database user (default: postgres): ").strip() or "postgres"
    db_password = input("Database password: ").strip() or "password"
    db_port = input("Database port (default: 5432): ").strip() or "5432"
    
    env_content = f"""# Anthropic API Key for AI analysis
ANTHROPIC_API_KEY={anthropic_key}

# Database Configuration
DB_HOST={db_host}
DB_NAME={db_name}
DB_USER={db_user}
DB_PASSWORD={db_password}
DB_PORT={db_port}

# Optional: Reddit API (not needed for scraping)
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=RedditLeadFinder/1.0
"""
    
    with open(env_file, "w") as f:
        f.write(env_content)
    
    print("✅ .env file created")
    return True

def test_database_connection():
    """Test database connection"""
    try:
        from database import Database
        db = Database()
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\n💡 Make sure PostgreSQL is running and credentials are correct")
        print("   macOS: brew install postgresql && brew services start postgresql")
        print("   Create database: createdb reddit_leads")
        return False

def initialize_database():
    """Initialize database tables and data"""
    try:
        from setup_database import main as setup_main
        setup_main()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def test_scraper():
    """Test the Reddit scraper"""
    try:
        from reddit_scraper_final import RedditLeadScraper
        scraper = RedditLeadScraper()
        leads = scraper.search_leads(
            keywords=["help", "tool"],
            subreddits=["entrepreneur"],
            days_back=1
        )
        if leads:
            print(f"✅ Scraper test successful - found {len(leads)} leads")
            return True
        else:
            print("⚠️  Scraper test returned no leads (this might be normal)")
            return True
    except Exception as e:
        print(f"❌ Scraper test failed: {e}")
        return False

def test_ai_analyzer():
    """Test AI analyzer"""
    try:
        from ai_analyzer import AILeadAnalyzer
        analyzer = AILeadAnalyzer()
        
        # Test with dummy data
        test_lead = {
            'title': 'Looking for a good CRM for my startup',
            'content': 'We are a small startup and need help managing our customer relationships',
            'subreddit': 'entrepreneur',
            'keywords_matched': ['CRM', 'startup']
        }
        
        result = analyzer.analyze_lead(test_lead)
        if result.get('probability', 0) > 0:
            print(f"✅ AI analyzer test successful - {result['probability']}% probability")
            return True
        else:
            print("❌ AI analyzer returned 0% probability")
            return False
    except Exception as e:
        print(f"❌ AI analyzer test failed: {e}")
        print("💡 Check your Anthropic API key in .env file")
        return False

def main():
    """Main installation function"""
    print_header("Reddit Lead Finder MVP - Installation")
    
    print("This script will set up the complete Reddit Lead Finder system.")
    print("You'll need:")
    print("  • Python 3.7+")
    print("  • PostgreSQL database")
    print("  • Anthropic API key (for AI analysis)")
    
    if input("\nContinue with installation? (y/N): ").lower() != 'y':
        print("Installation cancelled.")
        sys.exit(0)
    
    # Step 1: Check Python version
    print_step(1, "Checking Python Version")
    check_python_version()
    
    # Step 2: Install requirements
    print_step(2, "Installing Python Packages")
    if not install_requirements():
        print("❌ Installation failed at package installation")
        sys.exit(1)
    
    # Step 3: Check PostgreSQL
    print_step(3, "Checking PostgreSQL")
    if not check_postgresql():
        print("❌ Installation failed at PostgreSQL check")
        sys.exit(1)
    
    # Step 4: Setup environment
    print_step(4, "Setting up Environment")
    if not setup_env_file():
        print("❌ Installation failed at environment setup")
        sys.exit(1)
    
    # Step 5: Test database connection
    print_step(5, "Testing Database Connection")
    if not test_database_connection():
        print("❌ Installation failed at database connection")
        print("Please fix database issues and run: python3 setup_database.py")
        sys.exit(1)
    
    # Step 6: Initialize database
    print_step(6, "Initializing Database")
    if not initialize_database():
        print("❌ Installation failed at database initialization")
        sys.exit(1)
    
    # Step 7: Test scraper
    print_step(7, "Testing Reddit Scraper")
    if not test_scraper():
        print("⚠️  Scraper test had issues, but continuing...")
    
    # Step 8: Test AI analyzer
    print_step(8, "Testing AI Analyzer")
    if not test_ai_analyzer():
        print("⚠️  AI analyzer test failed, but continuing...")
        print("💡 You can add your Anthropic API key later in .env file")
    
    # Success!
    print_header("Installation Complete! 🎉")
    
    print("✅ Reddit Lead Finder MVP is ready to use!")
    print("\n🚀 Next steps:")
    print("   1. python3 scheduler.py once    # Test the full pipeline")
    print("   2. python3 view_leads.py        # View any leads found")
    print("   3. python3 scheduler.py         # Start hourly monitoring")
    
    print("\n📊 Management commands:")
    print("   python3 view_leads.py high      # View high-quality leads")
    print("   python3 view_leads.py stats     # View database statistics")
    
    print("\n💡 Tips:")
    print("   • Edit keywords/subreddits in setup_database.py")
    print("   • Check .env file for API keys and database settings")
    print("   • Monitor logs when running the scheduler")
    
    print(f"\n📁 All files are in: {os.getcwd()}")

if __name__ == "__main__":
    main()