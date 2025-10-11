#!/usr/bin/env python3
"""
View and manage leads from the database.
Simple CLI tool to see your Reddit leads and their AI analysis.
"""

import sys
from datetime import datetime
from database import Database

def view_leads(min_probability=0, limit=20):
    """View leads from database"""
    db = Database()
    
    print(f"🔍 Fetching leads (min probability: {min_probability}%, limit: {limit})")
    print("=" * 80)
    
    leads = db.get_leads(limit=limit, min_probability=min_probability)
    
    if not leads:
        print("📭 No leads found matching your criteria.")
        print("\nTry:")
        print("  python view_leads.py --min-prob 0    # Show all leads")
        print("  python scheduler.py once             # Run scraper once")
        return
    
    print(f"📊 Found {len(leads)} leads\n")
    
    for i, lead in enumerate(leads, 1):
        # Format dates
        created_date = lead.get('created_date')
        if isinstance(created_date, str):
            created_date = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
        
        processed_date = lead.get('processed_at')
        if isinstance(processed_date, str):
            processed_date = datetime.fromisoformat(processed_date.replace('Z', '+00:00'))
        
        # Calculate age
        if created_date:
            age_hours = (datetime.now() - created_date.replace(tzinfo=None)).total_seconds() / 3600
            if age_hours < 24:
                age_str = f"{int(age_hours)}h ago"
            else:
                age_str = f"{int(age_hours/24)}d ago"
        else:
            age_str = "unknown"
        
        # Display lead
        probability = lead.get('ai_probability', 0)
        prob_emoji = "🔥" if probability >= 80 else "🔶" if probability >= 60 else "🔵" if probability >= 40 else "⚪"
        
        print(f"{i:2d}. {prob_emoji} [{probability:2d}%] {lead.get('title', '')[:60]}...")
        print(f"    📍 r/{lead.get('subreddit', '')} | 👤 u/{lead.get('author', '')} | ⏰ {age_str}")
        print(f"    👍 {lead.get('upvotes', 0)} upvotes | 💬 {lead.get('num_comments', 0)} comments")
        print(f"    🔗 {lead.get('url', '')}")
        
        # Show AI analysis if available
        ai_analysis = lead.get('ai_analysis', '')
        if ai_analysis and ai_analysis != 'None':
            # Clean up analysis text
            analysis_clean = ai_analysis.replace('Probability:', '').replace(f'{probability}%', '').strip()
            if analysis_clean.startswith('- '):
                analysis_clean = analysis_clean[2:]
            print(f"    🤖 {analysis_clean[:100]}...")
        
        # Show matched keywords
        keywords = lead.get('keywords_matched', [])
        if keywords:
            print(f"    🏷️  Keywords: {', '.join(keywords[:3])}{'...' if len(keywords) > 3 else ''}")
        
        print()

def show_stats():
    """Show database statistics"""
    db = Database()
    
    print("📊 Database Statistics")
    print("=" * 30)
    
    # Get leads by probability ranges
    all_leads = db.get_leads(limit=1000, min_probability=0)
    
    if not all_leads:
        print("📭 No leads in database yet.")
        return
    
    high_quality = len([l for l in all_leads if l.get('ai_probability', 0) >= 70])
    medium_quality = len([l for l in all_leads if 40 <= l.get('ai_probability', 0) < 70])
    low_quality = len([l for l in all_leads if l.get('ai_probability', 0) < 40])
    
    print(f"Total leads: {len(all_leads)}")
    print(f"🔥 High quality (70%+): {high_quality}")
    print(f"🔶 Medium quality (40-69%): {medium_quality}")
    print(f"⚪ Low quality (<40%): {low_quality}")
    
    # Subreddit breakdown
    subreddit_counts = {}
    for lead in all_leads:
        sub = lead.get('subreddit', 'unknown')
        subreddit_counts[sub] = subreddit_counts.get(sub, 0) + 1
    
    print(f"\n📍 Top subreddits:")
    for sub, count in sorted(subreddit_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"   r/{sub}: {count} leads")
    
    # Recent activity
    recent_leads = [l for l in all_leads if l.get('processed_at')]
    if recent_leads:
        latest = max(recent_leads, key=lambda x: x.get('processed_at', ''))
        latest_time = latest.get('processed_at')
        if isinstance(latest_time, str):
            latest_time = datetime.fromisoformat(latest_time.replace('Z', '+00:00'))
        print(f"\n⏰ Last update: {latest_time.strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Main CLI function"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "stats":
            show_stats()
            return
        elif command == "high":
            view_leads(min_probability=70, limit=10)
            return
        elif command == "all":
            view_leads(min_probability=0, limit=50)
            return
        elif command.startswith("--min-prob"):
            try:
                min_prob = int(sys.argv[2]) if len(sys.argv) > 2 else 50
                view_leads(min_probability=min_prob, limit=30)
                return
            except (ValueError, IndexError):
                pass
    
    # Default: show medium to high quality leads
    view_leads(min_probability=50, limit=20)
    
    print("\n💡 Commands:")
    print("  python view_leads.py              # Show good leads (50%+)")
    print("  python view_leads.py high         # Show high quality leads (70%+)")
    print("  python view_leads.py all          # Show all leads")
    print("  python view_leads.py stats        # Show database statistics")
    print("  python view_leads.py --min-prob X # Show leads with X% or higher")

if __name__ == "__main__":
    main()