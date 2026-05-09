# Notification Service for VitaChain
# Handles security alerts and user notifications

import structlog
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum
import json

logger = structlog.get_logger("notification")

class NotificationType(str, Enum):
    SECURITY_ALERT = "security_alert"
    NEW_DEVICE = "new_device"
    SUSPICIOUS_LOGIN = "suspicious_login"
    ACCOUNT_LOCKED = "account_locked"
    PASSWORD_RESET = "password_reset"

class NotificationChannel(str, Enum):
    EMAIL = "email"
    IN_APP = "in_app"
    SMS = "sms"
    WEBHOOK = "webhook"

class NotificationService:
    """Service for sending security notifications"""
    
    def __init__(self, email_service=None, webhook_url: str = None):
        self.email_service = email_service
        self.webhook_url = webhook_url
        
    async def send_security_alert(self, alert_data: Dict[str, Any], 
                                 channels: List[NotificationChannel] = None) -> bool:
        """
        Send security alert notification
        
        Args:
            alert_data: Security alert data
            channels: List of notification channels to use
            
        Returns:
            True if notification sent successfully
        """
        try:
            # Default to email and in-app if no channels specified
            if not channels:
                channels = [NotificationChannel.EMAIL, NotificationChannel.IN_APP]
            
            success_count = 0
            total_channels = len(channels)
            
            for channel in channels:
                if channel == NotificationChannel.EMAIL:
                    success = await self._send_email_notification(alert_data)
                elif channel == NotificationChannel.IN_APP:
                    success = await self._send_in_app_notification(alert_data)
                elif channel == NotificationChannel.WEBHOOK and self.webhook_url:
                    success = await self._send_webhook_notification(alert_data)
                else:
                    logger.warning("unsupported_notification_channel", channel=channel)
                    continue
                
                if success:
                    success_count += 1
            
            success_rate = success_count / total_channels if total_channels > 0 else 0
            
            logger.info("security_alert_sent", 
                       alert_type=alert_data.get("alert_type"),
                       channels=[channel.value for channel in channels],
                       success_rate=success_rate)
            
            return success_rate > 0.5  # Consider successful if majority sent
            
        except Exception as e:
            logger.error("security_alert_error", 
                       alert_type=alert_data.get("alert_type"),
                       error=str(e))
            return False
    
    async def send_user_notification(self, user_id: str, notification_type: NotificationType,
                                 title: str, message: str, 
                                 metadata: Dict[str, Any] = None,
                                 channels: List[NotificationChannel] = None) -> bool:
        """
        Send notification to user about their account security
        
        Args:
            user_id: User ID to notify
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            metadata: Additional notification data
            channels: List of notification channels to use
            
        Returns:
            True if notification sent successfully
        """
        try:
            # Default to in-app if no channels specified
            if not channels:
                channels = [NotificationChannel.IN_APP]
            
            notification_data = {
                "user_id": user_id,
                "notification_type": notification_type.value,
                "title": title,
                "message": message,
                "metadata": metadata or {},
                "created_at": datetime.utcnow().isoformat()
            }
            
            success_count = 0
            total_channels = len(channels)
            
            for channel in channels:
                if channel == NotificationChannel.IN_APP:
                    success = await self._send_in_app_notification({
                        **notification_data,
                        "channel": "in_app"
                    })
                elif channel == NotificationChannel.EMAIL and self.email_service:
                    success = await self._send_email_notification({
                        **notification_data,
                        "channel": "email"
                    })
                else:
                    logger.warning("unsupported_user_notification_channel", channel=channel)
                    continue
                
                if success:
                    success_count += 1
            
            success_rate = success_count / total_channels if total_channels > 0 else 0
            
            logger.info("user_notification_sent", 
                       user_id=user_id,
                       notification_type=notification_type.value,
                       channels=[channel.value for channel in channels],
                       success_rate=success_rate)
            
            return success_rate > 0.5
            
        except Exception as e:
            logger.error("user_notification_error", 
                       user_id=user_id,
                       notification_type=notification_type.value,
                       error=str(e))
            return False
    
    async def _send_email_notification(self, notification_data: Dict[str, Any]) -> bool:
        """Send email notification"""
        try:
            if not self.email_service:
                logger.warning("email_service_not_configured")
                return False
            
            # Generate email content
            subject = notification_data.get("title", "Security Alert")
            message = notification_data.get("message", "")
            
            # Add security-specific formatting
            if notification_data.get("alert_type"):
                message = self._format_security_email_message(notification_data)
            
            # Send email (placeholder implementation)
            # In production, integrate with actual email service
            logger.info("email_notification_sent", 
                       to=notification_data.get("user_id"),
                       subject=subject)
            
            return True
            
        except Exception as e:
            logger.error("email_notification_error", error=str(e))
            return False
    
    async def _send_in_app_notification(self, notification_data: Dict[str, Any]) -> bool:
        """Send in-app notification"""
        try:
            # Store notification in database for in-app display
            # This would integrate with Supabase notifications table
            logger.info("in_app_notification_stored", 
                       user_id=notification_data.get("user_id"),
                       title=notification_data.get("title"),
                       channel=notification_data.get("channel", "in_app"))
            
            return True
            
        except Exception as e:
            logger.error("in_app_notification_error", error=str(e))
            return False
    
    async def _send_webhook_notification(self, notification_data: Dict[str, Any]) -> bool:
        """Send webhook notification"""
        try:
            if not self.webhook_url:
                logger.warning("webhook_url_not_configured")
                return False
            
            # Prepare webhook payload
            payload = {
                "event": "security_alert",
                "timestamp": datetime.utcnow().isoformat(),
                "data": notification_data
            }
            
            # Send webhook (placeholder implementation)
            # In production, use httpx to send POST request
            logger.info("webhook_notification_sent", 
                       url=self.webhook_url,
                       event_type=notification_data.get("alert_type"))
            
            return True
            
        except Exception as e:
            logger.error("webhook_notification_error", error=str(e))
            return False
    
    def _format_security_email_message(self, alert_data: Dict[str, Any]) -> str:
        """Format security alert email message"""
        alert_type = alert_data.get("alert_type", "unknown")
        user_id = alert_data.get("user_id", "Unknown User")
        
        base_message = f"""
        Security Alert - {alert_data.get('title', 'Suspicious Activity Detected')}
        
        Dear User {user_id},
        
        We detected suspicious activity on your VitaChain account:
        
        """
        
        if alert_type == "new_device":
            device = alert_data.get("metadata", {}).get("device", "Unknown Device")
            base_message += f"""
        • New device login detected from: {device}
        • If this was you, please verify your account security
        • If this was not you, please change your password immediately
        
            """
        
        elif alert_type == "suspicious_login":
            ip = alert_data.get("ip_address", "Unknown IP")
            location = alert_data.get("metadata", {}).get("location", {})
            city = location.get("city", "Unknown Location")
            country = location.get("country_name", "Unknown Country")
            
            base_message += f"""
        • Suspicious login attempt from: {ip}
        • Location: {city}, {country}
        • If this was you, you can safely ignore this alert
        • If this was not you, please secure your account immediately
        
            """
        
        elif alert_type == "account_locked":
            reason = alert_data.get("metadata", {}).get("reason", "Security Policy Violation")
            base_message += f"""
        • Your account has been temporarily locked
        • Reason: {reason}
        • Please contact support if you believe this is an error
        
            """
        
        else:
            anomalies = alert_data.get("metadata", {}).get("anomalies", [])
            for anomaly in anomalies:
                anomaly_type = anomaly.get("type", "unknown")
                base_message += f"• {anomaly_type.replace('_', ' ').title()}: {anomaly}\n"
        
        base_message += f"""
        For your security, we recommend:
        • Enabling two-factor authentication
        • Using a strong, unique password
        • Regularly reviewing your account activity
        
        If you have any questions, please contact our support team.
        
        Best regards,
        VitaChain Security Team
        """
        
        return base_message.strip()
    
    async def get_user_notifications(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get user's security notifications
        
        Args:
            user_id: User ID
            limit: Maximum number of notifications to return
            
        Returns:
            List of user notifications
        """
        try:
            # This would query notifications from database
            # For now, return empty list
            logger.info("user_notifications_retrieved", user_id=user_id, limit=limit)
            return []
            
        except Exception as e:
            logger.error("get_user_notifications_error", 
                       user_id=user_id,
                       error=str(e))
            return []
    
    async def mark_notification_read(self, notification_id: str, user_id: str) -> bool:
        """
        Mark notification as read
        
        Args:
            notification_id: Notification ID
            user_id: User ID
            
        Returns:
            True if marked as read successfully
        """
        try:
            # This would update notification in database
            logger.info("notification_marked_read", 
                       notification_id=notification_id,
                       user_id=user_id)
            return True
            
        except Exception as e:
            logger.error("mark_notification_read_error", 
                       notification_id=notification_id,
                       user_id=user_id,
                       error=str(e))
            return False

# Global notification service instance
notification_service = NotificationService()
