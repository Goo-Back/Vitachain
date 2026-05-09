# API Key Rotation Service for VitaChain
# Background service for automatic API key rotation

import asyncio
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import structlog

from ..core.security import APIKeyManager

logger = structlog.get_logger("api_key_rotation")

class APIKeyRotationService:
    """Background service for automatic API key rotation"""
    
    def __init__(self, supabase_client, rotation_enabled: bool = True):
        self.supabase = supabase_client
        self.rotation_enabled = rotation_enabled
        self.api_key_manager = APIKeyManager()
        self.rotation_task = None
        self.is_running = False
        
    async def start_rotation_scheduler(self):
        """Start background task for API key rotation"""
        if not self.rotation_enabled:
            logger.info("api_key_rotation_disabled")
            return
        
        if self.is_running:
            logger.warning("api_key_rotation_already_running")
            return
        
        self.is_running = True
        self.rotation_task = asyncio.create_task(self._rotation_loop())
        logger.info("api_key_rotation_scheduler_started")
    
    async def stop_rotation_scheduler(self):
        """Stop background rotation task"""
        self.is_running = False
        if self.rotation_task:
            self.rotation_task.cancel()
            try:
                await self.rotation_task
            except asyncio.CancelledError:
                pass
            self.rotation_task = None
        logger.info("api_key_rotation_scheduler_stopped")
    
    async def _rotation_loop(self):
        """Background task to check and rotate expired keys"""
        while self.is_running:
            try:
                await self._rotate_expired_keys()
                await asyncio.sleep(3600)  # Check every hour
            except asyncio.CancelledError:
                logger.info("api_key_rotation_cancelled")
                break
            except Exception as e:
                logger.error("api_key_rotation_error", 
                           error=str(e),
                           severity="high")
                # Wait before retrying on error
                await asyncio.sleep(300)  # 5 minutes
    
    async def _rotate_expired_keys(self):
        """Rotate API keys that are due for rotation"""
        try:
            expiry_date = datetime.utcnow() - timedelta(days=90)
            
            # Get expired keys
            result = self.supabase.table("iot_api_keys")\
                .select("*")\
                .lt("created_at", expiry_date.isoformat())\
                .eq("active", True)\
                .execute()
            
            expired_keys = result.data
            rotated_count = 0
            
            if expired_keys:
                logger.info("found_expired_keys", 
                           count=len(expired_keys))
                
                for key_record in expired_keys:
                    try:
                        await self._rotate_single_key(key_record)
                        rotated_count += 1
                    except Exception as e:
                        logger.error("single_key_rotation_failed",
                                   device_id=key_record.get("device_id"),
                                   error=str(e),
                                   severity="medium")
                
                logger.info("api_key_rotation_completed",
                           rotated_keys=rotated_count,
                           total_expired=len(expired_keys))
            
            return rotated_count
            
        except Exception as e:
            logger.error("rotate_expired_keys_error",
                        error=str(e),
                        severity="high")
            raise
    
    async def _rotate_single_key(self, key_record: dict):
        """Rotate a single API key"""
        device_id = key_record["device_id"]
        old_key_id = key_record["id"]
        
        try:
            # Generate new key
            new_key = self.api_key_manager.generate_api_key()
            new_hash = self.api_key_manager.hash_api_key(new_key)
            
            # Start database transaction
            # Deactivate old key first
            deactivate_result = self.supabase.table("iot_api_keys")\
                .update({"active": False, "deactivated_at": datetime.utcnow().isoformat()})\
                .eq("id", old_key_id)\
                .execute()
            
            if not deactivate_result.data:
                raise Exception(f"Failed to deactivate old key {old_key_id}")
            
            # Create new key
            new_key_data = {
                "device_id": device_id,
                "key_hash": new_hash,
                "created_at": datetime.utcnow().isoformat(),
                "active": True,
                "rotation_reason": "scheduled_rotation"
            }
            
            insert_result = self.supabase.table("iot_api_keys")\
                .insert(new_key_data)\
                .execute()
            
            if not insert_result.data:
                # Rollback: reactivate old key
                self.supabase.table("iot_api_keys")\
                    .update({"active": True, "deactivated_at": None})\
                    .eq("id", old_key_id)\
                    .execute()
                raise Exception("Failed to create new key")
            
            new_key_id = insert_result.data[0]["id"]
            
            # Log successful rotation
            logger.info("api_key_rotated_successfully",
                       device_id=device_id,
                       old_key_id=old_key_id,
                       new_key_id=new_key_id,
                       severity="info")
            
            # Notify device about key change
            await self._notify_device_key_change(device_id, new_key, new_key_id)
            
            # Create audit log entry
            await self._create_audit_log(
                device_id=device_id,
                action="api_key_rotation",
                old_key_id=old_key_id,
                new_key_id=new_key_id,
                reason="scheduled_rotation"
            )
            
        except Exception as e:
            logger.error("single_key_rotation_error",
                        device_id=device_id,
                        old_key_id=key_record.get("id"),
                        error=str(e),
                        severity="high")
            raise
    
    async def _notify_device_key_change(self, device_id: str, new_key: str, new_key_id: str):
        """Notify device about key change"""
        try:
            # In production, this would send the new key to the IoT device
            # via secure channel (MQTT, LoRaWAN, cellular, etc.)
            
            # For now, we'll create a notification record
            notification_data = {
                "device_id": device_id,
                "notification_type": "api_key_rotation",
                "new_key_id": new_key_id,
                "sent_at": datetime.utcnow().isoformat(),
                "status": "pending",
                "delivery_method": "placeholder"
            }
            
            result = self.supabase.table("device_notifications")\
                .insert(notification_data)\
                .execute()
            
            if result.data:
                notification_id = result.data[0]["id"]
                logger.info("device_notification_created",
                           device_id=device_id,
                           notification_id=notification_id,
                           severity="info")
            
            # Simulate device notification (placeholder)
            # In production, implement actual device communication
            await asyncio.sleep(1)  # Simulate network delay
            
            # Update notification status
            self.supabase.table("device_notifications")\
                .update({"status": "sent", "delivered_at": datetime.utcnow().isoformat()})\
                .eq("id", notification_id)\
                .execute()
            
            logger.info("device_key_change_notification_sent",
                       device_id=device_id,
                       new_key_id=new_key_id,
                       severity="info")
            
        except Exception as e:
            logger.error("device_notification_failed",
                        device_id=device_id,
                        error=str(e),
                        severity="medium")
            # Don't raise here - notification failure shouldn't break rotation
    
    async def _create_audit_log(self, device_id: str, action: str, 
                               old_key_id: str = None, new_key_id: str = None,
                               reason: str = None):
        """Create audit log entry for key rotation"""
        try:
            audit_data = {
                "device_id": device_id,
                "action": action,
                "old_key_id": old_key_id,
                "new_key_id": new_key_id,
                "reason": reason,
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": "system",  # System-initiated rotation
                "ip_address": "system"
            }
            
            result = self.supabase.table("security_audit_log")\
                .insert(audit_data)\
                .execute()
            
            if result.data:
                logger.info("audit_log_created",
                           device_id=device_id,
                           action=action,
                           audit_id=result.data[0]["id"],
                           severity="info")
            
        except Exception as e:
            logger.error("audit_log_creation_failed",
                        device_id=device_id,
                        action=action,
                        error=str(e),
                        severity="medium")
    
    async def force_rotate_key(self, device_id: str, reason: str = "manual_rotation"):
        """Manually force rotation of a device's API key"""
        try:
            # Get current active key for device
            result = self.supabase.table("iot_api_keys")\
                .select("*")\
                .eq("device_id", device_id)\
                .eq("active", True)\
                .execute()
            
            if not result.data:
                raise Exception(f"No active key found for device {device_id}")
            
            current_key = result.data[0]
            
            # Rotate the key
            await self._rotate_single_key(current_key)
            
            logger.info("manual_key_rotation_completed",
                       device_id=device_id,
                       reason=reason,
                       severity="info")
            
            return True
            
        except Exception as e:
            logger.error("manual_key_rotation_failed",
                        device_id=device_id,
                        reason=reason,
                        error=str(e),
                        severity="high")
            raise
    
    async def get_rotation_status(self) -> Dict[str, Any]:
        """Get current rotation service status"""
        try:
            # Count keys that will need rotation in next 30 days
            future_expiry = datetime.utcnow() + timedelta(days=30)
            
            result = self.supabase.table("iot_api_keys")\
                .select("*")\
                .lt("created_at", future_expiry.isoformat())\
                .eq("active", True)\
                .execute()
            
            upcoming_rotations = len(result.data)
            
            # Count currently expired keys
            expiry_date = datetime.utcnow() - timedelta(days=90)
            
            result = self.supabase.table("iot_api_keys")\
                .select("*")\
                .lt("created_at", expiry_date.isoformat())\
                .eq("active", True)\
                .execute()
            
            expired_keys = len(result.data)
            
            return {
                "service_running": self.is_running,
                "rotation_enabled": self.rotation_enabled,
                "upcoming_rotations_30d": upcoming_rotations,
                "expired_keys_pending": expired_keys,
                "last_rotation_check": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("rotation_status_check_failed",
                        error=str(e),
                        severity="medium")
            return {
                "service_running": self.is_running,
                "rotation_enabled": self.rotation_enabled,
                "error": str(e)
            }
    
    async def get_device_key_history(self, device_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get history of API keys for a device"""
        try:
            result = self.supabase.table("iot_api_keys")\
                .select("*")\
                .eq("device_id", device_id)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            
            return result.data
            
        except Exception as e:
            logger.error("device_key_history_failed",
                        device_id=device_id,
                        error=str(e),
                        severity="medium")
            return []
