from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime

# Authentication models
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: Optional[str]

class AuthResponse(BaseModel):
    success: bool
    user: Optional[UserResponse] = None
    token: Optional[str] = None
    error: Optional[str] = None

# Business models
class BusinessCreate(BaseModel):
    name: str
    website_url: Optional[str] = None
    description: Optional[str] = None
    industry: Optional[str] = None

class BusinessResponse(BaseModel):
    id: int
    name: str
    website_url: Optional[str]
    description: Optional[str]
    industry: Optional[str]
    created_at: datetime
    is_active: bool

class WebsiteAnalyzeRequest(BaseModel):
    website_url: str
    business_name: str
    business_description: Optional[str] = ""
    industry: Optional[str] = ""

class KeywordData(BaseModel):
    keyword: str
    source: str = "manual"
    priority: int = 1
    reason: Optional[str] = ""

class KeywordsRequest(BaseModel):
    keywords: List[KeywordData]

class SubredditData(BaseModel):
    subreddit: str
    source: str = "manual"
    reason: Optional[str] = ""

class SubredditsRequest(BaseModel):
    subreddits: List[SubredditData]

# Lead models
class BusinessLead(BaseModel):
    id: int
    title: str
    content: Optional[str]
    url: str
    author: str
    source_location: str
    platform: str
    matched_keywords: List[str]
    ai_probability: int
    ai_analysis: str
    status: str
    created_date: datetime
    processed_at: datetime

class LeadsResponse(BaseModel):
    leads: List[BusinessLead]
    total: int

# Processing models
class ScrapingRequest(BaseModel):
    days_back: int = 1

class ProcessingResult(BaseModel):
    processed: int
    matched: int
    high_quality: int