# Reddit Lead Finder MVP

A complete system that automatically finds potential customers on Reddit, analyzes them with AI, and stores high-quality leads in a PostgreSQL database. Runs every hour to continuously discover new opportunities.

## 🚀 What It Does

1. **Scrapes Reddit** - Uses efficient search queries to find posts across multiple subreddits
2. **AI Analysis** - Claude analyzes each post and assigns a probability score (0-100%)
3. **Database Storage** - Stores leads with full metadata and AI analysis
4. **Hourly Schedule** - Automatically runs every hour to find new opportunities
5. **Lead Management** - View and filter leads by quality score

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Reddit API    │───▶│  AI Analyzer     │───▶│   PostgreSQL    │
│  (Scraping)     │    │  (Claude 3)      │    │   Database      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         ▲                        ▲                       ▲
         │                        │                       │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Scheduler     │    │   Keywords &     │    │   Lead Viewer   │
│  (Every Hour)   │    │   Subreddits     │    │     (CLI)       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📦 Installation

### 1. Install Dependencies
```bash
cd server
pip3 install -r requirements.txt
```

### 2. Setup PostgreSQL
```bash
# Install PostgreSQL (macOS)
brew install postgresql
brew services start postgresql

# Create database
createdb reddit_leads
```

### 3. Configure Environment
Edit `server/.env`:
```env
ANTHROPIC_API_KEY=your_claude_api_key

# Database
DB_HOST=localhost
DB_NAME=reddit_leads
DB_USER=postgres
DB_PASSWORD=your_password
DB_PORT=5432
```

### 4. Initialize Database
```bash
python3 setup_database.py
```

## 🎯 Quick Start

### Test the Scraper
```bash
python3 test_scraper.py
```

### Run Once (Test Full Pipeline)
```bash
python3 scheduler.py once
```

### Start Continuous Monitoring
```bash
python3 scheduler.py
```

### View Your Leads
```bash
python3 view_leads.py
```

## 📊 Database Schema

### Keywords Table
Tracks which keywords to search for:
```sql
keywords (
  id, keyword, active, created_at
)
```



### Leads Table
Stores found leads with AI analysis:
```sql
leads (
  id, reddit_id, service, title, content, url, author,
  type, keywords_matched, ai_probability, ai_analysis,
  hotness_score, upvotes, num_comments, created_date, processed_at, raw_data
)
```

## 🔍 How It Works

### 1. Efficient Scraping
Instead of making individual requests to each subreddit (which causes rate limiting), the system:
- Uses Reddit's search API with subreddit filters: `"keyword" (subreddit:entrepreneur+subreddit:startups)`
- Makes one request per keyword across ALL monitored subreddits
- Dramatically reduces API calls and avoids rate limits

### 2. AI Analysis
Each found post is analyzed by Claude 3 Haiku:
- Evaluates if the person has a genuine business need
- Checks if they're likely a decision maker with budget
- Assigns probability score (0-100%)
- Provides reasoning for the score

### 3. Quality Scoring
- **70%+ (🔥)** - High quality leads, ready to contact
- **40-69% (🔶)** - Medium quality, worth investigating  
- **0-39% (⚪)** - Low quality, probably not worth pursuing

## 📋 Commands

### Database Setup
```bash
python3 setup_database.py          # Initialize database and add default keywords/subreddits
```

### Running the System
```bash
python3 scheduler.py               # Start hourly monitoring
python3 scheduler.py once          # Run once for testing
python3 test_scraper.py           # Test scraper only
```

### Viewing Leads
```bash
python3 view_leads.py             # Show good leads (50%+)
python3 view_leads.py high        # Show high quality leads (70%+)
python3 view_leads.py all         # Show all leads
python3 view_leads.py stats       # Show database statistics
python3 view_leads.py --min-prob 80  # Show leads with 80%+ probability
```

## ⚙️ Configuration

### Adding Keywords
Edit `setup_database.py` or add directly to database:
```python
db.add_keyword("email automation")
db.add_keyword("struggling with CRM")
```

