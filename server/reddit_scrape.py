import requests
import json
from datetime import datetime
from urllib.parse import urljoin

# --- CONFIG ---
KEYWORDS = [
    "SaaS", "marketing", "SEO tool", "email automation", "growth hacking",
    "customer acquisition", "lead gen", "B2B software", "subscription service",
    "inbound marketing",
]
SUBREDDIT = "all"
LIMIT = 100

HEADERS = {
    "User-Agent": "KeywordLeadBot/1.0 by your_username"
}

# --- FUNCTIONS ---
def fetch_latest_comments():
    url = f"https://www.reddit.com/r/{SUBREDDIT}/comments/.json?limit={LIMIT}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def fetch_latest_posts():
    url = f"https://www.reddit.com/r/{SUBREDDIT}/new/.json?limit={LIMIT}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def matches_keywords(text, keywords):
    lowered = text.lower()
    return any(keyword.lower() in lowered for keyword in keywords)

def extract_leads(json_data, keywords, is_comment=True):
    leads = []
    for child in json_data.get("data", {}).get("children", []):
        data = child["data"]
        text = data.get("body") if is_comment else data.get("title", "") + "\n" + data.get("selftext", "")
        if matches_keywords(text, keywords):
            leads.append({
                "author": data.get("author"),
                "subreddit": data.get("subreddit"),
                "text": text,
                "permalink": urljoin("https://reddit.com", data.get("permalink", "")),
                "created_utc": datetime.utcfromtimestamp(data.get("created_utc")).isoformat(),
                "type": "comment" if is_comment else "post"
            })
    return leads

# --- MAIN ---
if __name__ == "__main__":
    comment_data = fetch_latest_comments()
    post_data = fetch_latest_posts()
    comment_leads = extract_leads(comment_data, KEYWORDS, is_comment=True)
    post_leads = extract_leads(post_data, KEYWORDS, is_comment=False)
    leads = comment_leads + post_leads
    with open("reddit_leads.json", "w") as f:
        json.dump(leads, f, indent=2)
    print(f"Found {len(leads)} leads (comments: {len(comment_leads)}, posts: {len(post_leads)}). Saved to reddit_leads.json")