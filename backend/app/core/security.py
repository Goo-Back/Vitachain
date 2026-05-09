# Security Module for VitaChain
# Handles API key management, validation, rotation, and JWT authentication

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import structlog
from jose import jwt, JWTError
from fastapi import HTTPException, status, Request, Response
from app.core.config import settings

logger = structlog.get_logger("security")

class APIKeyManager:
    """Manages API key generation, validation, and rotation for IoT devices"""
    
    def __init__(self, rotation_period_days: int = 90):
        self.rotation_period_days = rotation_period_days
        
    def generate_api_key(self) -> str:
        """Generate a secure API key for IoT devices"""
        return f"vitachain-{secrets.token_urlsafe(32)}"
    
    def hash_api_key(self, api_key: str) -> str:
        """Hash API key for secure storage"""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    def validate_api_key(self, provided_key: str, stored_hash: str) -> bool:
        """Validate API key against stored hash"""
        return self.hash_api_key(provided_key) == stored_hash
    
    def should_rotate_key(self, created_at: datetime) -> bool:
        """Check if API key needs rotation"""
        return datetime.utcnow() > created_at + timedelta(days=self.rotation_period_days)
    
    def extract_device_id_from_key(self, api_key: str) -> Optional[str]:
        """Extract device ID from API key format"""
        if api_key.startswith("vitachain-"):
            # For now, we'll use a simple approach
            # In production, this would involve database lookup
            return api_key.split("-")[1] if len(api_key.split("-")) > 1 else None
        return None
    
    async def rotate_iot_api_keys(self, supabase_client):
        """Automatically rotate expired IoT API keys"""
        try:
            expiry_date = datetime.utcnow() - timedelta(days=self.rotation_period_days)
            
            # Get expired keys
            result = supabase_client.table("iot_api_keys")\
                .select("*")\
                .lt("created_at", expiry_date.isoformat())\
                .eq("active", True)\
                .execute()
            
            rotated_count = 0
            for key_record in result.data:
                await self._rotate_single_key(supabase_client, key_record)
                rotated_count += 1
            
            logger.info("api_key_rotation_completed", 
                       rotated_keys=rotated_count,
                       severity="info")
            
            return rotated_count
            
        except Exception as e:
            logger.error("api_key_rotation_error", 
                        error=str(e),
                        severity="high")
            raise
    
    async def _rotate_single_key(self, supabase_client, key_record: dict):
        """Rotate a single API key"""
        device_id = key_record["device_id"]
        
        # Generate new key
        new_key = self.generate_api_key()
        new_hash = self.hash_api_key(new_key)
        
        try:
            # Deactivate old key
            supabase_client.table("iot_api_keys")\
                .update({"active": False})\
                .eq("id", key_record["id"])\
                .execute()
            
            # Create new key
            supabase_client.table("iot_api_keys")\
                .insert({
                    "device_id": device_id,
                    "key_hash": new_hash,
                    "created_at": datetime.utcnow().isoformat(),
                    "active": True
                })\
                .execute()
            
            # Log rotation
            logger.info("api_key_rotated",
                       device_id=device_id,
                       old_key_id=key_record["id"],
                       severity="info")
            
            # Notify device (implementation depends on IoT communication method)
            await self._notify_device_key_change(device_id, new_key)
            
        except Exception as e:
            logger.error("single_key_rotation_error",
                        device_id=device_id,
                        error=str(e),
                        severity="medium")
            raise
    
    async def _notify_device_key_change(self, device_id: str, new_key: str):
        """Notify device about key change (placeholder implementation)"""
        # In production, this would send the new key to the IoT device
        # via secure channel (MQTT, LoRaWAN, etc.)
        logger.info("device_key_change_notification",
                   device_id=device_id,
                   notification_sent=True,
                   severity="info")
        
        # For now, we'll just log it
        # In production, implement actual device communication
        pass

