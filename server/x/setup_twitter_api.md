# Setting Up Twitter API Access

## 🔑 Getting Twitter API Credentials

Since snscrape is being blocked, here's how to set up the official Twitter API for reliable access:

### Step 1: Apply for Twitter Developer Account

1. Go to [developer.twitter.com](https://developer.twitter.com)
2. Click "Apply for a developer account"
3. Fill out the application (usually approved within 24-48 hours)
4. Describe your use case: "Lead generation and market research for business development"

### Step 2: Create a Twitter App

1. Once approved, go to the Developer Portal
2. Create a new "App"
3. Fill in basic information:
   - **App name**: "Lead Finder" (or similar)
   - **Description**: "Tool for finding potential business leads on Twitter"
   - **Website**: Your website or GitHub repo

### Step 3: Generate Bearer Token

1. In your app dashboard, go to "Keys and tokens"
2. Generate a "Bearer Token"
3. Copy and save this token securely

### Step 4: Configure Environment

Add your Bearer Token to your environment:

```bash
# Option 1: Environment variable
export TWITTER_BEARER_TOKEN="your_bearer_token_here"

# Option 2: Add to .env file
echo "TWITTER_BEARER_TOKEN=your_bearer_token_here" >> server/.env
```

## 🚀 Testing the API

Once configured, test with:

```bash
cd server/x
python twitter_api_scraper.py
```

## 📊 API Limits & Pricing

### Free Tier (Essential Access)
- **Recent Search**: 500,000 tweets/month
- **Rate limit**: 300 requests/15 minutes
- **Lookback**: 7 days
- **Cost**: Free

### Paid Tiers
- **Basic ($100/month)**: 2M tweets/month, 30-day lookback
- **Pro ($5,000/month)**: 10M tweets/month, full archive access

For lead generation, the free tier is usually sufficient to start.

## 🔧 Alternative: Browser Automation

If you prefer not to use the API, I can create a browser automation version using Selenium:

```python
# Would use Selenium to automate a browser
# More complex but doesn't require API access
# Slower but can work around restrictions
```

## 📈 Expected Results

With proper API access, searching for "how to market" should return:
- 50-100 recent tweets per search
- Confidence scores based on engagement and content
- Direct links to tweets for outreach
- User information for lead qualification

Would you like me to help you set up the Twitter API, or would you prefer the browser automation approach?