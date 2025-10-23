#!/usr/bin/env python3
"""
Background service that runs every hour to:
1. Scrape Reddit for new leads using database keywords (PostgreSQL)
2. Process leads for all businesses
3. Log results

This should be run as a daemon/service to continuously fetch leads.
Updated: Fixed PostgreSQL compatibility and keyword deduplication.
"""

import sys
import os
import time
import schedule
from datetime import datetime
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the server directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import Database
from f5bot_reddit_scraper import search_reddit_leads_efficient
from deepseek_analyzer import DeepSeekAnalyzer

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('background_service.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class LeadScrapingService:
    """Background service for continuous lead scraping and processing."""
    
    def __init__(self):
        self.db = Database()
        self.ai = DeepSeekAnalyzer()
        self.last_run = None
        self.version = "2.0-postgresql"  # Version identifier for debugging
        
    def scrape_and_process_leads(self):
        """Main function that scrapes Reddit using F5Bot and processes leads for all businesses."""
        logger.info("🚀 Starting F5Bot lead scraping and processing...")
        logger.info(f"📋 Service version: {self.version}")
        logger.info("=" * 70)
        
        try:
            # Step 1: Scrape Reddit for new leads
            scraped_count = self._scrape_reddit_leads()
            
            # Step 2: Process leads for all businesses
            processed_results = self._process_all_businesses()
            
            # Step 3: Log summary
            self._log_summary(scraped_count, processed_results)
            
            self.last_run = datetime.now()
            logger.info("✅ F5Bot processing completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ F5Bot processing failed: {str(e)}")
            
        logger.info("=" * 70)
    
    def _scrape_reddit_leads(self):
        """Scrape Reddit using F5Bot with all database keywords and store in global_leads."""
        logger.info("📡 Step 1: F5Bot Reddit scraping for new leads...")
        
        try:
            # Get all unique keywords from all businesses in database
            keywords = self._get_all_unique_keywords()
            
            if not keywords:
                logger.warning("⚠️  No keywords found in database - skipping Reddit scraping")
                logger.info("💡 Add keywords to your businesses to enable lead discovery")
                logger.info("🚫 F5Bot NOT started - no keywords to search for")
                return 0
            
            logger.info(f"🔍 F5Bot scraping with {len(keywords)} unique keywords from all businesses")
            
            # Additional safety check for keyword quality
            valid_keywords = [kw for kw in keywords if kw and len(kw.strip()) >= 2]
            if len(valid_keywords) != len(keywords):
                logger.info(f"🧹 Filtered out {len(keywords) - len(valid_keywords)} invalid keywords")
                keywords = valid_keywords
                
            if not keywords:
                logger.warning("⚠️  No valid keywords after filtering - skipping Reddit scraping")
                logger.info("🚫 F5Bot NOT started - no valid keywords remaining")
                return 0
            
            # Get scraping interval to determine time range
            interval_minutes = int(os.getenv('SCRAPING_INTERVAL_MINUTES', '120'))
            days_back = max(1, interval_minutes / (60 * 24))  # Convert minutes to days
            
            # Scrape Reddit using F5Bot
            logger.info("🤖 Starting F5Bot Reddit scraper...")
            leads = search_reddit_leads_efficient(
                keywords=keywords,

                days_back=days_back,
                limit=100  # Reasonable limit for F5Bot scraping
            )
            
            logger.info(f"📊 F5Bot found {len(leads)} potential leads from Reddit")
            
            if not leads:
                logger.info("ℹ️  No new leads found")
                return 0
            
            # Store leads in database
            stored_count = 0
            duplicate_count = 0
            
            for lead in leads:
                try:
                    # Extract Reddit post ID from URL for platform_id
                    platform_id = lead.get('id', '').replace('f5bot_', '') or f"unknown_{hash(lead.get('title', ''))}"
                    
                    lead_id = self.db.add_global_lead(
                        platform='reddit',
                        platform_id=platform_id,
                        title=lead.get('title', ''),
                        content=lead.get('content', ''),
                        author=lead.get('author', ''),
                        url=lead.get('url', ''),

                        score=lead.get('upvotes', 0)
                    )
                    
                    if lead_id:
                        stored_count += 1
                        matched_kw = ', '.join(lead.get('matched_keywords', [])[:2])
                        logger.info(f"  ✅ Stored: {lead['title'][:40]}... | Keywords: {matched_kw}")
                    else:
                        duplicate_count += 1
                        
                except Exception as e:
                    logger.error(f"  ❌ Error storing lead: {str(e)}")
                    continue
            
            logger.info(f"📊 F5Bot results: {stored_count} stored, {duplicate_count} duplicates")
            return stored_count
            
        except Exception as e:
            logger.error(f"❌ F5Bot scraping failed: {str(e)}")
            return 0
    
    def _get_all_unique_keywords(self):
        """Get all unique keywords from all businesses in the database with enhanced filtering."""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Get all keywords from all businesses with better filtering
            cursor.execute('''
                SELECT DISTINCT TRIM(LOWER(keyword)) as clean_keyword, keyword as original_keyword
                FROM keywords 
                WHERE keyword IS NOT NULL 
                AND TRIM(keyword) != '' 
                AND LENGTH(TRIM(keyword)) >= 2
                ORDER BY clean_keyword
            ''')
            
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            
            if not results:
                logger.warning("⚠️  No valid keywords found in database")
                return []
            
            # Use a set to ensure uniqueness (case-insensitive)
            unique_keywords = {}
            for clean_keyword, original_keyword in results:
                if clean_keyword not in unique_keywords:
                    unique_keywords[clean_keyword] = original_keyword
            
            final_keywords = list(unique_keywords.values())
            
            logger.info(f"📋 Loaded {len(final_keywords)} unique keywords from database")
            logger.info(f"🔍 Sample keywords: {', '.join(final_keywords[:5])}{'...' if len(final_keywords) > 5 else ''}")
            
            return final_keywords
            
        except Exception as e:
            logger.error(f"❌ Error loading keywords: {str(e)}")
            return []
    
    def _process_all_businesses(self):
        """Process leads for all businesses using AI analysis."""
        logger.info("🤖 Step 2: Processing leads for all businesses...")
        
        try:
            # Get all businesses
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT id, name, description FROM businesses')
            businesses = cursor.fetchall()
            cursor.close()
            conn.close()
            
            if not businesses:
                logger.warning("⚠️  No businesses found")
                return {'total_processed': 0, 'total_matched': 0, 'businesses_processed': 0}
            
            logger.info(f"🏢 Processing {len(businesses)} businesses")
            
            total_processed = 0
            total_matched = 0
            
            for business_id, business_name, business_description in businesses:
                logger.info(f"  📋 Processing: {business_name} (ID: {business_id})")
                
                # Log business description for context
                if business_description:
                    logger.info(f"    📄 Description: {business_description[:60]}{'...' if len(business_description) > 60 else ''}")
                
                # Get business keywords
                keywords = self.db.get_business_keywords(business_id)
                if not keywords:
                    logger.info(f"    ⚠️  No keywords for {business_name}")
                    continue
                
                keyword_list = [kw['keyword'].lower() for kw in keywords]
                logger.info(f"    🔍 Keywords: {', '.join(keyword_list[:3])}{'...' if len(keyword_list) > 3 else ''}")
                
                # Get unprocessed leads for this business
                unprocessed_leads = self.db.get_unprocessed_leads_for_business(business_id)
                logger.info(f"    📊 {len(unprocessed_leads)} unprocessed leads")
                
                # Filter leads that match business keywords first
                matching_leads = []
                for lead in unprocessed_leads:
                    lead_text = f"{lead['title']} {lead['content']}".lower()
                    matched_keywords = []
                    
                    for keyword in keyword_list:
                        if keyword.lower() in lead_text:
                            matched_keywords.append(keyword)
                    
                    if matched_keywords:
                        lead['matched_keywords'] = matched_keywords
                        matching_leads.append(lead)
                
                logger.info(f"    🎯 {len(matching_leads)} leads match business keywords")
                
                processed_count = len(unprocessed_leads)
                matched_count = 0
                
                # Process leads in batches of 5 for AI analysis (smaller batches to avoid timeouts)
                batch_size = 5
                for i in range(0, len(matching_leads), batch_size):
                    batch = matching_leads[i:i + batch_size]
                    
                    try:
                        batch_num = i//batch_size + 1
                        logger.info(f"    🤖 Analyzing batch {batch_num} ({len(batch)} leads)")
                        
                        # Batch analyze with AI (with retry on timeout)
                        analyzed_leads = None
                        for retry in range(2):  # Try twice
                            try:
                                analyzed_leads = self.ai.batch_analyze_leads_for_business(
                                    leads=batch,
                                    business_keywords=keyword_list,
                                    business_name=business_name,
                                    business_description=business_description or "No description available"
                                )
                                break  # Success, exit retry loop
                            except Exception as e:
                                if "timeout" in str(e).lower() and retry == 0:
                                    logger.warning(f"    ⚠️  Batch {batch_num} timed out, retrying...")
                                    time.sleep(2)
                                    continue
                                else:
                                    raise e
                        
                        if not analyzed_leads:
                            logger.error(f"    ❌ Batch {batch_num} failed after retries")
                            continue
                        
                        # Save leads that meet the threshold
                        for analyzed_lead in analyzed_leads:
                            ai_score = analyzed_lead.get('probability', 0)
                            ai_reasoning = analyzed_lead.get('analysis', 'No analysis available')
                            matched_keywords = analyzed_lead.get('matched_keywords', [])
                            
                            # Only save if AI score is above threshold (60%)
                            if ai_score >= 60:
                                success = self.db.add_business_lead(
                                    business_id=business_id,
                                    global_lead_id=analyzed_lead['id'],
                                    ai_score=ai_score,
                                    ai_reasoning=ai_reasoning,
                                    matched_keywords=matched_keywords
                                )
                                
                                if success:
                                    matched_count += 1
                                    logger.info(f"    ✅ Matched: {analyzed_lead['title'][:40]}... (Score: {ai_score}%)")
                        
                        # Small delay between batches
                        time.sleep(1)
                        
                    except Exception as e:
                        logger.error(f"    ❌ Error processing batch: {str(e)}")
                        continue
                
                logger.info(f"    📊 Results: {processed_count} processed, {matched_count} matched")
                total_processed += processed_count
                total_matched += matched_count
            
            return {
                'total_processed': total_processed,
                'total_matched': total_matched,
                'businesses_processed': len(businesses)
            }
            
        except Exception as e:
            logger.error(f"❌ Business processing failed: {str(e)}")
            return {'error': str(e), 'total_processed': 0, 'total_matched': 0}
    
    def _log_summary(self, scraped_count, processed_results):
        """Log a summary of the processing results."""
        interval_minutes = int(os.getenv('SCRAPING_INTERVAL_MINUTES', '120'))
        logger.info("📊 F5BOT SCRAPING SUMMARY:")
        logger.info(f"   New leads scraped: {scraped_count}")
        logger.info(f"   Leads processed: {processed_results.get('total_processed', 0)}")
        logger.info(f"   Leads matched: {processed_results.get('total_matched', 0)}")
        logger.info(f"   Businesses processed: {processed_results.get('businesses_processed', 0)}")
        logger.info(f"   Next run in: {interval_minutes} minutes")
        
        if 'error' in processed_results:
            logger.error(f"   Processing error: {processed_results['error']}")
    
    def get_status(self):
        """Get current service status."""
        interval_minutes = int(os.getenv('SCRAPING_INTERVAL_MINUTES', '60'))
        return {
            'service': 'Lead Scraping Service',
            'status': 'running',
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'next_run': f'Every {interval_minutes} minutes',
            'interval_minutes': interval_minutes
        }

def run_service():
    """Run the F5Bot background service with configurable scheduling."""
    # Get scraping interval from environment variable (default to 120 minutes)
    interval_minutes = int(os.getenv('SCRAPING_INTERVAL_MINUTES', '120'))
    
    logger.info("🚀 Starting F5Bot Lead Scraping Background Service")
    logger.info(f"⏰ Scheduled to run every {interval_minutes} minutes")
    logger.info("🤖 Using F5Bot techniques for reliable Reddit scraping")
    logger.info("📋 Press Ctrl+C to stop the service")
    logger.info("=" * 70)
    
    service = LeadScrapingService()
    
    # Schedule the job to run at the configured interval
    schedule.every(interval_minutes).minutes.do(service.scrape_and_process_leads)
    
    # Run once immediately on startup
    logger.info("🔄 Running initial scraping...")
    service.scrape_and_process_leads()
    
    # Keep the service running
    try:
        while True:
            schedule.run_pending()
            time.sleep(30)  # Check every 30 seconds
    except KeyboardInterrupt:
        logger.info("⏹️  Service stopped by user")
    except Exception as e:
        logger.error(f"❌ Service crashed: {str(e)}")

def run_once():
    """Run the F5Bot scraping and processing once (for testing)."""
    logger.info("🧪 Running F5Bot lead scraping once for testing...")
    service = LeadScrapingService()
    service.scrape_and_process_leads()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "once":
        run_once()
    else:
        run_service()