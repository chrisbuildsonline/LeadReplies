# Requirements Document

## Introduction

This feature creates a comprehensive Reddit lead generation backend that can identify potential customers or leads for SaaS products through two complementary approaches: AI-powered relevance detection and keyword-based scraping. The system will help businesses find Reddit posts and comments where users are asking questions or expressing needs that align with their SaaS offerings.

## Requirements

### Requirement 1

**User Story:** As a SaaS business owner, I want to use AI to intelligently find relevant Reddit posts without traditional scraping, so that I can discover high-quality leads based on context and intent rather than just keyword matching.

#### Acceptance Criteria

1. WHEN the AI search is initiated THEN the system SHALL use web search to find Reddit posts mentioning specified keywords from the last configurable number of days
2. WHEN search results are returned THEN the system SHALL analyze each result for relevance and assign a hotness score from 1-100
3. WHEN processing results THEN the system SHALL extract post title, Reddit link, reply type (post_reply or user_reply), and hotness score
4. WHEN results are processed THEN the system SHALL return up to 10 high-quality leads ranked by relevance
5. IF no relevant results are found THEN the system SHALL return an empty result set with appropriate messaging

### Requirement 2

**User Story:** As a SaaS business owner, I want to scrape Reddit for keyword-based leads with subreddit filtering, so that I can systematically monitor specific communities for potential customers mentioning relevant terms.

#### Acceptance Criteria

1. WHEN keyword scraping is initiated THEN the system SHALL fetch latest posts and comments from specified subreddits or r/all
2. WHEN processing Reddit data THEN the system SHALL filter content based on configurable keyword lists
3. WHEN a keyword match is found THEN the system SHALL extract author, subreddit, text content, permalink, timestamp, and content type
4. WHEN subreddit filtering is enabled THEN the system SHALL only search within specified subreddit communities
5. WHEN scraping is complete THEN the system SHALL save results to a structured JSON format
6. IF rate limits are encountered THEN the system SHALL implement appropriate delays and retry logic

### Requirement 3

**User Story:** As a developer, I want a unified backend API that combines both AI and scraping approaches, so that I can choose the best method for different use cases and compare results.

#### Acceptance Criteria

1. WHEN the backend is called THEN the system SHALL support both AI-powered and scraping-based lead generation methods
2. WHEN configuration is provided THEN the system SHALL accept parameters for keywords, time ranges, subreddit filters, and result limits
3. WHEN results are returned THEN the system SHALL provide a consistent data structure regardless of the method used
4. WHEN both methods are used THEN the system SHALL allow comparison and deduplication of results
5. IF authentication is required THEN the system SHALL securely handle Reddit API credentials and Anthropic API keys

### Requirement 4

**User Story:** As a SaaS business owner, I want to configure search parameters and filters, so that I can target specific markets, timeframes, and communities relevant to my business.

#### Acceptance Criteria

1. WHEN configuring searches THEN the system SHALL accept customizable keyword lists for different SaaS categories
2. WHEN setting time filters THEN the system SHALL support configurable date ranges for recent content
3. WHEN targeting communities THEN the system SHALL support both specific subreddit filtering and r/all searches
4. WHEN setting limits THEN the system SHALL accept configurable result limits to control output volume
5. IF invalid configuration is provided THEN the system SHALL validate inputs and return appropriate error messages

### Requirement 5

**User Story:** As a business user, I want to receive structured lead data with quality indicators, so that I can prioritize my outreach efforts and focus on the most promising opportunities.

#### Acceptance Criteria

1. WHEN leads are generated THEN the system SHALL provide structured data including author, content, link, timestamp, and source method
2. WHEN AI analysis is used THEN the system SHALL include relevance scores and intent indicators
3. WHEN scraping is used THEN the system SHALL include keyword match information and subreddit context
4. WHEN results are formatted THEN the system SHALL ensure consistent JSON structure for easy integration
5. IF duplicate leads are found THEN the system SHALL implement deduplication logic based on permalink or content similarity