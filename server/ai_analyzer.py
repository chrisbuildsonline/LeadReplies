import os
import json
from typing import Dict, List
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

class AILeadAnalyzer:
    """
    AI analyzer that evaluates Reddit leads and assigns probability scores.
    Uses Claude to analyze if a post/comment represents a genuine business opportunity.
    """
    
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        
        # Define your business context - customize this for your specific tool/service
        self.business_context = """
        I'm analyzing Reddit posts/comments to find potential customers for business tools and SaaS products.
        I'm particularly interested in:
        - People looking for marketing automation tools
        - Small business owners needing CRM solutions
        - Entrepreneurs seeking productivity tools
        - Companies wanting to automate processes
        - Anyone expressing pain points that software could solve
        """
    
    def analyze_lead(self, lead_data: Dict) -> Dict:
        """
        Analyze a lead and return probability score (0-100) and analysis.
        
        Args:
            lead_data: Dictionary containing lead information
            
        Returns:
            Dict with 'probability' (int 0-100) and 'analysis' (str)
        """
        try:
            # Prepare the content for analysis
            title = lead_data.get('title', '')
            content = lead_data.get('content', '')
            subreddit = lead_data.get('subreddit', '')
            keywords_matched = lead_data.get('keywords_matched', [])
            
            # Create analysis prompt
            prompt = self._create_analysis_prompt(title, content, subreddit, keywords_matched)
            
            # Call Claude API
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",  # Fast and cost-effective
                max_tokens=300,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # Parse response
            analysis_text = response.content[0].text
            probability = self._extract_probability(analysis_text)
            
            return {
                'probability': probability,
                'analysis': analysis_text
            }
            
        except Exception as e:
            print(f"AI analysis error: {str(e)}")
            return {
                'probability': 0,
                'analysis': f"Analysis failed: {str(e)}"
            }
    
    def _create_analysis_prompt(self, title: str, content: str, subreddit: str, keywords: List[str]) -> str:
        """Create the analysis prompt for Claude"""
        return f"""
{self.business_context}

Please analyze this Reddit post and determine the probability (0-100%) that this person would be interested in business/marketing tools or SaaS products.

POST DETAILS:
Title: {title}
Content: {content[:500]}
Subreddit: r/{subreddit}
Matched Keywords: {', '.join(keywords)}

ANALYSIS CRITERIA:
- Are they expressing a business problem or pain point?
- Are they asking for tool/software recommendations?
- Do they seem to be a business owner, entrepreneur, or decision maker?
- Is this a genuine need vs just casual discussion?
- Would they likely have budget for paid solutions?

Please respond with:
1. A probability score (0-100%)
2. Brief reasoning (2-3 sentences)

Format: "Probability: X% - [reasoning]"

Example: "Probability: 85% - User is actively seeking CRM solutions for their growing startup and mentions budget concerns, indicating they're a qualified prospect ready to purchase."
"""
    
    def _extract_probability(self, analysis_text: str) -> int:
        """Extract probability score from Claude's response"""
        try:
            # Look for "Probability: X%" pattern
            import re
            match = re.search(r'Probability:\s*(\d+)%', analysis_text)
            if match:
                return int(match.group(1))
            
            # Fallback: look for any percentage
            match = re.search(r'(\d+)%', analysis_text)
            if match:
                return int(match.group(1))
            
            # If no percentage found, try to infer from keywords
            analysis_lower = analysis_text.lower()
            if any(word in analysis_lower for word in ['high', 'very likely', 'strong']):
                return 75
            elif any(word in analysis_lower for word in ['medium', 'moderate', 'possible']):
                return 50
            elif any(word in analysis_lower for word in ['low', 'unlikely', 'weak']):
                return 25
            else:
                return 0
                
        except Exception:
            return 0
    
    def analyze_batch(self, leads: List[Dict]) -> List[Dict]:
        """
        Analyze multiple leads in batch.
        Returns leads with added AI analysis.
        """
        analyzed_leads = []
        
        print(f"🤖 Analyzing {len(leads)} leads with AI...")
        
        for i, lead in enumerate(leads, 1):
            try:
                print(f"  Analyzing lead {i}/{len(leads)}: {lead.get('title', '')[:50]}...")
                
                analysis = self.analyze_lead(lead)
                
                # Add AI analysis to lead data
                lead['ai_probability'] = analysis['probability']
                lead['ai_analysis'] = analysis['analysis']
                
                analyzed_leads.append(lead)
                
                # Small delay to avoid rate limits
                if i % 5 == 0:  # Every 5 requests
                    print(f"    Processed {i} leads, brief pause...")
                    import time
                    time.sleep(1)
                
            except Exception as e:
                print(f"  ❌ Error analyzing lead {i}: {str(e)}")
                # Add lead without AI analysis
                lead['ai_probability'] = 0
                lead['ai_analysis'] = f"Analysis failed: {str(e)}"
                analyzed_leads.append(lead)
                continue
        
        # Sort by probability score
        analyzed_leads.sort(key=lambda x: x.get('ai_probability', 0), reverse=True)
        
        print(f"✅ AI analysis complete. Top lead: {analyzed_leads[0].get('ai_probability', 0)}%")
        
        return analyzed_leads
    
    def get_high_probability_leads(self, leads: List[Dict], min_probability: int = 70) -> List[Dict]:
        """Filter leads by minimum probability threshold"""
        return [lead for lead in leads if lead.get('ai_probability', 0) >= min_probability]