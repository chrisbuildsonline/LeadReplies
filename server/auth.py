import bcrypt
import jwt
import os
from datetime import datetime, timedelta
from typing import Optional, Dict
from database_v2 import DatabaseV2

class AuthService:
    """
    Authentication service for user login/registration
    """
    
    def __init__(self):
        self.db = DatabaseV2()
        self.jwt_secret = os.getenv('JWT_SECRET', 'your-secret-key-change-this')
        self.jwt_algorithm = 'HS256'
        self.token_expiry_hours = 24 * 7  # 7 days
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def generate_token(self, user_id: int, email: str) -> str:
        """Generate a JWT token for a user"""
        payload = {
            'user_id': user_id,
            'email': email,
            'exp': datetime.utcnow() + timedelta(hours=self.token_expiry_hours),
            'iat': datetime.utcnow()
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify a JWT token and return user data"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return {
                'user_id': payload['user_id'],
                'email': payload['email']
            }
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def register_user(self, email: str, password: str, name: str = None) -> Dict:
        """Register a new user"""
        try:
            # Check if user already exists
            existing_user = self.db.get_user_by_email(email)
            if existing_user:
                return {'success': False, 'error': 'User already exists'}
            
            # Hash password and create user
            password_hash = self.hash_password(password)
            user_id = self.db.create_user(email, password_hash, name)
            
            # Generate token
            token = self.generate_token(user_id, email)
            
            return {
                'success': True,
                'user': {
                    'id': user_id,
                    'email': email,
                    'name': name
                },
                'token': token
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def login_user(self, email: str, password: str) -> Dict:
        """Login a user"""
        try:
            # Get user from database
            user = self.db.get_user_by_email(email)
            if not user:
                return {'success': False, 'error': 'Invalid credentials'}
            
            # Verify password
            if not self.verify_password(password, user['password_hash']):
                return {'success': False, 'error': 'Invalid credentials'}
            
            # Update last login
            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = %s",
                        (user['id'],)
                    )
                    conn.commit()
            
            # Generate token
            token = self.generate_token(user['id'], user['email'])
            
            return {
                'success': True,
                'user': {
                    'id': user['id'],
                    'email': user['email'],
                    'name': user['name']
                },
                'token': token
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_current_user(self, token: str) -> Optional[Dict]:
        """Get current user from token"""
        user_data = self.verify_token(token)
        if not user_data:
            return None
        
        # Get full user data from database
        user = self.db.get_user_by_email(user_data['email'])
        if user:
            return {
                'id': user['id'],
                'email': user['email'],
                'name': user['name']
            }
        
        return None