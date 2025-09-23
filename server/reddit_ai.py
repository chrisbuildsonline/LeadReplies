import os
from datetime import datetime, timedelta
from anthropic import Anthropic
from dotenv import load_dotenv
import time

# Load API key from .env
load_dotenv()
client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

# Configurable search
keyword = "GPT-5"
days = 30
calculated_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

# Prompt Claude to use web_search
prompt = (
    f"Use the `web_search` tool to search for Reddit posts or comments from the last {days} days "
    f"that mention the keyword '{keyword}' and contain questions or requests for help.\n\n"
    f"Search using: site:reddit.com {keyword} question OR advice OR problem after:{calculated_date}\n\n"
    "From the search results, return up to 10 Reddit leads. For each, provide:\n"
    "- The visible post title or snippet (only what's available from the search engine)\n"
    "- A direct Reddit link to reply\n"
    "- Label it as either `post_reply` or `user_reply` based on context\n"
    "- A 'hotness' score from 1–100 for how relevant this is as a lead (estimate based on text)\n\n"
    "Only use what is visible from the web search results. Do not fabricate content. Do not fetch full pages."
)

# Send the initial message
initial_response = client.messages.create(
    model="claude-3-7-sonnet-latest",
    max_tokens=1500,
    messages=[{"role": "user", "content": prompt}],
    tools=[{
        "type": "web_search_20250305",
        "name": "web_search",
        "max_uses": 5
    }]
)

# Wait and fetch the final response using polling
message_id = initial_response.id
status = initial_response.stop_reason

while status != "end_turn":
    time.sleep(1)  # wait 1 second before polling again
    final_response = client.messages.get(message_id)
    status = final_response.stop_reason

# Print result
if final_response.content:
    print(final_response.content[0].text)
else:
    print("No results returned.")