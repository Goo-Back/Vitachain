"""Direct HTTP client for Supabase to bypass library issues."""

import requests
import json
from typing import Dict, Any, Optional
from app.core.logging import get_logger
from app.core.config import get_settings

logger = get_logger(__name__)


class SupabaseHTTPClient:
    """Direct HTTP client for Supabase REST API."""
    
    def __init__(self, service_role: bool = False):
        """Initialize Supabase HTTP client."""
        self.settings = get_settings()
        self.service_role = service_role
        self.base_url = f"{self.settings.supabase_url}/rest/v1"
        
        if service_role:
            self.api_key = getattr(self.settings, 'supabase_service_role_key', None)
        else:
            self.api_key = getattr(self.settings, 'supabase_anon_key', None)
            
        if not self.api_key:
            raise ValueError("API key is required for Supabase client")
            
        self.headers = {
            "apikey": self.api_key,
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
    
    def test_connection(self) -> bool:
        """Test connection to Supabase."""
        try:
            response = requests.get(
                f"{self.base_url}/",
                headers=self.headers,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Supabase connection test failed: {e}")
            return False
    
    def sign_up(self, email: str, password: str, user_metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Sign up a new user using Supabase Auth API."""
        try:
            auth_url = f"{self.settings.supabase_url}/auth/v1/signup"
            headers = {
                "apikey": self.api_key,
                "Content-Type": "application/json"
            }
            
            data = {
                "email": email,
                "password": password,
                "options": {
                    "data": user_metadata or {}
                }
            }
            
            response = requests.post(auth_url, headers=headers, json=data, timeout=10)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "user": response.json(),
                    "message": "User registered successfully"
                }
            else:
                return {
                    "success": False,
                    "error": response.json(),
                    "status_code": response.status_code
                }
        except Exception as e:
            logger.error(f"Supabase signup failed: {e}")
            return {
                "success": False,
                "error": {"message": str(e)}
            }
    
    def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """Sign in a user using Supabase Auth API."""
        try:
            auth_url = f"{self.settings.supabase_url}/auth/v1/token?grant_type=password"
            headers = {
                "apikey": self.api_key,
                "Content-Type": "application/json"
            }
            
            data = {
                "email": email,
                "password": password
            }
            
            response = requests.post(auth_url, headers=headers, json=data, timeout=10)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "session": response.json(),
                    "message": "User signed in successfully"
                }
            else:
                return {
                    "success": False,
                    "error": response.json(),
                    "status_code": response.status_code
                }
        except Exception as e:
            logger.error(f"Supabase sign in failed: {e}")
            return {
                "success": False,
                "error": {"message": str(e)}
            }
    
    def get_user(self, access_token: str) -> Dict[str, Any]:
        """Get user information using access token."""
        try:
            auth_url = f"{self.settings.supabase_url}/auth/v1/user"
            headers = {
                "apikey": self.api_key,
                "Authorization": f"Bearer {access_token}"
            }
            
            response = requests.get(auth_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "user": response.json()
                }
            else:
                return {
                    "success": False,
                    "error": response.json(),
                    "status_code": response.status_code
                }
        except Exception as e:
            logger.error(f"Supabase get user failed: {e}")
            return {
                "success": False,
                "error": {"message": str(e)}
            }
    
    def sign_out(self, access_token: str) -> Dict[str, Any]:
        """Sign out a user."""
        try:
            auth_url = f"{self.settings.supabase_url}/auth/v1/logout"
            headers = {
                "apikey": self.api_key,
                "Authorization": f"Bearer {access_token}"
            }
            
            response = requests.post(auth_url, headers=headers, timeout=10)
            
            if response.status_code == 204:
                return {
                    "success": True,
                    "message": "User signed out successfully"
                }
            else:
                return {
                    "success": False,
                    "error": response.json() if response.text else {"message": "Logout failed"},
                    "status_code": response.status_code
                }
        except Exception as e:
            logger.error(f"Supabase sign out failed: {e}")
            return {
                "success": False,
                "error": {"message": str(e)}
            }


def get_supabase_http_client(service_role: bool = False) -> SupabaseHTTPClient:
    """Get Supabase HTTP client instance."""
    return SupabaseHTTPClient(service_role=service_role)