class SecurityValidator:
    """Validates security-related requests and data"""
    
    @staticmethod
    def validate_api_request(api_key: str, device_id: str, api_key_manager: APIKeyManager) -> bool:
        """Validate API request with API key"""
        if not api_key or not device_id:
            return False
        
        # Extract device ID from key
        key_device_id = api_key_manager.extract_device_id_from_key(api_key)
        if not key_device_id or key_device_id != device_id:
            return False
        
        # In production, validate against database
        # For now, just check format
        return api_key.startswith("vitachain-") and len(api_key) > 40
    
    @staticmethod
    def sanitize_input(data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize input data to prevent injection attacks"""
        sanitized = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                # Remove potentially dangerous characters
                sanitized[key] = value.replace("<", "&lt;").replace(">", "&gt;")
            else:
                sanitized[key] = value
        
        return sanitized
    
    @staticmethod
    def validate_telemetry_data(data: Dict[str, Any]) -> bool:
        """Validate telemetry data format and ranges"""
        required_fields = ["device_id", "temperature", "humidity"]
        
        if not all(field in data for field in required_fields):
            return False
        
        try:
            # Validate temperature range (-10 to 60 degrees Celsius)
            temp = float(data["temperature"])
            if temp < -10 or temp > 60:
                return False
            
            # Validate humidity range (0 to 100 percent)
            humidity = float(data["humidity"])
            if humidity < 0 or humidity > 100:
                return False
            
            # Validate NDVI range (-1 to 1) if present
            if "ndvi" in data:
                ndvi = float(data["ndvi"])
                if ndvi < -1 or ndvi > 1:
                    return False
            
            return True
            
        except (ValueError, TypeError):
            return False

class SecurityHeaders:
    """Security headers for HTTP responses"""
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """Get comprehensive security headers"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
            "X-RateLimit-Limit": "100",
            "X-RateLimit-Remaining": "99",
            "X-RateLimit-Reset": "60"
        }

