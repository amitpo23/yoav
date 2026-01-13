"""
Security Service
Rate limiting, JWT authentication, and security utilities
"""

from typing import Dict, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict
import hashlib
import secrets
import jwt
import os


# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", secrets.token_urlsafe(32))
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24


class RateLimiter:
    """
    Token bucket rate limiter
    """
    
    def __init__(self, requests_per_minute: int = 60, requests_per_hour: int = 1000):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        
        # Track requests by IP/identifier
        self.minute_buckets: Dict[str, list] = defaultdict(list)
        self.hour_buckets: Dict[str, list] = defaultdict(list)
        
        # Blocked IPs
        self.blocked_ips: Dict[str, datetime] = {}
        
        # Whitelist
        self.whitelist: set = set()
    
    def _clean_old_requests(self, bucket: list, seconds: int) -> list:
        """Remove requests older than specified seconds"""
        cutoff = datetime.now() - timedelta(seconds=seconds)
        return [r for r in bucket if r > cutoff]
    
    def is_allowed(self, identifier: str) -> Dict[str, Any]:
        """Check if request is allowed"""
        
        # Check whitelist
        if identifier in self.whitelist:
            return {'allowed': True, 'reason': 'whitelisted'}
        
        # Check if blocked
        if identifier in self.blocked_ips:
            if datetime.now() < self.blocked_ips[identifier]:
                return {
                    'allowed': False,
                    'reason': 'blocked',
                    'retry_after': (self.blocked_ips[identifier] - datetime.now()).seconds
                }
            else:
                del self.blocked_ips[identifier]
        
        now = datetime.now()
        
        # Clean old requests
        self.minute_buckets[identifier] = self._clean_old_requests(
            self.minute_buckets[identifier], 60
        )
        self.hour_buckets[identifier] = self._clean_old_requests(
            self.hour_buckets[identifier], 3600
        )
        
        # Check minute limit
        if len(self.minute_buckets[identifier]) >= self.requests_per_minute:
            return {
                'allowed': False,
                'reason': 'rate_limit_minute',
                'retry_after': 60,
                'limit': self.requests_per_minute
            }
        
        # Check hour limit
        if len(self.hour_buckets[identifier]) >= self.requests_per_hour:
            return {
                'allowed': False,
                'reason': 'rate_limit_hour',
                'retry_after': 3600,
                'limit': self.requests_per_hour
            }
        
        # Add request to buckets
        self.minute_buckets[identifier].append(now)
        self.hour_buckets[identifier].append(now)
        
        return {
            'allowed': True,
            'remaining_minute': self.requests_per_minute - len(self.minute_buckets[identifier]),
            'remaining_hour': self.requests_per_hour - len(self.hour_buckets[identifier])
        }
    
    def block_ip(self, ip: str, hours: int = 1):
        """Block an IP for specified hours"""
        self.blocked_ips[ip] = datetime.now() + timedelta(hours=hours)
    
    def unblock_ip(self, ip: str):
        """Unblock an IP"""
        if ip in self.blocked_ips:
            del self.blocked_ips[ip]
    
    def add_to_whitelist(self, identifier: str):
        """Add to whitelist"""
        self.whitelist.add(identifier)
    
    def remove_from_whitelist(self, identifier: str):
        """Remove from whitelist"""
        self.whitelist.discard(identifier)
    
    def get_stats(self) -> Dict:
        """Get rate limiter statistics"""
        return {
            'active_clients': len(self.minute_buckets),
            'blocked_ips': len(self.blocked_ips),
            'whitelisted': len(self.whitelist)
        }


