import os
import requests
import json
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

class DeepSeekAnalyzer:
    """
    AI analyzer using DeepSeek API for lead analysis and keyword extraction
    """
    
    def __init__(self):
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        self.base_url = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com/v1')
        
        if not self.api_key:
            print("⚠️  WARNING: DEEPSEEK_API_KEY not found in environment variables")
            print("   AI analysis features will be disabled until API key is provided")
            self.api_key = None
    
    def _make_request(self, messages: List[Dict], max_tokens: int = 500) -> Optional[str]:
        """Make a request to DeepSeek API"""
        if not self.api_key:
            print("⚠️  DeepSeek API key not available - skipping AI analysis")
            return None
            
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'deepseek-chat',
                'messages': messages,
                'max_tokens': max_tokens,
                'temperature': 0.7
            }
            
            response = requests.post(
                f'{self.base_url}/chat/completions',
                headers=headers,
                json=data,
                timeout=45  # Increased timeout for batch requests
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                print(f"DeepSeek API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"DeepSeek API request failed: {e}")
            return None
    
    def analyze_website_for_keywords(self, website_url: str, business_name: str, 
                                   business_description: str = "") -> List[Dict]:
        """
        Analyze a website and extract relevant keywords for lead tracking
        Returns list of keywords with priority and source
        """
        if not self.api_key:
            print("⚠️  DeepSeek API key not available - returning empty keywords list")
            return []
        prompt = f"""
        Analyze this business and suggest 15-20 relevant keywords for finding potential customers on Reddit.

        Business: {business_name}
        Website: {website_url}
        Description: {business_description}

        Focus on:
        1. Pain points your target customers might express
        2. Problems your product/service solves
        3. Industry-specific terms
        4. Competitor mentions
        5. Solution-seeking language

        Return ONLY a JSON array of objects with this format:
        [
            {{"keyword": "keyword phrase", "priority": 1, "reason": "why this keyword is relevant"}},
            {{"keyword": "another keyword", "priority": 2, "reason": "explanation"}}
        ]

        Priority levels: 1=high (most likely to find customers), 2=medium, 3=low
        """
        
        messages = [
            {"role": "system", "content": "You are an expert at identifying customer pain points and search patterns for lead generation."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._make_request(messages, max_tokens=800)
        
        if response:
            try:
                # Extract JSON from response
                json_start = response.find('[')
                json_end = response.rfind(']') + 1
                if json_start != -1 and json_end != -1:
                    json_str = response[json_start:json_end]
                    keywords_data = json.loads(json_str)
                    
                    # Format for database
                    formatted_keywords = []
                    for kw in keywords_data:
                        formatted_keywords.append({
                            'keyword': kw.get('keyword', '').strip(),
                            'source': 'ai_website',
                            'priority': kw.get('priority', 2),
                            'reason': kw.get('reason', '')
                        })
                    
                    return formatted_keywords
                    
            except json.JSONDecodeError as e:
                print(f"Failed to parse keywords JSON: {e}")
                print(f"Response was: {response}")
        
        return []
    

    
    def analyze_lead_for_business(self, lead_title: str, lead_content: str, 
                                 business_keywords: List[str], business_name: str,
                                 business_description: str = "", buying_intent: str = "") -> Dict:
        """
        Analyze if a lead is relevant for a specific business
        Returns probability score and analysis
        """
        if not self.api_key:
            print("⚠️  DeepSeek API key not available - returning default analysis")
            return {
                "probability": 50,
                "analysis": "AI analysis unavailable - API key not configured",
                "matched_keywords": business_keywords[:3] if business_keywords else []
            }
        keywords_str = ", ".join(business_keywords)
        
        # Build the buying intent section
        buying_intent_section = ""
        if buying_intent and buying_intent.strip():
            buying_intent_section = f"""
        QUALIFIED LEAD CRITERIA:
        {buying_intent}
        
        IMPORTANT: A lead is only HIGH QUALITY (80%+) if they match the buying intent criteria above. 
        If they don't match the specific buying intent, score them lower even if they mention keywords."""
        
        prompt = f"""
        Analyze this Reddit post to determine if the person would be interested in our business solution.

        OUR BUSINESS:
        Name: {business_name}
        Description: {business_description}
        Target Keywords: {keywords_str}
        {buying_intent_section}

        REDDIT POST:
        Title: {lead_title}
        Content: {lead_content}

        Analyze:
        1. Does this person have a problem our business solves?
        2. Are they actively seeking solutions?
        3. Do they seem to be a decision maker with budget?
        4. Is this a genuine business need vs casual discussion?
        5. How well do they match our target customer profile?
        6. MOST IMPORTANT: Do they match the specific buying intent criteria defined above?

        Return ONLY a JSON object:
        {{
            "probability": 85,
            "analysis": "User is actively seeking CRM solutions for their growing startup and mentions budget concerns, indicating they're a qualified prospect ready to purchase.",
            "matched_keywords": ["CRM", "startup", "budget"],
            "decision_maker_likelihood": "high",
            "urgency_level": "medium",
            "buying_intent_match": "high"
        }}

        Probability: 0-100 (0=not relevant, 100=perfect match)
        Use 80%+ ONLY if they clearly match the buying intent criteria.
        """
        
        messages = [
            {"role": "system", "content": "You are an expert at qualifying business leads and identifying potential customers."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._make_request(messages, max_tokens=400)
        
        if response:
            try:
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start != -1 and json_end != -1:
                    json_str = response[json_start:json_end]
                    analysis_data = json.loads(json_str)
                    
                    return {
                        'probability': analysis_data.get('probability', 0),
                        'analysis': analysis_data.get('analysis', 'Analysis failed'),
                        'matched_keywords': analysis_data.get('matched_keywords', []),
                        'decision_maker_likelihood': analysis_data.get('decision_maker_likelihood', 'unknown'),
                        'urgency_level': analysis_data.get('urgency_level', 'unknown'),
                        'buying_intent_match': analysis_data.get('buying_intent_match', 'unknown')
                    }
                    
            except json.JSONDecodeError as e:
                print(f"Failed to parse analysis JSON: {e}")
        
        return {
            'probability': 0,
            'analysis': 'AI analysis failed',
            'matched_keywords': [],
            'decision_maker_likelihood': 'unknown',
            'urgency_level': 'unknown'
        }
    
    def batch_analyze_leads_for_business(self, leads: List[Dict], business_keywords: List[str], 
                                       business_name: str, business_description: str = "", buying_intent: str = "") -> List[Dict]:
        """
        Analyze multiple leads in batch for efficiency (up to 10 at a time).
        """
        if not leads:
            return []
            
        if not self.api_key:
            print("⚠️  DeepSeek API key not available - returning default analysis for all leads")
            return [{
                **lead,
                "probability": 50,
                "analysis": "AI analysis unavailable - API key not configured",
                "matched_keywords": business_keywords[:3] if business_keywords else []
            } for lead in leads]
        
        keywords_str = ", ".join(business_keywords)
        
        # Build concise batch analysis prompt
        leads_text = ""
        for i, lead in enumerate(leads, 1):
            title = lead.get('title', 'No title')[:100]
            content = lead.get('content', 'No content')[:200]
            leads_text += f"LEAD {i}: {title} | {content}\n"
        
        # Build the buying intent section
        buying_intent_section = ""
        if buying_intent and buying_intent.strip():
            buying_intent_section = f"""
QUALIFIED LEAD CRITERIA: {buying_intent}
IMPORTANT: Score 80%+ ONLY if they match the buying intent criteria above."""
        
        prompt = f"""Business: {business_name} - {business_description[:100]}
Keywords: {keywords_str}
{buying_intent_section}

Analyze these {len(leads)} Reddit posts for business relevance:
{leads_text}

Return JSON array with probability (0-100) and brief analysis:
[{{"lead_id": "1", "probability": 85, "analysis": "Seeking solutions"}}, {{"lead_id": "2", "probability": 20, "analysis": "Not business related"}}]"""
        
        messages = [
            {"role": "system", "content": "You are an expert at qualifying business leads and identifying potential customers. Analyze each lead carefully and return valid JSON."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._make_request(messages, max_tokens=1200)
        
        if response:
            try:
                # Extract JSON from response
                json_start = response.find('[')
                json_end = response.rfind(']') + 1
                if json_start != -1 and json_end != -1:
                    json_str = response[json_start:json_end]
                    analyses = json.loads(json_str)
                    
                    # Match analyses back to leads using position-based matching
                    analyzed_leads = []
                    for i, lead in enumerate(leads):
                        # Use position-based matching (simpler and more reliable)
                        if i < len(analyses):
                            analysis = analyses[i]
                            analyzed_leads.append({
                                **lead,
                                'probability': analysis.get('probability', 0),
                                'analysis': analysis.get('analysis', 'No analysis'),
                                'ai_matched_keywords': [],  # Simplified for batch processing
                                'decision_maker_likelihood': 'unknown',
                                'urgency_level': 'unknown'
                            })
                        else:
                            # Fallback if no analysis found
                            analyzed_leads.append({
                                **lead,
                                'probability': 0,
                                'analysis': 'Analysis not found',
                                'ai_matched_keywords': [],
                                'decision_maker_likelihood': 'unknown',
                                'urgency_level': 'unknown'
                            })
                    
                    return analyzed_leads
                    
            except json.JSONDecodeError as e:
                print(f"Failed to parse batch analysis JSON: {e}")
                print(f"Response was: {response[:500]}...")
        
        # Fallback: return leads with no analysis
        return [{
            **lead,
            'probability': 0,
            'analysis': 'Batch analysis failed',
            'ai_matched_keywords': [],
            'decision_maker_likelihood': 'unknown',
            'urgency_level': 'unknown'
        } for lead in leads]
    
    def comprehensive_business_setup(self, website_url: str, business_name: str) -> Dict:
        """
        Comprehensive AI analysis to set up entire business profile
        """
        if not self.api_key:
            print("⚠️  DeepSeek API key not available - returning default setup")
            return {
                "business_info": {
                    "description": "AI analysis unavailable - API key not configured",
                    "buying_intent": "AI analysis unavailable - API key not configured"
                },
                "keywords": [],
                "ai_settings": {}
            }
        
        prompt = f"""
        Analyze this business website and create a comprehensive setup for lead generation and AI replies.

        Current Business Name: {business_name}
        Website: {website_url}

        IMPORTANT: Carefully analyze the website to find the actual business name. Look for:
        - Company name in the title, header, or about section
        - Brand name displayed prominently
        - Business name in contact information
        - Logo text or company branding
        
        If you find a better/more professional business name on the website, use that instead of the current name.

        Please provide a complete business analysis and setup. Return ONLY a JSON object with this structure:

        {{
            "business_info": {{
                "name": "Extract the actual business name from the website, or improve the current name to be more professional",
                "description": "Clear, professional 2-3 sentence description of what this business does",
                "buying_intent": "Specific description of what constitutes a qualified lead (e.g., 'Someone looking to buy a car', 'Business owners needing web development services')"
            }},
            "keywords": [
                {{"keyword": "relevant keyword 1", "priority": 1}},
                {{"keyword": "relevant keyword 2", "priority": 2}}
            ],
            "ai_settings": {{
                "persona": "Professional AI persona for this business (e.g., 'You are an experienced car sales consultant...')",
                "instructions": "Specific reply instructions (e.g., 'Always mention our free consultation', 'Keep responses helpful and under 200 words')",
                "tone": "professional",
                "service_links": {{
                    "Learn More": "{website_url}",
                    "Contact Us": "{website_url}/contact",
                    "Get Started": "{website_url}/get-started",
                    "Free Quote": "{website_url}/quote"
                }}
            }}
        }}

        Focus on:
        1. EXTRACT THE REAL BUSINESS NAME from the website (check title tags, headers, about pages, contact info)
        2. Understanding the business model and target customers
        3. Identifying pain points customers express online
        4. Creating natural, helpful AI reply strategies
        5. Suggesting 15-20 relevant keywords for lead discovery
        6. Professional but approachable AI persona
        7. Generate realistic service links (try common pages like /contact, /services, /pricing, /about)
        """
        
        messages = [
            {"role": "system", "content": "You are an expert business analyst and marketing strategist. Analyze websites thoroughly and create comprehensive lead generation setups."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._make_request(messages, max_tokens=1500)
        
        if response:
            try:
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start != -1 and json_end != -1:
                    json_str = response[json_start:json_end]
                    setup_data = json.loads(json_str)
                    return setup_data
                    
            except json.JSONDecodeError as e:
                print(f"Failed to parse comprehensive setup JSON: {e}")
        
        # Return fallback setup
        return {
            "business_info": {
                "name": business_name,
                "description": f"Professional {business_name} services",
                "buying_intent": "Someone actively looking for our services"
            },
            "keywords": [
                {"keyword": business_name.lower(), "priority": 1}
            ],
            "ai_settings": {
                "persona": f"You are a helpful representative from {business_name}",
                "instructions": "Provide helpful information about our services",
                "tone": "professional",
                "service_links": {
                    "Learn More": website_url,
                    "Contact Us": f"{website_url}/contact",
                    "Get Started": f"{website_url}/get-started"
                }
            }
        }
    
    def text_based_business_setup(self, business_prompt: str, business_name: str) -> Dict:
        """
        AI analysis based on text description only (no website)
        """
        if not self.api_key:
            print("⚠️  DeepSeek API key not available - returning default setup")
            return {
                "business_info": {
                    "description": "AI analysis unavailable - API key not configured",
                    "buying_intent": "AI analysis unavailable - API key not configured"
                },
                "keywords": [],
                "ai_settings": {}
            }
        
        prompt = f"""
        Based on this business description, create a comprehensive setup for lead generation and AI replies.

        Current Business Name: {business_name}
        Business Description: {business_prompt}

        IMPORTANT: Based on the business description, suggest a more professional/catchy business name if the current one can be improved.

        Please provide a complete business analysis and setup. Return ONLY a JSON object with this structure:

        {{
            "business_info": {{
                "name": "Suggest a professional, catchy business name based on the description (improve current name if possible)",
                "description": "Clear, professional 2-3 sentence description based on the provided information",
                "buying_intent": "Specific description of what constitutes a qualified lead for this business"
            }},
            "keywords": [
                {{"keyword": "relevant keyword 1", "priority": 1}},
                {{"keyword": "relevant keyword 2", "priority": 2}}
            ],
            "ai_settings": {{
                "persona": "Professional AI persona for this business type",
                "instructions": "Specific reply instructions for this business",
                "tone": "professional"
            }}
        }}

        Focus on:
        1. CREATE A BETTER BUSINESS NAME based on the description (make it professional, memorable, and catchy)
        2. Understanding the business model from the description
        3. Identifying what customers would be searching for
        4. Creating natural, helpful AI reply strategies
        5. Suggesting 15-20 relevant keywords for lead discovery
        6. Professional but approachable AI persona

        Note: Do NOT include service_links since no website was provided.
        """
        
        messages = [
            {"role": "system", "content": "You are an expert business analyst. Create comprehensive lead generation setups based on business descriptions."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._make_request(messages, max_tokens=1200)
        
        if response:
            try:
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start != -1 and json_end != -1:
                    json_str = response[json_start:json_end]
                    setup_data = json.loads(json_str)
                    return setup_data
                    
            except json.JSONDecodeError as e:
                print(f"Failed to parse text-based setup JSON: {e}")
        
        # Return fallback setup
        return {
            "business_info": {
                "name": business_name,
                "description": f"Professional {business_name} services based on: {business_prompt[:100]}...",
                "buying_intent": "Someone actively looking for our services"
            },
            "keywords": [
                {"keyword": business_name.lower(), "priority": 1}
            ],
            "ai_settings": {
                "persona": f"You are a helpful representative from {business_name}",
                "instructions": "Provide helpful information about our services",
                "tone": "professional"
            }
        }