class JWTManager:
    """Manages JWT token validation and user authentication"""
    
    @staticmethod
    def validate_jwt_token(token: str) -> Dict[str, Any]:
        """
        Validate JWT token and extract user information
        
        Args:
            token: JWT token from cookie
            
        Returns:
            User information from token payload
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            payload = jwt.decode(
                token, 
                settings.SUPABASE_JWT_SECRET, 
                algorithms=["HS256"]
            )
            
            # Extract user information
            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "code": "INVALID_TOKEN",
                        "message": "Invalid token: missing user ID"
                    }
                )
            
            # Extract role from user metadata
            user_metadata = payload.get("user_metadata", {})
            role = user_metadata.get("role")
            
            # Extract email
            email = payload.get("email")
            
            return {
                "user_id": user_id,
                "email": email,
                "role": role,
                "user_metadata": user_metadata
            }
            
        except JWTError as e:
            logger.warning(
                "JWT validation failed",
                error=str(e),
                severity="medium"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "INVALID_TOKEN",
                    "message": "Invalid or expired token"
                }
            )
    
    @staticmethod
    def set_auth_cookie(response: Response, access_token: str, refresh_token: str = None):
        """
        Set httpOnly authentication cookies
        
        Args:
            response: FastAPI response object
            access_token: JWT access token
            refresh_token: JWT refresh token (optional)
        """
        # Set access token cookie
        response.set_cookie(
            key="sb-access-token",
            value=access_token,
            httponly=True,
            secure=True,  # HTTPS only
            samesite="lax",
            max_age=24 * 60 * 60  # 24 hours
        )
        
        # Set refresh token cookie if provided
        if refresh_token:
            response.set_cookie(
                key="sb-refresh-token",
                value=refresh_token,
                httponly=True,
                secure=True,  # HTTPS only
                samesite="lax",
                max_age=30 * 24 * 60 * 60  # 30 days
            )
    
    @staticmethod
    def clear_auth_cookies(response: Response):
        """
        Clear authentication cookies
        
        Args:
            response: FastAPI response object
        """
        response.delete_cookie(key="sb-access-token")
        response.delete_cookie(key="sb-refresh-token")
    
    @staticmethod
    def get_dashboard_redirect_url(role: str) -> str:
        """
        Get dashboard redirect URL based on user role
        
        Args:
            role: User role
            
        Returns:
            Dashboard URL for the role
        """
        role_dashboards = {
            "FARMER": "/dashboard/katara",
            "RESTAURANT": "/dashboard/secondserve",
            "CITIZEN": "/dashboard/secondserve",
            "ADMIN": "/dashboard/admin",
            "SUPPORT": "/dashboard/support"
        }
        
        return role_dashboards.get(role, "/dashboard")


class MagicLinkManager:
    """Manages magic link token generation and validation for passwordless authentication"""
    
    def __init__(self, expiry_minutes: int = 15):
        self.expiry_minutes = expiry_minutes
        
    def generate_token(self, email: str) -> str:
        """
        Generate secure magic link token
        
        Args:
            email: User email address
            
        Returns:
            JWT token for magic link authentication
        """
        now = datetime.utcnow()
        payload = {
            'email': email,
            'exp': now + timedelta(minutes=self.expiry_minutes),
            'iat': now,
            'jti': secrets.token_urlsafe(16),  # Unique identifier for single-use
            'type': 'magic_link'
        }
        
        return jwt.encode(
            payload, 
            settings.SUPABASE_JWT_SECRET, 
            algorithm='HS256'
        )
    
    def validate_token(self, token: str) -> dict:
        """
        Validate magic link token and extract user information
        
        Args:
            token: Magic link JWT token
            
        Returns:
            Decoded token payload
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            payload = jwt.decode(
                token, 
                settings.SUPABASE_JWT_SECRET, 
                algorithms=['HS256']
            )
            
            # Verify token type
            if payload.get('type') != 'magic_link':
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "code": "INVALID_TOKEN_TYPE",
                        "message": "Invalid token type"
                    }
                )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning(
                "Magic link token expired",
                token_preview=token[:10] + "..." if len(token) > 10 else token
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "MAGIC_LINK_EXPIRED",
                    "message": "Magic link has expired"
                }
            )
        except jwt.InvalidTokenError as e:
            logger.warning(
                "Invalid magic link token",
                error=str(e),
                token_preview=token[:10] + "..." if len(token) > 10 else token
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "INVALID_MAGIC_LINK",
                    "message": "Invalid or expired magic link"
                }
            )
    
    def extract_email_from_token(self, token: str) -> str:
        """
        Extract email from magic link token
        
        Args:
            token: Magic link JWT token
            
        Returns:
            Email address from token
        """
        payload = self.validate_token(token)
        return payload.get('email')
    
    def is_token_expired(self, token: str) -> bool:
        """
        Check if magic link token is expired
        
        Args:
            token: Magic link JWT token
            
        Returns:
            True if token is expired, False otherwise
        """
        try:
            self.validate_token(token)
            return False
        except HTTPException as e:
            return e.detail.get("code") == "MAGIC_LINK_EXPIRED"


class MagicLinkRateLimiter:
    """Rate limiting for magic link requests"""
    
    def __init__(self):
        # In production, use Redis or similar
        self.request_store = {}
        
    def check_rate_limit(self, email: str, ip: str) -> tuple[bool, str]:
        """
        Check if magic link request is within rate limits
        
        Args:
            email: User email address
            ip: Client IP address
            
        Returns:
            Tuple of (allowed, reason_if_denied)
        """
        now = datetime.utcnow()
        cutoff_1h = now - timedelta(hours=1)
        
        # Clean old entries
        keys_to_remove = []
        for key, timestamps in self.request_store.items():
            self.request_store[key] = [ts for ts in timestamps if ts > cutoff_1h]
            if not self.request_store[key]:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.request_store[key]
        
        # Check email rate limit (3 per hour)
        email_key = f"magic_email_{email}"
        if email_key in self.request_store:
            email_requests = len(self.request_store[email_key])
            if email_requests >= 3:
                return False, "Too many magic link requests for this email"
        
        # Check IP rate limit (10 per hour)
        ip_key = f"magic_ip_{ip}"
        if ip_key in self.request_store:
            ip_requests = len(self.request_store[ip_key])
            if ip_requests >= 10:
                return False, "Too many magic link requests from this IP"
        
        # Record this request
        if email_key not in self.request_store:
            self.request_store[email_key] = []
        if ip_key not in self.request_store:
            self.request_store[ip_key] = []
            
        self.request_store[email_key].append(now)
        self.request_store[ip_key].append(now)
        
        return True, ""