### Adding Subreddits
```python
db.add_subreddit("entrepreneur")
db.add_subreddit("startups")
```

### Customizing AI Analysis
Edit `ai_analyzer.py` to customize the business context:
```python
self.business_context = """
I'm looking for potential customers for my SEO tool.
I want to find people who:
- Are struggling with SEO
- Need help with keyword research
- Want to improve their rankings
"""
```

## 📈 Example Output

```
🚀 Starting lead finding cycle at 2025-01-10 14:30:00
================================================================
📋 Keywords (15): SaaS, marketing tool, CRM, automation, lead generation...
📋 Subreddits (12): r/entrepreneur, r/startups, r/marketing, r/SaaS, r/webdev...

📡 Step 1: Scraping Reddit...
🔍 Searching 12 subreddits with single query approach...
  🔎 Searching for: 'SaaS'
    📊 Retrieved 23 recent posts
    ✅ Found 8 post leads
  🔎 Searching for: 'marketing tool'
    📊 Retrieved 15 recent posts
    ✅ Found 5 post leads
✅ Found 13 raw leads

🤖 Step 2: AI Analysis...
  Analyzing lead 1/13: Looking for a good CRM for my startup...
  Analyzing lead 2/13: Need help with email automation...
✅ AI analysis complete. Top lead: 87%

💾 Step 3: Saving to database...
✅ Saved 13/13 leads to database

📊 Cycle Summary:
   🔥 High quality leads (70%+): 4
   🔶 Medium quality leads (40-69%): 6
   📈 Total leads processed: 13

🏆 Top 3 leads this cycle:
   1. [87%] Looking for a good CRM for my startup that's not too expensive...
      r/entrepreneur | 15 upvotes
   2. [82%] Our email marketing is manual and taking forever, any automation tools?
      r/marketing | 8 upvotes
   3. [75%] Small business owner here, need help tracking leads better...
      r/smallbusiness | 12 upvotes
```

## 🔧 Troubleshooting

### No Leads Found
- Check if keywords are too specific
- Verify subreddit names are correct
- Try increasing `days_back` parameter
- Run `python3 test_scraper.py` to test scraping

### Database Connection Issues
- Ensure PostgreSQL is running: `brew services start postgresql`
- Check `.env` database credentials
- Create database: `createdb reddit_leads`

### Rate Limiting
- The new system should avoid this, but if it happens:
- Wait 10-15 minutes before retrying
- Reduce number of keywords temporarily

### AI Analysis Errors
- Check your Anthropic API key in `.env`
- Ensure you have API credits
- Check network connection

## 🎯 Customization for Your Business

### For SEO Tools
```python
# In setup_database.py, add SEO-specific keywords:
seo_keywords = [
    "SEO help", "keyword research", "ranking issues", "Google traffic",
    "website not ranking", "need SEO tool", "organic traffic down"
]

seo_subreddits = [
    "SEO", "webdev", "entrepreneur", "smallbusiness", "marketing"
]
```

### For E-commerce Tools
```python
ecommerce_keywords = [
    "Shopify help", "inventory management", "order tracking", 
    "customer service tool", "abandoned cart", "conversion rate"
]

ecommerce_subreddits = [
    "shopify", "ecommerce", "entrepreneur", "dropshipping", "amazon"
]
```

## 📊 Performance

- **Scraping**: ~30 seconds per cycle
- **AI Analysis**: ~2-3 seconds per lead
- **Database**: Handles thousands of leads efficiently
- **Memory**: ~50MB typical usage
- **API Costs**: ~$0.10-0.50 per hour (depending on lead volume)

## 🚀 Next Steps

1. **Run the system** for a few hours to collect leads
2. **Review high-quality leads** (70%+) for outreach opportunities
3. **Customize keywords** based on your specific product/service
4. **Add more subreddits** relevant to your target audience
5. **Build integrations** (Slack notifications, CRM sync, etc.)

This MVP gives you everything you need to start finding qualified leads on Reddit automatically!