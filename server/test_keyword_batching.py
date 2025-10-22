#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to demonstrate keyword batching for Reddit scraping.
Shows how 100+ keywords are split into optimal batches.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from f5bot_reddit_scraper import F5BotRedditScraper

def test_keyword_batching():
    """Test the keyword batching functionality."""
    
    # Create a list of 100 test keywords
    test_keywords = [
        # Business/SaaS keywords
        "CRM software", "project management", "team collaboration", "workflow automation",
        "customer support", "help desk", "ticketing system", "live chat",
        "email marketing", "marketing automation", "lead generation", "sales funnel",
        "analytics dashboard", "business intelligence", "data visualization", "reporting tool",
        "inventory management", "supply chain", "logistics software", "warehouse management",
        
        # Tech/Development keywords
        "API integration", "webhook", "REST API", "GraphQL", "microservices",
        "cloud hosting", "AWS", "Azure", "Google Cloud", "serverless",
        "database migration", "SQL optimization", "NoSQL", "MongoDB", "PostgreSQL",
        "CI/CD pipeline", "DevOps", "Docker", "Kubernetes", "container orchestration",
        "monitoring tool", "logging", "error tracking", "performance monitoring", "uptime",
        
        # E-commerce keywords
        "online store", "e-commerce platform", "shopping cart", "payment gateway",
        "inventory tracking", "order management", "shipping integration", "tax calculation",
        "product catalog", "customer reviews", "recommendation engine", "personalization",
        "abandoned cart", "conversion optimization", "A/B testing", "checkout optimization",
        "multi-channel selling", "marketplace integration", "dropshipping", "fulfillment",
        
        # Marketing keywords
        "social media management", "content scheduling", "influencer marketing", "brand monitoring",
        "SEO tool", "keyword research", "backlink analysis", "rank tracking",
        "PPC management", "Google Ads", "Facebook Ads", "ad optimization",
        "email automation", "drip campaigns", "newsletter", "subscriber management",
        "landing page", "conversion tracking", "attribution modeling", "customer journey",
        
        # HR/People keywords
        "HR software", "payroll management", "employee onboarding", "performance review",
        "time tracking", "attendance management", "leave management", "shift scheduling",
        "recruitment tool", "applicant tracking", "candidate screening", "interview scheduling",
        "employee engagement", "feedback tool", "survey platform", "culture assessment",
        "learning management", "training platform", "skill assessment", "certification tracking",
        
        # Finance/Accounting keywords
        "accounting software", "bookkeeping", "invoice management", "expense tracking",
        "financial reporting", "budget planning", "cash flow", "profit analysis",
        "tax preparation", "compliance management", "audit trail", "financial dashboard",
        "payment processing", "billing automation", "subscription management", "recurring payments"
    ]
    
    print("KEYWORD BATCHING TEST")
    print("=" * 50)
    print("Total keywords to test: {}".format(len(test_keywords)))
    print("Sample keywords: {}...".format(', '.join(test_keywords[:5])))
    print()
    
    # Initialize scraper
    scraper = F5BotRedditScraper()
    
    # Test the batching function
    batches = scraper._split_keywords_into_batches(test_keywords)
    
    print("BATCHING RESULTS:")
    print("   Total batches created: {}".format(len(batches)))
    print("   Max keywords per batch: {}".format(scraper.max_keywords_per_batch))
    print("   Max query length: {}".format(scraper.max_query_length))
    print()
    
    # Show details of each batch
    total_keywords_in_batches = 0
    for i, batch in enumerate(batches, 1):
        # Estimate query length
        query = "(" + " OR ".join(['"{}"'.format(kw) for kw in batch]) + ")"
        query_length = len(query)
        
        print("Batch {}:".format(i))
        print("   Keywords: {}".format(len(batch)))
        print("   Query length: {} chars".format(query_length))
        print("   Sample: {}{}".format(', '.join(batch[:3]), '...' if len(batch) > 3 else ''))
        print()
        
        total_keywords_in_batches += len(batch)
    
    # Verify all keywords are included
    print("VERIFICATION:")
    print("   Original keywords: {}".format(len(test_keywords)))
    print("   Keywords in batches: {}".format(total_keywords_in_batches))
    print("   All keywords preserved: {}".format('Yes' if total_keywords_in_batches == len(test_keywords) else 'No'))
    print()
    
    # Show estimated performance
    estimated_requests = len(batches) * 2  # 2 methods per batch
    estimated_time = estimated_requests * 5  # ~5 seconds per request with delays
    
    print("ESTIMATED PERFORMANCE:")
    print("   API requests needed: {}".format(estimated_requests))
    print("   Estimated time: ~{}m {}s".format(estimated_time // 60, estimated_time % 60))
    print("   Rate limit friendly: Yes (built-in delays)")
    print()
    
    print("RECOMMENDATIONS:")
    print("   • For 100 keywords: Use 8-10 batches of 10-12 keywords each")
    print("   • For 200+ keywords: Consider running in multiple sessions")
    print("   • Monitor rate limits and adjust delays if needed")
    print("   • Use time filters (week/month) to focus on recent content")

if __name__ == "__main__":
    test_keyword_batching()