class PasswordValidator:
    """Validates password strength and security requirements"""
    
    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, list[str]]:
        """
        Validate password meets security requirements
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check minimum length
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        # Check for uppercase letter
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        # Check for lowercase letter
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        # Check for number
        if not re.search(r'\d', password):
            errors.append("Password must contain at least one number")
        
        # Check for special character (optional but recommended)
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password should contain at least one special character")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def get_password_strength_score(password: str) -> dict:
        """
        Get password strength score and feedback
        
        Args:
            password: Password to evaluate
            
        Returns:
            Dictionary with strength score and feedback
        """
        score = 0
        feedback = []
        
        # Length scoring
        if len(password) >= 8:
            score += 20
        if len(password) >= 12:
            score += 10
        if len(password) >= 16:
            score += 10
        
        # Character variety scoring
        if re.search(r'[a-z]', password):
            score += 15
            feedback.append("Contains lowercase letters")
        else:
            feedback.append("Add lowercase letters")
        
        if re.search(r'[A-Z]', password):
            score += 15
            feedback.append("Contains uppercase letters")
        else:
            feedback.append("Add uppercase letters")
        
        if re.search(r'\d', password):
            score += 15
            feedback.append("Contains numbers")
        else:
            feedback.append("Add numbers")
        
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            score += 15
            feedback.append("Contains special characters")
        else:
            feedback.append("Add special characters")
        
        # Common patterns penalty
        if re.search(r'(.)\1{2,}', password):  # Repeated characters
            score -= 10
            feedback.append("Avoid repeated characters")
        
        if re.search(r'123456|qwerty|password|admin', password.lower()):  # Common patterns
            score -= 20
            feedback.append("Avoid common patterns")
        
        # Determine strength level
        if score >= 80:
            strength = "very_strong"
        elif score >= 60:
            strength = "strong"
        elif score >= 40:
            strength = "medium"
        elif score >= 20:
            strength = "weak"
        else:
            strength = "very_weak"
        
        return {
            "score": max(0, min(100, score)),
            "strength": strength,
            "feedback": feedback
        }


class PasswordResetRateLimiter:
    """Rate limiting for password reset requests"""
    
    def __init__(self):
        # In production, use Redis or similar
        self.request_store = {}
        
    def check_rate_limit(self, email: str, ip: str) -> tuple[bool, str]:
        """
        Check if password reset request is within rate limits
        
        Args:
            email: User email address
            ip: Client IP address
            
        Returns:
            Tuple of (allowed, reason_if_denied)
        """
        now = datetime.utcnow()
        cutoff_1h = now - timedelta(hours=1)
        
        # Clean old entries
        keys_to_remove = []
        for key, timestamps in self.request_store.items():
            self.request_store[key] = [ts for ts in timestamps if ts > cutoff_1h]
            if not self.request_store[key]:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.request_store[key]
        
        # Check email rate limit (3 per hour)
        email_key = f"reset_email_{email}"
        if email_key in self.request_store:
            email_requests = len(self.request_store[email_key])
            if email_requests >= 3:
                return False, "Too many password reset requests for this email"
        
        # Check IP rate limit (10 per hour)
        ip_key = f"reset_ip_{ip}"
        if ip_key in self.request_store:
            ip_requests = len(self.request_store[ip_key])
            if ip_requests >= 10:
                return False, "Too many password reset requests from this IP"
        
        # Record this request
        if email_key not in self.request_store:
            self.request_store[email_key] = []
        if ip_key not in self.request_store:
            self.request_store[ip_key] = []
            
        self.request_store[email_key].append(now)
        self.request_store[ip_key].append(now)
        
        return True, ""


# Import regex for password validation
import re

# Global instances
api_key_manager = APIKeyManager()
security_validator = SecurityValidator()
security_headers = SecurityHeaders()
jwt_manager = JWTManager()
magic_link_manager = MagicLinkManager()
magic_link_rate_limiter = MagicLinkRateLimiter()
password_validator = PasswordValidator()
password_reset_rate_limiter = PasswordResetRateLimiter()
