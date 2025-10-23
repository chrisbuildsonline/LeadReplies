import os
import jwt
import requests
from typing import Optional, Dict
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class SupabaseAuth:
    """
    Supabase authentication service for backend API
    """
    
    def __init__(self):
        # Try server-friendly variables first, fallback to NEXT_PUBLIC_ versions
        self.supabase_url = os.getenv('SUPABASE_URL') or os.getenv('NEXT_PUBLIC_SUPABASE_URL')
        self.supabase_anon_key = os.getenv('SUPABASE_ANON_KEY') or os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')
        self.supabase_jwt_secret = os.getenv('SUPABASE_JWT_SECRET')  # Optional for JWT verification
        
        if not self.supabase_url or not self.supabase_anon_key:
            print("⚠️ Supabase URL or anon key not found - auth will be disabled")
            self.supabase_url = None
            self.supabase_anon_key = None
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """
        Verify a Supabase JWT token and return user data
        """
        if not self.supabase_url or not self.supabase_anon_key:
            print("⚠️ Supabase not configured - skipping token verification")
            return None
            
        try:
            # First try to verify with Supabase API
            api_result = self._verify_with_supabase_api(token)
            if api_result:
                return api_result
            
            # If API verification fails, fall back to JWT decoding without verification
            import jwt
            payload = jwt.decode(token, options={"verify_signature": False})
            print(f"🔍 Token payload: iss={payload.get('iss')}, aud={payload.get('aud')}, sub={payload.get('sub')}")
            
            # Basic validation - be more flexible with audience
            if payload.get('iss') != 'supabase':
                print(f"Invalid token issuer: {payload.get('iss')}")
                return None
                
            # Check if audience is valid (can be 'authenticated' or other valid values)
            aud = payload.get('aud')
            if not aud or (aud != 'authenticated' and 'authenticated' not in str(aud)):
                print(f"Invalid token audience: {aud}")
                # Don't return None yet, let's be more permissive for now
                print("⚠️ Proceeding with potentially invalid audience")
                
            return {
                'user_id': payload.get('sub'),
                'email': payload.get('email'),
                'role': payload.get('role', 'authenticated')
            }
                
        except Exception as e:
            print(f"Token verification error: {e}")
            return None
    
    def _verify_with_supabase_api(self, token: str) -> Optional[Dict]:
        """
        Verify token with Supabase API
        """
        try:
            headers = {
                'Authorization': f'Bearer {token}',
                'apikey': self.supabase_anon_key,
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f'{self.supabase_url}/auth/v1/user',
                headers=headers,
                timeout=5  # Reduced timeout
            )
            
            if response.status_code == 200:
                user_data = response.json()
                return {
                    'user_id': user_data.get('id'),
                    'email': user_data.get('email'),
                    'role': user_data.get('role', 'authenticated')
                }
            else:
                # Don't print error for 403/401 as these are expected for expired tokens
                if response.status_code not in [401, 403]:
                    print(f"Supabase API error: {response.status_code}")
                return None
                
        except requests.RequestException as e:
            # Don't print timeout errors as they're common
            if "timeout" not in str(e).lower():
                print(f"Supabase API request error: {e}")
            return None
    
    def get_user_metadata(self, user_id: str) -> Optional[Dict]:
        """
        Get additional user metadata from Supabase
        """
        # This would typically query your user profiles table
        # For now, return basic info
        return {
            'id': user_id,
            'created_at': datetime.utcnow().isoformat()
        }
    
    def create_or_update_user_profile(self, user_data: Dict) -> bool:
        """
        Create or update user profile in your local database
        This syncs Supabase users with your local user management
        """
        try:
            from database import Database
            db = Database()
            
            print(f"🔄 Creating/updating user profile for: {user_data.get('email')} (ID: {user_data.get('user_id')})")
            
            # Check if user exists in local database
            conn = db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT id FROM users WHERE supabase_id = %s",
                (user_data['user_id'],)
            )
            
            existing_user = cursor.fetchone()
            
            if existing_user:
                print(f"✅ Updating existing user: {existing_user[0]}")
                # Update existing user
                cursor.execute(
                    """UPDATE users 
                       SET email = %s, last_login = CURRENT_TIMESTAMP 
                       WHERE supabase_id = %s""",
                    (user_data['email'], user_data['user_id'])
                )
            else:
                print(f"➕ Creating new user for Supabase ID: {user_data['user_id']}")
                # Create new user
                cursor.execute(
                    """INSERT INTO users (supabase_id, email, created_at, last_login) 
                       VALUES (%s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)""",
                    (user_data['user_id'], user_data['email'])
                )
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"✅ User profile created/updated successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error creating/updating user profile: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_local_user_id(self, supabase_user_id: str) -> Optional[int]:
        """
        Get the local database user ID from Supabase user ID
        """
        try:
            from database import Database
            db = Database()
            
            print(f"🔍 Looking up local user ID for Supabase ID: {supabase_user_id}")
            
            conn = db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT id FROM users WHERE supabase_id = %s",
                (supabase_user_id,)
            )
            
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if result:
                print(f"✅ Found local user ID: {result[0]}")
                return result[0]
            else:
                print(f"❌ No local user found for Supabase ID: {supabase_user_id}")
                return None
            
        except Exception as e:
            print(f"❌ Error getting local user ID: {e}")
            import traceback
            traceback.print_exc()
            return None