import schedule
import time
import threading
from datetime import datetime
from database import Database
from reddit_scraper_final import RedditLeadScraper
from ai_analyzer import AILeadAnalyzer

class LeadFinderScheduler:
    """
    Scheduler that runs Reddit lead finding every hour.
    Manages the complete pipeline: scraping -> AI analysis -> database storage.
    """
    
    def __init__(self):
        self.db = Database()
        self.scraper = RedditLeadScraper()
        self.ai_analyzer = AILeadAnalyzer()
        self.running = False
        self.thread = None
    
    def run_lead_finding_cycle(self):
        """Run a complete lead finding cycle"""
        try:
            print(f"\n🚀 Starting lead finding cycle at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 60)
            
            # Get active keywords and subreddits from database
            keywords = self.db.get_active_keywords()
            subreddits = self.db.get_active_subreddits()
            
            if not keywords:
                print("⚠️  No active keywords found. Please add some keywords first.")
                return
            
            if not subreddits:
                print("⚠️  No active subreddits found. Please add some subreddits first.")
                return
            
            print(f"📋 Keywords ({len(keywords)}): {', '.join(keywords[:5])}{'...' if len(keywords) > 5 else ''}")
            print(f"📋 Subreddits ({len(subreddits)}): {', '.join([f'r/{s}' for s in subreddits[:5]])}{'...' if len(subreddits) > 5 else ''}")
            
            # Step 1: Scrape Reddit for leads
            print(f"\n📡 Step 1: Scraping Reddit...")
            raw_leads = self.scraper.search_leads(keywords, subreddits, days_back=1)  # Last 24 hours
            
            if not raw_leads:
                print("ℹ️  No new leads found in this cycle.")
                return
            
            print(f"✅ Found {len(raw_leads)} raw leads")
            
            # Step 2: AI Analysis
            print(f"\n🤖 Step 2: AI Analysis...")
            analyzed_leads = self.ai_analyzer.analyze_batch(raw_leads)
            
            # Step 3: Save to database
            print(f"\n💾 Step 3: Saving to database...")
            saved_count = 0
            for lead in analyzed_leads:
                if self.db.save_lead(lead):
                    saved_count += 1
            
            print(f"✅ Saved {saved_count}/{len(analyzed_leads)} leads to database")
            
            # Step 4: Show summary
            high_quality_leads = [l for l in analyzed_leads if l.get('ai_probability', 0) >= 70]
            medium_quality_leads = [l for l in analyzed_leads if 40 <= l.get('ai_probability', 0) < 70]
            
            print(f"\n📊 Cycle Summary:")
            print(f"   🔥 High quality leads (70%+): {len(high_quality_leads)}")
            print(f"   🔶 Medium quality leads (40-69%): {len(medium_quality_leads)}")
            print(f"   📈 Total leads processed: {len(analyzed_leads)}")
            
            # Show top 3 leads
            if high_quality_leads:
                print(f"\n🏆 Top 3 leads this cycle:")
                for i, lead in enumerate(high_quality_leads[:3], 1):
                    print(f"   {i}. [{lead.get('ai_probability', 0)}%] {lead.get('title', '')[:60]}...")
                    print(f"      r/{lead.get('subreddit', '')} | {lead.get('upvotes', 0)} upvotes")
            
            print(f"\n✅ Cycle completed at {datetime.now().strftime('%H:%M:%S')}")
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ Error in lead finding cycle: {str(e)}")
    
    def start_scheduler(self):
        """Start the scheduler in a separate thread"""
        if self.running:
            print("⚠️  Scheduler is already running")
            return
        
        print("🕐 Starting lead finder scheduler...")
        print("📅 Schedule: Every hour")
        print("🔄 First run: Now")
        print("⏹️  Press Ctrl+C to stop\n")
        
        # Schedule the job to run every hour
        schedule.every().hour.do(self.run_lead_finding_cycle)
        
        # Run once immediately
        self.run_lead_finding_cycle()
        
        self.running = True
        
        # Start scheduler loop in separate thread
        def scheduler_loop():
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        self.thread = threading.Thread(target=scheduler_loop, daemon=True)
        self.thread.start()
        
        try:
            # Keep main thread alive
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_scheduler()
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        print("\n⏹️  Stopping scheduler...")
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("✅ Scheduler stopped")
    
    def run_once(self):
        """Run the lead finding cycle once (for testing)"""
        print("🧪 Running single lead finding cycle...")
        self.run_lead_finding_cycle()

def main():
    """Main function to run the scheduler"""
    scheduler = LeadFinderScheduler()
    
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "once":
        # Run once for testing
        scheduler.run_once()
    else:
        # Start continuous scheduler
        scheduler.start_scheduler()

if __name__ == "__main__":
    main()