class JWTManager:
    """
    JWT token management
    """
    
    def __init__(self, secret: str = JWT_SECRET, algorithm: str = JWT_ALGORITHM):
        self.secret = secret
        self.algorithm = algorithm
        self.revoked_tokens: set = set()
    
    def create_token(self, user_id: str, role: str = "user", 
                     extra_claims: Dict = None, expires_hours: int = JWT_EXPIRATION_HOURS) -> str:
        """Create a JWT token"""
        now = datetime.utcnow()
        
        payload = {
            'sub': user_id,
            'role': role,
            'iat': now,
            'exp': now + timedelta(hours=expires_hours),
            'jti': secrets.token_urlsafe(16)  # Unique token ID
        }
        
        if extra_claims:
            payload.update(extra_claims)
        
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
            
            # Check if token is revoked
            if payload.get('jti') in self.revoked_tokens:
                return {'valid': False, 'error': 'Token has been revoked'}
            
            return {
                'valid': True,
                'payload': payload,
                'user_id': payload.get('sub'),
                'role': payload.get('role')
            }
            
        except jwt.ExpiredSignatureError:
            return {'valid': False, 'error': 'Token has expired'}
        except jwt.InvalidTokenError as e:
            return {'valid': False, 'error': f'Invalid token: {str(e)}'}
    
    def revoke_token(self, token: str):
        """Revoke a token"""
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
            if 'jti' in payload:
                self.revoked_tokens.add(payload['jti'])
        except:
            pass
    
    def create_refresh_token(self, user_id: str) -> str:
        """Create a refresh token (longer expiration)"""
        return self.create_token(user_id, role="refresh", expires_hours=24 * 7)
    
    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """Get new access token using refresh token"""
        result = self.verify_token(refresh_token)
        
        if result['valid'] and result.get('role') == 'refresh':
            return self.create_token(result['user_id'], expires_hours=JWT_EXPIRATION_HOURS)
        
        return None


class SecurityService:
    """
    Main security service combining all security features
    """
    
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.jwt_manager = JWTManager()
        self.failed_logins: Dict[str, list] = defaultdict(list)
        self.max_failed_logins = 5
        self.lockout_minutes = 15
    
    def hash_password(self, password: str, salt: str = None) -> Dict[str, str]:
        """Hash a password"""
        if not salt:
            salt = secrets.token_hex(16)
        
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt.encode(),
            100000
        ).hex()
        
        return {'hash': password_hash, 'salt': salt}
    
    def verify_password(self, password: str, password_hash: str, salt: str) -> bool:
        """Verify a password"""
        result = self.hash_password(password, salt)
        return result['hash'] == password_hash
    
    def check_login_attempt(self, identifier: str) -> Dict[str, Any]:
        """Check if login is allowed (not locked out)"""
        now = datetime.now()
        cutoff = now - timedelta(minutes=self.lockout_minutes)
        
        # Clean old attempts
        self.failed_logins[identifier] = [
            t for t in self.failed_logins[identifier] if t > cutoff
        ]
        
        if len(self.failed_logins[identifier]) >= self.max_failed_logins:
            oldest = min(self.failed_logins[identifier])
            unlock_time = oldest + timedelta(minutes=self.lockout_minutes)
            return {
                'allowed': False,
                'reason': 'too_many_attempts',
                'retry_after': (unlock_time - now).seconds
            }
        
        return {'allowed': True}
    
    def record_failed_login(self, identifier: str):
        """Record a failed login attempt"""
        self.failed_logins[identifier].append(datetime.now())
    
    def clear_failed_logins(self, identifier: str):
        """Clear failed logins after successful login"""
        if identifier in self.failed_logins:
            del self.failed_logins[identifier]
    
    def generate_api_key(self) -> str:
        """Generate an API key"""
        return f"hms_{secrets.token_urlsafe(32)}"
    
    def sanitize_input(self, text: str) -> str:
        """Basic input sanitization"""
        # Remove potential XSS/injection patterns
        dangerous_patterns = ['<script', 'javascript:', 'onerror=', 'onclick=']
        result = text
        for pattern in dangerous_patterns:
            result = result.replace(pattern, '')
        return result.strip()
    
    def validate_session_id(self, session_id: str) -> bool:
        """Validate session ID format"""
        import re
        # UUID format
        pattern = r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$'
        return bool(re.match(pattern, session_id.lower()))


# Global instances
rate_limiter = RateLimiter(requests_per_minute=60, requests_per_hour=1000)
jwt_manager = JWTManager()
security_service = SecurityService()
