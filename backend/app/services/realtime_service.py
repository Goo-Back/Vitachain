"""
Real-time service for broadcasting alert status changes
Handles Supabase Realtime subscriptions and broadcasts
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

from app.core.logging import get_logger
from app.core.database import get_supabase_client

logger = get_logger(__name__)


class RealtimeService:
    """Service for handling real-time broadcasts via Supabase Realtime"""
    
    def __init__(self, supabase_client):
        """Initialize realtime service with Supabase client."""
        self.supabase = supabase_client
        self.logger = get_logger(f"{__name__}.RealtimeService")
    
    async def broadcast_alert_status_change(
        self, 
        alert_id: uuid.UUID, 
        farmer_id: uuid.UUID, 
        read_status: bool,
        read_at: Optional[datetime] = None
    ) -> bool:
        """
        Broadcast alert status change to farmer's connected clients.
        
        Args:
            alert_id: Alert UUID that was updated
            farmer_id: Farmer UUID who owns the alert
            read_status: New read status
            read_at: Timestamp when alert was marked as read (if applicable)
            
        Returns:
            True if broadcast successful, False otherwise
        """
        try:
            # Create broadcast payload
            payload = {
                "type": "alert_status_change",
                "alert_id": str(alert_id),
                "farmer_id": str(farmer_id),
                "read_status": read_status,
                "read_at": read_at.isoformat() if read_at else None,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Use Supabase Realtime to broadcast
            # Note: Supabase handles the broadcast automatically when we update the database
            # This method is for logging and potential custom broadcast logic
            
            self.logger.info(
                "alert_status_broadcast",
                alert_id=str(alert_id),
                farmer_id=str(farmer_id),
                read_status=read_status,
                broadcast_type="database_trigger"
            )
            
            return True
            
        except Exception as e:
            self.logger.error(
                "broadcast_alert_status_change_error",
                alert_id=str(alert_id),
                farmer_id=str(farmer_id),
                error=str(e)
            )
            return False
    
    async def broadcast_bulk_alert_status_change(
        self, 
        updated_alerts: list[Dict[str, Any]], 
        farmer_id: uuid.UUID
    ) -> bool:
        """
        Broadcast bulk alert status changes to farmer's connected clients.
        
        Args:
            updated_alerts: List of updated alert records
            farmer_id: Farmer UUID who owns the alerts
            
        Returns:
            True if broadcast successful, False otherwise
        """
        try:
            # Create broadcast payload for bulk updates
            payload = {
                "type": "bulk_alert_status_change",
                "farmer_id": str(farmer_id),
                "updated_count": len(updated_alerts),
                "alerts": [
                    {
                        "alert_id": alert["id"],
                        "read_status": alert["read_status"],
                        "read_at": alert.get("read_at")
                    }
                    for alert in updated_alerts
                ],
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.logger.info(
                "bulk_alert_status_broadcast",
                farmer_id=str(farmer_id),
                updated_count=len(updated_alerts),
                broadcast_type="database_trigger"
            )
            
            return True
            
        except Exception as e:
            self.logger.error(
                "broadcast_bulk_alert_status_change_error",
                farmer_id=str(farmer_id),
                error=str(e)
            )
            return False
    
    async def broadcast_unread_count_change(
        self, 
        farmer_id: uuid.UUID, 
        unread_count: int
    ) -> bool:
        """
        Broadcast unread count change to farmer's connected clients.
        
        Args:
            farmer_id: Farmer UUID
            unread_count: New unread alert count
            
        Returns:
            True if broadcast successful, False otherwise
        """
        try:
            # Create broadcast payload
            payload = {
                "type": "unread_count_change",
                "farmer_id": str(farmer_id),
                "unread_count": unread_count,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.logger.info(
                "unread_count_broadcast",
                farmer_id=str(farmer_id),
                unread_count=unread_count,
                broadcast_type="database_trigger"
            )
            
            return True
            
        except Exception as e:
            self.logger.error(
                "broadcast_unread_count_change_error",
                farmer_id=str(farmer_id),
                error=str(e)
            )
            return False


# Factory function for dependency injection
def get_realtime_service() -> RealtimeService:
    """Create realtime service instance."""
    supabase = get_supabase_client()
    return RealtimeService(supabase)
