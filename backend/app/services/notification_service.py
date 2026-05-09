"""
Notification Service for KATARA real-time alert notifications
Handles Supabase Realtime subscriptions and notification delivery
"""

import json
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
import asyncio

from app.core.logging import get_logger
from app.core.database import get_supabase_client
from app.models.schemas import Alert, AlertType, AlertSeverity

logger = get_logger(__name__)


class NotificationService:
    """Service for handling real-time notifications via Supabase Realtime."""
    
    def __init__(self, supabase_client):
        """Initialize notification service with Supabase client."""
        self.supabase = supabase_client
        self.logger = get_logger(f"{__name__}.NotificationService")
        self.subscriptions = {}  # Store active subscriptions by farmer_id
    
    async def subscribe_to_farmer_alerts(
        self, 
        farmer_id: str, 
        callback: Callable[[Dict[str, Any]], None]
    ) -> str:
        """
        Subscribe to real-time alerts for a specific farmer.
        
        Args:
            farmer_id: Farmer UUID as string
            callback: Callback function to handle notification events
            
        Returns:
            Subscription ID
        """
        try:
            # Subscribe to alerts table changes for this farmer
            subscription = self.supabase.channel(f"farmer_alerts_{farmer_id}").on_postgres_changes(
                event="INSERT",
                schema="public",
                table="katara_alerts",
                filter=f"farmer_id=eq.{farmer_id}"
            ).subscribe()
            
            # Store subscription and callback
            subscription_id = f"alerts_{farmer_id}"
            self.subscriptions[subscription_id] = {
                "subscription": subscription,
                "callback": callback,
                "farmer_id": farmer_id,
                "created_at": datetime.utcnow()
            }
            
            # Listen for events
            async def event_handler(payload):
                try:
                    await self._handle_alert_event(payload, callback)
                except Exception as e:
                    self.logger.error("alert_event_handler_error", error=str(e), payload=payload)
            
            subscription.listen(event_handler)
            
            self.logger.info("farmer_alert_subscription_created", farmer_id=farmer_id)
            return subscription_id
            
        except Exception as e:
            self.logger.error("subscribe_to_farmer_alerts_error", farmer_id=farmer_id, error=str(e))
            raise
    
    async def unsubscribe_from_farmer_alerts(self, subscription_id: str) -> bool:
        """
        Unsubscribe from farmer alerts.
        
        Args:
            subscription_id: Subscription ID to unsubscribe
            
        Returns:
            True if unsubscribed successfully, False otherwise
        """
        try:
            if subscription_id in self.subscriptions:
                subscription_info = self.subscriptions[subscription_id]
                await subscription_info["subscription"].unsubscribe()
                del self.subscriptions[subscription_id]
                
                self.logger.info("farmer_alert_subscription_removed", subscription_id=subscription_id)
                return True
            else:
                self.logger.warning("subscription_not_found", subscription_id=subscription_id)
                return False
                
        except Exception as e:
            self.logger.error("unsubscribe_from_farmer_alerts_error", subscription_id=subscription_id, error=str(e))
            return False
    
    async def _handle_alert_event(self, payload: Dict[str, Any], callback: Callable):
        """
        Handle incoming alert event from Supabase Realtime.
        
        Args:
            payload: Event payload from Supabase
            callback: Callback function to notify
        """
        try:
            event_type = payload.get("event", "")
            new_record = payload.get("new", {})
            
            if event_type == "INSERT" and new_record:
                # Create alert object from record
                alert = Alert(
                    id=new_record["id"],
                    farmer_id=new_record["farmer_id"],
                    device_id=new_record.get("device_id"),
                    type=AlertType(new_record["type"]),
                    severity=AlertSeverity(new_record["severity"]),
                    message=new_record["message"],
                    is_read=new_record["is_read"],
                    created_at=datetime.fromisoformat(new_record["created_at"].replace('Z', '+00:00'))
                )
                
                # Prepare notification payload
                notification = {
                    "event": "alert_created",
                    "alert": alert.dict(),
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                # Call the callback function
                if asyncio.iscoroutinefunction(callback):
                    await callback(notification)
                else:
                    callback(notification)
                
                self.logger.debug("alert_notification_sent", alert_id=str(alert.id))
            
        except Exception as e:
            self.logger.error("handle_alert_event_error", error=str(e), payload=payload)
            raise
    
    async def send_manual_notification(
        self, 
        farmer_id: str, 
        notification_type: str, 
        data: Dict[str, Any]
    ) -> bool:
        """
        Send a manual notification to a farmer (for testing or special cases).
        
        Args:
            farmer_id: Farmer UUID as string
            notification_type: Type of notification
            data: Notification data
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            notification = {
                "event": notification_type,
                "farmer_id": farmer_id,
                "data": data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Find active subscription for this farmer
            subscription_id = f"alerts_{farmer_id}"
            if subscription_id in self.subscriptions:
                callback = self.subscriptions[subscription_id]["callback"]
                
                if asyncio.iscoroutinefunction(callback):
                    await callback(notification)
                else:
                    callback(notification)
                
                self.logger.info("manual_notification_sent", farmer_id=farmer_id, type=notification_type)
                return True
            else:
                self.logger.warning("no_active_subscription", farmer_id=farmer_id)
                return False
                
        except Exception as e:
            self.logger.error("send_manual_notification_error", farmer_id=farmer_id, error=str(e))
            return False
    
    def get_active_subscriptions(self) -> List[Dict[str, Any]]:
        """
        Get list of active subscriptions.
        
        Returns:
            List of active subscription information
        """
        subscriptions = []
        
        for subscription_id, info in self.subscriptions.items():
            subscriptions.append({
                "subscription_id": subscription_id,
                "farmer_id": info["farmer_id"],
                "created_at": info["created_at"].isoformat(),
                "status": "active"
            })
        
        return subscriptions
    
    async def cleanup_subscriptions(self) -> int:
        """
        Clean up all active subscriptions.
        
        Returns:
            Number of subscriptions cleaned up
        """
        cleanup_count = 0
        
        for subscription_id in list(self.subscriptions.keys()):
            if await self.unsubscribe_from_farmer_alerts(subscription_id):
                cleanup_count += 1
        
        self.logger.info("subscriptions_cleaned_up", count=cleanup_count)
        return cleanup_count
    
    async def test_notification_delivery(self, farmer_id: str) -> Dict[str, Any]:
        """
        Test notification delivery for a farmer.
        
        Args:
            farmer_id: Farmer UUID as string
            
        Returns:
            Test result information
        """
        try:
            test_notification = {
                "event": "test_notification",
                "farmer_id": farmer_id,
                "data": {
                    "message": "This is a test notification",
                    "test_id": str(datetime.utcnow().timestamp())
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Check if subscription exists
            subscription_id = f"alerts_{farmer_id}"
            has_subscription = subscription_id in self.subscriptions
            
            if has_subscription:
                callback = self.subscriptions[subscription_id]["callback"]
                
                if asyncio.iscoroutinefunction(callback):
                    await callback(test_notification)
                else:
                    callback(test_notification)
                
                return {
                    "success": True,
                    "farmer_id": farmer_id,
                    "has_subscription": True,
                    "test_sent_at": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "success": False,
                    "farmer_id": farmer_id,
                    "has_subscription": False,
                    "error": "No active subscription found"
                }
                
        except Exception as e:
            self.logger.error("test_notification_delivery_error", farmer_id=farmer_id, error=str(e))
            return {
                "success": False,
                "farmer_id": farmer_id,
                "error": str(e)
            }


# Factory function for dependency injection
def get_notification_service() -> NotificationService:
    """Create notification service instance."""
    supabase = get_supabase_client()
    return NotificationService(supabase)
