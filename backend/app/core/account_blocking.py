# Account Blocking Service for VitaChain
# Handles temporary account blocking with audit trail and automatic expiration

import structlog
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from supabase import Client
from app.core.notification_service import NotificationService
from app.core.account_blocking_exceptions import (
    AccountBlockingError, UserNotFoundError, UserAlreadyBlockedError,
    InvalidBlockDurationError, InvalidBlockReasonError, DatabaseError,
    NotificationError
)
from app.core.account_blocking_config import account_blocking_config
from app.core.permissions import require_account_blocking
import asyncio
from functools import wraps

logger = structlog.get_logger("account_blocking")

class AccountBlockingService:
    """Service for managing temporary account blocks with audit trail"""
    
    def __init__(self, supabase: Client, notification_service: NotificationService):
        self.supabase = supabase
        self.notification_service = notification_service
        self.config = account_blocking_config
        self._block_status_cache = {}  # Simple in-memory cache
    
    def _handle_database_errors(func):
        """Decorator to handle database errors consistently"""
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            try:
                return await func(self, *args, **kwargs)
            except Exception as e:
                error_msg = str(e).lower()
                if "duplicate key" in error_msg or "unique constraint" in error_msg:
                    raise UserAlreadyBlockedError(args[0] if args else "unknown")
                elif "no rows" in error_msg or "not found" in error_msg:
                    raise UserNotFoundError(args[0] if args else "unknown")
                else:
                    raise DatabaseError(func.__name__, str(e))
        return wrapper
    
    def _validate_block_inputs(self, user_id: str, blocked_by: str, block_reason: str, duration_hours: int):
        """Validate inputs for blocking operation"""
        if not user_id or not user_id.strip():
            raise AccountBlockingError("User ID cannot be empty", "INVALID_USER_ID")
        
        if not blocked_by or not blocked_by.strip():
            raise AccountBlockingError("Blocked by ID cannot be empty", "INVALID_BLOCKED_BY")
        
        # Validate block reason
        is_valid, error_msg = self.config.validate_block_reason(block_reason)
        if not is_valid:
            raise InvalidBlockReasonError(error_msg)
        
        # Validate duration
        if not self.config.validate_block_duration(duration_hours):
            raise InvalidBlockDurationError(duration_hours, self.config.MAX_BLOCK_DURATION)
    
    def _get_cache_key(self, user_id: str) -> str:
        """Generate cache key for user block status"""
        return f"block_status:{user_id}"
    
    def _get_cached_status(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get cached block status for user"""
        if not self.config.ENABLE_BLOCK_STATUS_CACHE:
            return None
        
        cache_key = self._get_cache_key(user_id)
        if cache_key in self._block_status_cache:
            cached_data, timestamp = self._block_status_cache[cache_key]
            # Check if cache is still valid
            if datetime.utcnow().timestamp() - timestamp < self.config.BLOCK_STATUS_CACHE_TTL:
                return cached_data
            else:
                # Remove expired cache entry
                del self._block_status_cache[cache_key]
        return None
    
    def _set_cached_status(self, user_id: str, status_data: Dict[str, Any]):
        """Set cached block status for user"""
        if not self.config.ENABLE_BLOCK_STATUS_CACHE:
            return
        
        cache_key = self._get_cache_key(user_id)
        self._block_status_cache[cache_key] = (status_data, datetime.utcnow().timestamp())
    
    def _invalidate_cache(self, user_id: str):
        """Invalidate cached status for user"""
        if not self.config.ENABLE_BLOCK_STATUS_CACHE:
            return
        
        cache_key = self._get_cache_key(user_id)
        if cache_key in self._block_status_cache:
            del self._block_status_cache[cache_key]
    
    async def check_multiple_block_status(self, user_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """Check block status for multiple users efficiently"""
        results = {}
        
        # Check cache first
        uncached_users = []
        for user_id in user_ids:
            cached_status = self._get_cached_status(user_id)
            if cached_status:
                results[user_id] = cached_status
            else:
                uncached_users.append(user_id)
        
        # Fetch uncached users from database
        if uncached_users:
            try:
                # Batch query for multiple users
                batch_result = self.supabase.table("profiles").select(
                    "id, account_status, blocked_until, block_reason, auto_block"
                ).in_("id", uncached_users).execute()
                
                # Process results and cache them
                for user_data in batch_result.data:
                    user_id = user_data["id"]
                    status_data = self._process_user_status_data(user_data)
                    results[user_id] = status_data
                    self._set_cached_status(user_id, status_data)
                
                # Handle users not found
                for user_id in uncached_users:
                    if user_id not in results:
                        results[user_id] = {"is_blocked": False}
                        self._set_cached_status(user_id, {"is_blocked": False})
                        
            except Exception as e:
                logger.error(
                    "batch_block_status_check_failed",
                    user_ids=uncached_users,
                    error=str(e)
                )
                # Fall back to individual checks for failed batch
                for user_id in uncached_users:
                    try:
                        results[user_id] = await self.check_user_block_status(user_id)
                    except Exception as individual_error:
                        logger.error(
                            "individual_block_status_check_failed",
                            user_id=user_id,
                            error=str(individual_error)
                        )
                        results[user_id] = {"is_blocked": False}
        
        return results
    
    def _process_user_status_data(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process user status data from database"""
        account_status = user_data.get("account_status", "active")
        blocked_until = user_data.get("blocked_until")
        block_reason = user_data.get("block_reason")
        auto_block = user_data.get("auto_block", False)
        
        if account_status == "blocked" and blocked_until:
            try:
                blocked_until_dt = datetime.fromisoformat(blocked_until.replace('Z', '+00:00'))
                if blocked_until_dt > datetime.utcnow():
                    return {
                        "is_blocked": True,
                        "blocked_until": blocked_until,
                        "block_reason": block_reason,
                        "auto_block": auto_block
                    }
            except ValueError:
                logger.warning(
                    "invalid_blocked_until_format",
                    user_id=user_data.get("id"),
                    blocked_until=blocked_until
                )
        
        return {"is_blocked": False}
    
    @_handle_database_errors
    async def block_user(
        self,
        user_id: str,
        blocked_by: str,
        block_reason: str,
        duration_hours: int,
        auto_block: bool = False,
        security_event_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Block a user account temporarily
        
        Args:
            user_id: ID of user to block
            blocked_by: ID of admin performing the block
            block_reason: Reason for blocking
            duration_hours: Duration of block in hours
            auto_block: Whether this is an automatic security block
            security_event_id: Related security event ID (for automatic blocks)
            metadata: Additional metadata
            
        Returns:
            Dict with block details
            
        Raises:
            AccountBlockingError: If validation fails or operation fails
        """
        # Validate inputs
        self._validate_block_inputs(user_id, blocked_by, block_reason, duration_hours)
        
        # Check if user is already blocked
        user_result = self.supabase.table("profiles").select(
            "account_status, blocked_until"
        ).eq("id", user_id).execute()
        
        if not user_result.data:
            raise UserNotFoundError(user_id)
        
        user_data = user_result.data[0]
        if user_data.get("account_status") == "blocked" and user_data.get("blocked_until"):
            current_blocked_until = datetime.fromisoformat(user_data["blocked_until"].replace('Z', '+00:00'))
            if current_blocked_until > datetime.utcnow():
                raise UserAlreadyBlockedError(user_id, current_blocked_until.isoformat())
        
        # Use configured default duration if not specified
        if duration_hours is None:
            duration_hours = self.config.get_default_duration(auto_block)
        
        # Calculate block expiration
        blocked_at = datetime.utcnow()
        blocked_until = blocked_at + timedelta(hours=duration_hours)
        
        # Create block record
        block_data = {
            "user_id": user_id,
            "blocked_by": blocked_by,
            "block_reason": block_reason,
            "block_duration_hours": duration_hours,
            "blocked_at": blocked_at.isoformat(),
            "blocked_until": blocked_until.isoformat(),
            "is_active": True,
            "auto_block": auto_block,
            "security_event_id": security_event_id,
            "metadata": metadata or {}
        }
        
        block_result = self.supabase.table("account_blocks").insert(block_data).execute()
        
        if not block_result.data:
            raise DatabaseError("block_user", "Failed to create block record")
        
        block_id = block_result.data[0]["id"]
        
        # Invalidate cache for this user
        self._invalidate_cache(user_id)
        
        # Send notification to blocked user
        if self.config.ENABLE_BLOCK_NOTIFICATIONS:
            try:
                await self._send_block_notification(user_id, block_reason, blocked_until, auto_block)
            except Exception as e:
                logger.warning(
                    "block_notification_failed",
                    user_id=user_id,
                    error=str(e)
                )
                # Don't fail the block operation if notification fails
        
        # Log the block action
        logger.info(
            "user_blocked",
            user_id=user_id,
            blocked_by=blocked_by,
            block_reason=block_reason,
            duration_hours=duration_hours,
            auto_block=auto_block,
            block_id=block_id
        )
        
        return {
            "block_id": block_id,
            "user_id": user_id,
            "blocked_until": blocked_until.isoformat(),
            "block_reason": block_reason,
            "auto_block": auto_block
        }
    
    async def unblock_user(
        self,
        user_id: str,
        unblocked_by: str,
        unblock_reason: str
    ) -> Dict[str, Any]:
        """
        Unblock a user account
        
        Args:
            user_id: ID of user to unblock
            unblocked_by: ID of admin performing the unblock
            unblock_reason: Reason for unblocking
            
        Returns:
            Dict with unblock details
            
        Raises:
            Exception: If user is not blocked or operation fails
        """
        try:
            # Check if user is currently blocked
            user_result = self.supabase.table("profiles").select(
                "account_status, blocked_until"
            ).eq("id", user_id).execute()
            
            if not user_result.data:
                raise Exception(f"User {user_id} not found")
            
            user_data = user_result.data[0]
            if user_data.get("account_status") != "blocked":
                raise Exception(f"User {user_id} is not currently blocked")
            
            # Find active block record
            block_result = self.supabase.table("account_blocks").select(
                "id, blocked_at, block_reason"
            ).eq("user_id", user_id).eq("is_active", True).execute()
            
            if not block_result.data:
                raise Exception(f"No active block found for user {user_id}")
            
            block_record = block_result.data[0]
            
            # Update block record
            update_data = {
                "is_active": False,
                "unblocked_at": datetime.utcnow().isoformat(),
                "unblocked_by": unblocked_by,
                "unblock_reason": unblock_reason
            }
            
            unblock_result = self.supabase.table("account_blocks").update(update_data).eq(
                "id", block_record["id"]
            ).execute()
            
            if not unblock_result.data:
                raise Exception("Failed to update block record")
            
            # Send notification to unblocked user
            await self._send_unblock_notification(user_id, unblock_reason)
            
            # Log the unblock action
            logger.info(
                "user_unblocked",
                user_id=user_id,
                unblocked_by=unblocked_by,
                unblock_reason=unblock_reason,
                block_id=block_record["id"]
            )
            
            return {
                "user_id": user_id,
                "unblocked_at": datetime.utcnow().isoformat(),
                "unblock_reason": unblock_reason,
                "previous_block_id": block_record["id"]
            }
            
        except Exception as e:
            logger.error(
                "unblock_user_failed",
                user_id=user_id,
                error=str(e),
                unblocked_by=unblocked_by
            )
            raise Exception(f"Failed to unblock user: {str(e)}")
    
    async def extend_block(
        self,
        user_id: str,
        extended_by: str,
        additional_hours: int,
        extension_reason: str
    ) -> Dict[str, Any]:
        """
        Extend an existing block duration
        
        Args:
            user_id: ID of user whose block to extend
            extended_by: ID of admin performing the extension
            additional_hours: Additional hours to add to block
            extension_reason: Reason for extension
            
        Returns:
            Dict with extension details
        """
        try:
            # Find active block record
            block_result = self.supabase.table("account_blocks").select(
                "id, blocked_until, block_duration_hours, block_reason"
            ).eq("user_id", user_id).eq("is_active", True).execute()
            
            if not block_result.data:
                raise Exception(f"No active block found for user {user_id}")
            
            block_record = block_result.data[0]
            current_blocked_until = datetime.fromisoformat(
                block_record["blocked_until"].replace('Z', '+00:00')
            )
            
            # Calculate new block duration
            new_blocked_until = current_blocked_until + timedelta(hours=additional_hours)
            original_duration = block_record["block_duration_hours"]
            new_duration = original_duration + additional_hours
            
            # Update block record
            update_data = {
                "blocked_until": new_blocked_until.isoformat(),
                "block_duration_hours": new_duration,
                "metadata": {
                    **block_record.get("metadata", {}),
                    "extension": {
                        "extended_by": extended_by,
                        "additional_hours": additional_hours,
                        "extension_reason": extension_reason,
                        "extended_at": datetime.utcnow().isoformat()
                    }
                }
            }
            
            extend_result = self.supabase.table("account_blocks").update(update_data).eq(
                "id", block_record["id"]
            ).execute()
            
            if not extend_result.data:
                raise Exception("Failed to extend block")
            
            # Log the extension
            logger.info(
                "block_extended",
                user_id=user_id,
                extended_by=extended_by,
                additional_hours=additional_hours,
                new_duration_hours=new_duration,
                block_id=block_record["id"]
            )
            
            return {
                "block_id": block_record["id"],
                "user_id": user_id,
                "new_blocked_until": new_blocked_until.isoformat(),
                "additional_hours": additional_hours,
                "total_duration_hours": new_duration
            }
            
        except Exception as e:
            logger.error(
                "extend_block_failed",
                user_id=user_id,
                error=str(e),
                extended_by=extended_by
            )
            raise Exception(f"Failed to extend block: {str(e)}")
    
    async def get_blocked_users(
        self,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get list of currently blocked users
        
        Args:
            limit: Maximum number of users to return
            offset: Number of users to skip
            
        Returns:
            Dict with blocked users list and pagination info
        """
        try:
            # Get active blocks with user details
            result = self.supabase.table("account_blocks").select(
                """
                id, user_id, block_reason, block_duration_hours,
                blocked_at, blocked_until, auto_block,
                profiles!inner(id, full_name, email, role)
                """
            ).eq("is_active", True).order("blocked_at", desc=True).range(
                offset, offset + limit - 1
            ).execute()
            
            blocks = result.data or []
            
            # Calculate time remaining for each block
            for block in blocks:
                blocked_until = datetime.fromisoformat(
                    block["blocked_until"].replace('Z', '+00:00')
                )
                time_remaining = blocked_until - datetime.utcnow()
                block["time_remaining_hours"] = max(0, time_remaining.total_seconds() / 3600)
                block["time_remaining_minutes"] = max(0, time_remaining.total_seconds() / 60)
            
            return {
                "blocks": blocks,
                "total": len(blocks),
                "limit": limit,
                "offset": offset
            }
            
        except Exception as e:
            logger.error("get_blocked_users_failed", error=str(e))
            raise Exception(f"Failed to get blocked users: {str(e)}")
    
    async def cleanup_expired_blocks(self) -> int:
        """
        Clean up expired blocks and unblock users
        
        Returns:
            Number of blocks that were cleaned up
        """
        try:
            # Call the database cleanup function
            result = self.supabase.rpc("cleanup_expired_blocks").execute()
            
            cleanup_count = result.data if result.data else 0
            
            if cleanup_count > 0:
                logger.info(
                    "expired_blocks_cleaned",
                    count=cleanup_count,
                    timestamp=datetime.utcnow().isoformat()
                )
            
            return cleanup_count
            
        except Exception as e:
            logger.error("cleanup_expired_blocks_failed", error=str(e))
            raise Exception(f"Failed to cleanup expired blocks: {str(e)}")
    
    async def check_user_block_status(self, user_id: str) -> Dict[str, Any]:
        """
        Check if a user is currently blocked
        
        Args:
            user_id: ID of user to check
            
        Returns:
            Dict with block status information
        """
        try:
            result = self.supabase.table("profiles").select(
                "account_status, block_reason, blocked_at, blocked_until, auto_block"
            ).eq("id", user_id).execute()
            
            if not result.data:
                return {"is_blocked": False, "reason": "User not found"}
            
            user_data = result.data[0]
            
            if user_data.get("account_status") != "blocked":
                return {"is_blocked": False}
            
            # Check if block has expired
            if user_data.get("blocked_until"):
                blocked_until = datetime.fromisoformat(
                    user_data["blocked_until"].replace('Z', '+00:00')
                )
                if blocked_until <= datetime.utcnow():
                    return {"is_blocked": False, "reason": "Block expired"}
            
            return {
                "is_blocked": True,
                "block_reason": user_data.get("block_reason"),
                "blocked_at": user_data.get("blocked_at"),
                "blocked_until": user_data.get("blocked_until"),
                "auto_block": user_data.get("auto_block", False)
            }
            
        except Exception as e:
            logger.error(
                "check_user_block_status_failed",
                user_id=user_id,
                error=str(e)
            )
            return {"is_blocked": False, "reason": "Check failed"}
    
    async def _send_block_notification(
        self, user_id: str, block_reason: str, blocked_until: datetime, auto_block: bool
    ) -> None:
        """Send block notification email to user"""
        try:
            # Get user details
            user_result = self.supabase.table("profiles").select(
                "full_name, email"
            ).eq("id", user_id).execute()
            
            if not user_result.data:
                return
            
            user = user_result.data[0]
            
            # Prepare email content
            subject = "Your VitaChain Account Has Been Blocked"
            
            if auto_block:
                message = f"""
                Dear {user.get('full_name', 'User')},
                
                Your VitaChain account has been automatically blocked due to security concerns.
                
                Block Reason: {block_reason}
                Block Duration: Until {blocked_until.strftime('%Y-%m-%d %H:%M UTC')}
                
                This is an automatic security measure. If you believe this is an error, 
                please contact our support team.
                
                Best regards,
                VitaChain Security Team
                """
            else:
                message = f"""
                Dear {user.get('full_name', 'User')},
                
                Your VitaChain account has been temporarily blocked by our administration team.
                
                Block Reason: {block_reason}
                Block Duration: Until {blocked_until.strftime('%Y-%m-%d %H:%M UTC')}
                
                If you have questions about this block, please contact our support team.
                
                Best regards,
                VitaChain Administration Team
                """
            
            await self.notification_service.send_email(
                to_email=user.get("email"),
                subject=subject,
                message=message
            )
            
        except Exception as e:
            logger.error(
                "send_block_notification_failed",
                user_id=user_id,
                error=str(e)
            )
    
    async def _send_unblock_notification(
        self, user_id: str, unblock_reason: str
    ) -> None:
        """Send unblock notification email to user"""
        try:
            # Get user details
            user_result = self.supabase.table("profiles").select(
                "full_name, email"
            ).eq("id", user_id).execute()
            
            if not user_result.data:
                return
            
            user = user_result.data[0]
            
            # Prepare email content
            subject = "Your VitaChain Account Has Been Restored"
            message = f"""
            Dear {user.get('full_name', 'User')},
            
            Your VitaChain account has been restored and you can now access the platform.
            
            Unblock Reason: {unblock_reason}
            Restoration Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}
            
            Thank you for your patience.
            
            Best regards,
            VitaChain Administration Team
            """
            
            await self.notification_service.send_email(
                to_email=user.get("email"),
                subject=subject,
                message=message
            )
            
        except Exception as e:
            logger.error(
                "send_unblock_notification_failed",
                user_id=user_id,
                error=str(e)
            )
