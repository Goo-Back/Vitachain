"""
Session management service for VitaChain
Handles session creation, validation, and invalidation
"""

import uuid
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from supabase import Client

from app.core.logging import get_logger
from app.core.database import get_supabase_client

logger = get_logger(__name__)


class SessionService:
    """Service for managing user sessions with database tracking"""
    
    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.session_timeout_hours = 24  # Default session timeout
    
    async def create_session(
        self, 
        user_id: str, 
        session_id: str, 
        device_info: Dict[str, Any] = None,
        ip_address: str = None,
        user_agent: str = None
    ) -> bool:
        """
        Create a new session in the database
        
        Args:
            user_id: User UUID
            session_id: JWT jti claim
            device_info: Device fingerprint and details
            ip_address: Client IP address
            user_agent: Browser user agent string
            
        Returns:
            True if session created successfully
        """
        try:
            expires_at = datetime.utcnow() + timedelta(hours=self.session_timeout_hours)
            
            session_data = {
                'user_id': user_id,
                'session_id': session_id,
                'device_info': device_info or {},
                'ip_address': ip_address,
                'user_agent': user_agent,
                'expires_at': expires_at.isoformat(),
                'is_active': True
            }
            
            result = self.supabase.table('user_sessions').insert(session_data).execute()
            
            if result.data:
                logger.info(
                    "session_created",
                    user_id=user_id,
                    session_id=session_id,
                    expires_at=expires_at.isoformat()
                )
                return True
            else:
                logger.error(
                    "session_creation_failed",
                    user_id=user_id,
                    session_id=session_id,
                    error=result.error
                )
                return False
                
        except Exception as e:
            logger.error(
                "session_creation_error",
                user_id=user_id,
                session_id=session_id,
                error=str(e)
            )
            return False
    
    async def validate_session(self, session_id: str, user_id: str) -> bool:
        """
        Validate if a session is still active and not expired
        
        Args:
            session_id: JWT jti claim
            user_id: User UUID from JWT
            
        Returns:
            True if session is valid and active
        """
        try:
            result = self.supabase.table('user_sessions').select(
                'id', 'expires_at', 'is_active', 'user_id'
            ).eq('session_id', session_id).eq('is_active', True).single().execute()
            
            if not result.data:
                logger.warning(
                    "session_not_found",
                    session_id=session_id,
                    user_id=user_id
                )
                return False
            
            session = result.data[0]
            
            # Check if session belongs to user
            if session['user_id'] != user_id:
                logger.warning(
                    "session_user_mismatch",
                    session_id=session_id,
                    session_user_id=session['user_id'],
                    jwt_user_id=user_id
                )
                return False
            
            # Check if session is expired
            expires_at = datetime.fromisoformat(session['expires_at'].replace('Z', '+00:00'))
            if datetime.utcnow() > expires_at:
                logger.info(
                    "session_expired",
                    session_id=session_id,
                    user_id=user_id,
                    expires_at=expires_at.isoformat()
                )
                # Mark as expired
                await self._mark_session_expired(session_id)
                return False
            
            # Update last accessed time
            await self._update_last_accessed(session_id)
            
            return True
            
        except Exception as e:
            logger.error(
                "session_validation_error",
                session_id=session_id,
                user_id=user_id,
                error=str(e)
            )
            return False
    
    async def invalidate_session(
        self, 
        session_id: str, 
        user_id: str, 
        logout_reason: str = "user_initiated"
    ) -> bool:
        """
        Invalidate a specific session
        
        Args:
            session_id: JWT jti claim
            user_id: User UUID
            logout_reason: Reason for logout
            
        Returns:
            True if session invalidated successfully
        """
        try:
            result = self.supabase.table('user_sessions').update({
                'is_active': False,
                'logged_out_at': datetime.utcnow().isoformat(),
                'logout_reason': logout_reason
            }).eq('session_id', session_id).eq('user_id', user_id).execute()
            
            if result.data:
                logger.info(
                    "session_invalidated",
                    session_id=session_id,
                    user_id=user_id,
                    logout_reason=logout_reason
                )
                return True
            else:
                logger.error(
                    "session_invalidation_failed",
                    session_id=session_id,
                    user_id=user_id,
                    error=result.error
                )
                return False
                
        except Exception as e:
            logger.error(
                "session_invalidation_error",
                session_id=session_id,
                user_id=user_id,
                error=str(e)
            )
            return False
    
    async def invalidate_all_user_sessions(
        self, 
        user_id: str, 
        logout_reason: str = "user_initiated_all_devices"
    ) -> int:
        """
        Invalidate all sessions for a user
        
        Args:
            user_id: User UUID
            logout_reason: Reason for logout
            
        Returns:
            Number of sessions invalidated
        """
        try:
            result = self.supabase.table('user_sessions').update({
                'is_active': False,
                'logged_out_at': datetime.utcnow().isoformat(),
                'logout_reason': logout_reason
            }).eq('user_id', user_id).eq('is_active', True).execute()
            
            if result.data is not None:
                count = len(result.data)
                logger.info(
                    "all_user_sessions_invalidated",
                    user_id=user_id,
                    count=count,
                    logout_reason=logout_reason
                )
                return count
            else:
                logger.error(
                    "all_sessions_invalidation_failed",
                    user_id=user_id,
                    error=result.error
                )
                return 0
                
        except Exception as e:
            logger.error(
                "all_sessions_invalidation_error",
                user_id=user_id,
                error=str(e)
            )
            return 0
    
    async def force_logout_user(
        self, 
        target_user_id: str, 
        admin_user_id: str,
        reason: str = "admin_force_logout"
    ) -> bool:
        """
        Force logout a user (admin function)
        
        Args:
            target_user_id: User UUID to logout
            admin_user_id: Admin user UUID performing the action
            reason: Reason for force logout
            
        Returns:
            True if user was force logged out successfully
        """
        try:
            result = self.supabase.table('user_sessions').update({
                'is_active': False,
                'logged_out_at': datetime.utcnow().isoformat(),
                'logout_reason': reason,
                'logged_out_by': admin_user_id,
                'force_logout': True
            }).eq('user_id', target_user_id).eq('is_active', True).execute()
            
            if result.data is not None:
                count = len(result.data)
                logger.info(
                    "user_force_logged_out",
                    target_user_id=target_user_id,
                    admin_user_id=admin_user_id,
                    reason=reason,
                    sessions_terminated=count
                )
                return True
            else:
                logger.error(
                    "force_logout_failed",
                    target_user_id=target_user_id,
                    admin_user_id=admin_user_id,
                    error=result.error
                )
                return False
                
        except Exception as e:
            logger.error(
                "force_logout_error",
                target_user_id=target_user_id,
                admin_user_id=admin_user_id,
                error=str(e)
            )
            return False
    
    async def get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all active sessions for a user
        
        Args:
            user_id: User UUID
            
        Returns:
            List of active sessions
        """
        try:
            result = self.supabase.table('user_sessions').select(
                'id', 'session_id', 'device_info', 'ip_address', 
                'user_agent', 'created_at', 'last_accessed', 
                'expires_at', 'is_active', 'logout_reason'
            ).eq('user_id', user_id).eq('is_active', True).order(
                'last_accessed', desc=True
            ).execute()
            
            sessions = result.data or []
            
            logger.info(
                "user_sessions_retrieved",
                user_id=user_id,
                count=len(sessions)
            )
            
            return sessions
            
        except Exception as e:
            logger.error(
                "get_user_sessions_error",
                user_id=user_id,
                error=str(e)
            )
            return []
    
    async def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions (background task)
        
        Returns:
            Number of sessions cleaned up
        """
        try:
            # Call the database function to clean up expired sessions
            result = self.supabase.rpc('cleanup_expired_sessions').execute()
            
            if result.data is not None:
                logger.info(
                    "expired_sessions_cleaned",
                    cleaned_sessions=result.data
                )
                return result.data
            else:
                logger.error(
                    "session_cleanup_failed",
                    error=result.error
                )
                return 0
                
        except Exception as e:
            logger.error(
                "session_cleanup_error",
                error=str(e)
            )
            return 0
    
    async def _mark_session_expired(self, session_id: str) -> bool:
        """Mark a session as expired"""
        try:
            result = self.supabase.table('user_sessions').update({
                'is_active': False,
                'logged_out_at': datetime.utcnow().isoformat(),
                'logout_reason': 'session_expired'
            }).eq('session_id', session_id).execute()
            
            return result.data is not None
            
        except Exception as e:
            logger.error(
                "mark_session_expired_error",
                session_id=session_id,
                error=str(e)
            )
            return False
    
    async def _update_last_accessed(self, session_id: str) -> bool:
        """Update the last accessed time for a session"""
        try:
            result = self.supabase.table('user_sessions').update({
                'last_accessed': datetime.utcnow().isoformat()
            }).eq('session_id', session_id).execute()
            
            return result.data is not None
            
        except Exception as e:
            logger.error(
                "update_last_accessed_error",
                session_id=session_id,
                error=str(e)
            )
            return False


# Global session service instance
def get_session_service() -> SessionService:
    """Get session service instance"""
    supabase = get_supabase_client()
    return SessionService(supabase)
