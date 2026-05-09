"""
Alert Service for KATARA critical condition alert system
Handles threshold checking, alert generation, and real-time notifications
"""

import time
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
import os

from app.core.logging import get_logger
from app.core.database import get_supabase_client
from app.services.realtime_service import get_realtime_service
from app.services.threshold_service import get_threshold_service
from app.models.schemas import (
    Alert, AlertCreate, AlertType, AlertSeverity, MetricType,
    ThresholdConfig, ThresholdViolation, AlertGenerationRequest, AlertGenerationResponse,
    AlertNotFoundResponse, AlertForbiddenResponse, AlertValidationErrorResponse
)

logger = get_logger(__name__)

# Alert message templates
ALERT_MESSAGES = {
    "temperature_high": "Critical temperature detected: {value}°C (threshold: {threshold}°C). Immediate action recommended to prevent heat stress.",
    "humidity_low": "Low humidity detected: {value}% (threshold: {threshold}%). Risk of dehydration - consider irrigation.",
    "ndvi_low": "Vegetation stress detected: NDVI {value} (threshold: {threshold}). Review irrigation and nutrient levels."
}

# Threshold configuration from environment variables with defaults
# DEFAULT_THRESHOLDS imported from threshold_service to avoid duplication


class AlertService:
    """Service for handling alert generation and management."""
    
    def __init__(self, supabase_client):
        """Initialize alert service with Supabase client."""
        self.supabase = supabase_client
        self.realtime_service = get_realtime_service()
        self.logger = get_logger(f"{__name__}.AlertService")
        self.threshold_service = get_threshold_service()
    
    async def check_thresholds_and_create_alerts(
        self, 
        device_id: str, 
        farmer_id: uuid.UUID, 
        temperature: float, 
        humidity: float, 
        ndvi: Optional[float] = None
    ) -> AlertGenerationResponse:
        """
        Check telemetry against thresholds and create alerts if needed.
        
        Args:
            device_id: Device identifier
            farmer_id: Farmer UUID
            temperature: Temperature reading in Celsius
            humidity: Humidity reading in percentage
            ndvi: Optional NDVI reading
            
        Returns:
            Alert generation response with created alert IDs
        """
        start_time = time.time()
        alerts_created = []
        
        try:
            # Use threshold service to check all thresholds
            violations = self.threshold_service.check_all_thresholds(
                temperature=temperature,
                humidity=humidity,
                ndvi=ndvi
            )
            
            # Create alerts for each violation
            for violation in violations:
                alert = await self._create_threshold_alert_from_violation(
                    farmer_id=farmer_id,
                    device_id=device_id,
                    violation=violation
                )
                alerts_created.append(alert)
                
                self.logger.info(
                    "threshold_alert_created",
                    device_id=device_id,
                    metric=violation.metric.value,
                    value=violation.value,
                    threshold=violation.threshold,
                    severity=violation.severity.value
                )
            
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            return AlertGenerationResponse(
                alerts_created=len(alerts_created),
                alert_ids=[alert.id for alert in alerts_created],
                processing_time_ms=processing_time_ms
            )
            
        except Exception as e:
            self.logger.error("alert_generation_error", device_id=device_id, error=str(e))
            raise
    
    async def _create_threshold_alert_from_violation(
        self,
        farmer_id: uuid.UUID,
        device_id: str,
        violation: ThresholdViolation
    ) -> Alert:
        """
        Create a threshold exceeded alert from a violation object.
        
        Args:
            farmer_id: Farmer UUID
            device_id: Device identifier
            violation: Threshold violation object
            
        Returns:
            Created alert object
        """
        # Generate alert message using templates
        message_key = f"{violation.metric.value}_{violation.severity.value.lower()}"
        if message_key in ALERT_MESSAGES:
            message = ALERT_MESSAGES[message_key].format(
                value=violation.value,
                threshold=violation.threshold
            )
        else:
            message = f"Threshold exceeded for {violation.metric.value}: {violation.value} (threshold: {violation.threshold})"
        
        # Create alert data
        alert_data = AlertCreate(
            farmer_id=farmer_id,
            device_id=device_id,
            type=AlertType.THRESHOLD_EXCEEDED,
            severity=violation.severity,
            message=message,
            metric=violation.metric,
            value=violation.value,
            threshold=violation.threshold
        )
        
        return await self._create_alert_in_database(alert_data)
    
    async def _create_threshold_alert(
        self,
        farmer_id: uuid.UUID,
        device_id: str,
        metric: MetricType,
        value: float,
        threshold: float,
        severity: AlertSeverity
    ) -> Alert:
        """
        Create a threshold exceeded alert (legacy method for compatibility).
        
        Args:
            farmer_id: Farmer UUID
            device_id: Device identifier
            metric: Type of metric that triggered alert
            value: Actual metric value
            threshold: Threshold that was exceeded
            severity: Alert severity level
            
        Returns:
            Created alert object
        """
        # Create violation object and use new method
        violation = ThresholdViolation(
            metric=metric,
            value=value,
            threshold=threshold,
            severity=severity,
            operator=">" if metric == MetricType.TEMPERATURE else "<",
            violation_amount=abs(value - threshold)
        )
        
        return await self._create_threshold_alert_from_violation(farmer_id, device_id, violation)
    
    async def _create_alert_in_database(self, alert_data: AlertCreate) -> Alert:
        """
        Insert alert data into database and create Alert object.
        
        Args:
            alert_data: Alert creation data
            
        Returns:
            Created alert object
        """
        try:
            result = self.supabase.table("katara_alerts").insert({
                "farmer_id": str(alert_data.farmer_id),
                "device_id": alert_data.device_id,
                "type": alert_data.type.value,
                "severity": alert_data.severity.value,
                "message": alert_data.message,
                "read_status": False
            }).execute()
            
            if not result.data:
                raise Exception("Failed to insert alert into database")
            
            # Create alert object with additional fields
            alert_record = result.data[0]
            alert = Alert(
                id=uuid.UUID(alert_record["id"]),
                farmer_id=alert_data.farmer_id,
                device_id=alert_data.device_id,
                type=alert_data.type,
                severity=alert_data.severity,
                message=alert_data.message,
                read_status=alert_record["read_status"],
                read_at=datetime.fromisoformat(alert_record["read_at"].replace('Z', '+00:00')) if alert_record.get("read_at") and alert_record["read_at"] else None,
                created_at=datetime.fromisoformat(alert_record["created_at"].replace('Z', '+00:00')),
                metric=alert_data.metric,
                value=alert_data.value,
                threshold=alert_data.threshold
            )
            
            self.logger.debug(
                "alert_created",
                alert_id=str(alert.id),
                farmer_id=str(alert_data.farmer_id),
                device_id=alert_data.device_id,
                metric=alert_data.metric.value if alert_data.metric else None,
                severity=alert_data.severity.value
            )
            
            return alert
            
        except Exception as e:
            self.logger.error("alert_creation_error", error=str(e), alert_data=alert_data.dict())
            raise
    
    async def get_farmer_alerts(
        self,
        farmer_id: uuid.UUID,
        limit: int = 20,
        offset: int = 0,
        severity: Optional[AlertSeverity] = None,
        is_read: Optional[bool] = None,
        device_id: Optional[str] = None
    ) -> List[Alert]:
        """
        Get alerts for a specific farmer with filtering and pagination.
        
        Args:
            farmer_id: Farmer UUID
            limit: Number of alerts to return
            offset: Number of alerts to skip
            severity: Optional severity filter
            is_read: Optional read status filter
            device_id: Optional device ID filter
            
        Returns:
            List of alerts
        """
        try:
            # Build query
            query = self.supabase.table("katara_alerts").select("*").eq("farmer_id", str(farmer_id))
            
            # Apply filters
            if severity:
                query = query.eq("severity", severity.value)
            if is_read is not None:
                query = query.eq("read_status", is_read)
            if device_id:
                query = query.eq("device_id", device_id)
            
            # Apply ordering and pagination
            query = query.order("created_at", desc=True).range(offset, offset + limit - 1)
            
            result = query.execute()
            
            alerts = []
            for alert_record in result.data:
                alert = Alert(
                    id=uuid.UUID(alert_record["id"]),
                    farmer_id=uuid.UUID(alert_record["farmer_id"]),
                    device_id=alert_record.get("device_id"),
                    type=AlertType(alert_record["type"]),
                    severity=AlertSeverity(alert_record["severity"]),
                    message=alert_record["message"],
                    read_status=alert_record["read_status"],
                    read_at=datetime.fromisoformat(alert_record["read_at"].replace('Z', '+00:00')) if alert_record.get("read_at") and alert_record["read_at"] else None,
                    created_at=datetime.fromisoformat(alert_record["created_at"].replace('Z', '+00:00'))
                )
                alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            self.logger.error("get_farmer_alerts_error", farmer_id=str(farmer_id), error=str(e))
            raise
    
    async def get_unread_alerts_count(self, farmer_id: uuid.UUID) -> int:
        """
        Get count of unread alerts for a farmer.
        
        Args:
            farmer_id: Farmer UUID
            
        Returns:
            Number of unread alerts
        """
        try:
            result = self.supabase.table("katara_alerts").select("id", count="exact").eq("farmer_id", str(farmer_id)).eq("read_status", False).execute()
            
            return result.count or 0
            
        except Exception as e:
            self.logger.error("get_unread_alerts_count_error", farmer_id=str(farmer_id), error=str(e))
            return 0
    
    async def update_alert_status(self, alert_id: uuid.UUID, farmer_id: uuid.UUID, read_status: bool) -> Alert:
        """
        Update alert read status (read or unread) for a farmer.
        
        Args:
            alert_id: Alert UUID
            farmer_id: Farmer UUID requesting the update
            read_status: New read status (True=read, False=unread)
            
        Returns:
            Updated alert object
            
        Raises:
            Exception: If alert not found or access denied
        """
        try:
            # First check if alert exists and belongs to farmer
            result = self.supabase.table("katara_alerts").select("*").eq("id", str(alert_id)).eq("farmer_id", str(farmer_id)).execute()
            
            if not result.data:
                raise Exception("Alert not found or access denied")
            
            # Update alert
            update_result = self.supabase.table("katara_alerts").update({
                "read_status": read_status
            }).eq("id", str(alert_id)).eq("farmer_id", str(farmer_id)).execute()
            
            if not update_result.data:
                raise Exception("Failed to update alert")
            
            alert_record = update_result.data[0]
            alert = Alert(
                id=uuid.UUID(alert_record["id"]),
                farmer_id=uuid.UUID(alert_record["farmer_id"]),
                device_id=alert_record.get("device_id"),
                type=AlertType(alert_record["type"]),
                severity=AlertSeverity(alert_record["severity"]),
                message=alert_record["message"],
                read_status=alert_record["read_status"],
                read_at=datetime.fromisoformat(alert_record["read_at"].replace('Z', '+00:00')) if alert_record.get("read_at") and alert_record["read_at"] else None,
                created_at=datetime.fromisoformat(alert_record["created_at"].replace('Z', '+00:00'))
            )
            
            self.logger.info(
                "alert_status_updated",
                alert_id=str(alert_id),
                farmer_id=str(farmer_id),
                new_status=read_status
            )
            
            # Broadcast status change to connected clients
            await self.realtime_service.broadcast_alert_status_change(
                alert_id=alert_id,
                farmer_id=farmer_id,
                read_status=read_status,
                read_at=alert.read_at
            )
            
            return alert
            
        except Exception as e:
            self.logger.error("update_alert_status_error", alert_id=str(alert_id), farmer_id=str(farmer_id), error=str(e))
            raise

    async def bulk_update_alert_status(
        self, 
        alert_ids: List[uuid.UUID], 
        farmer_id: uuid.UUID, 
        read_status: bool
    ) -> Dict[str, Any]:
        """
        Update multiple alerts' read status for a farmer.
        
        Args:
            alert_ids: List of Alert UUIDs
            farmer_id: Farmer UUID requesting the update
            read_status: New read status (True=read, False=unread)
            
        Returns:
            Dictionary with update results
            
        Raises:
            Exception: If alerts not found or access denied
        """
        try:
            # Convert UUIDs to strings for database query
            alert_id_strings = [str(alert_id) for alert_id in alert_ids]
            
            # Verify all alerts exist and belong to farmer
            result = self.supabase.table("katara_alerts").select("*").in_("id", alert_id_strings).eq("farmer_id", str(farmer_id)).execute()
            
            if len(result.data) != len(alert_ids):
                raise Exception("Some alerts not found or access denied")
            
            # Update alerts
            update_result = self.supabase.table("katara_alerts").update({
                "read_status": read_status
            }).in_("id", alert_id_strings).eq("farmer_id", str(farmer_id)).execute()
            
            updated_count = len(update_result.data)
            failed_updates = len(alert_ids) - updated_count
            
            self.logger.info(
                "bulk_alert_status_updated",
                farmer_id=str(farmer_id),
                requested_count=len(alert_ids),
                updated_count=updated_count,
                failed_count=failed_updates,
                new_status=read_status
            )
            
            # Broadcast bulk status changes to connected clients
            await self.realtime_service.broadcast_bulk_alert_status_change(
                updated_alerts=update_result.data,
                farmer_id=farmer_id
            )
            
            return {
                "updated_count": updated_count,
                "failed_updates": failed_updates,
                "updated_alerts": update_result.data
            }
            
        except Exception as e:
            self.logger.error("bulk_update_alert_status_error", farmer_id=str(farmer_id), error=str(e))
            raise

    async def mark_alert_as_read(self, alert_id: uuid.UUID, farmer_id: uuid.UUID) -> Alert:
        """
        Mark an alert as read for a farmer (legacy method for compatibility).
        
        Args:
            alert_id: Alert UUID
            farmer_id: Farmer UUID requesting the update
            
        Returns:
            Updated alert object
            
        Raises:
            Exception: If alert not found or access denied
        """
        return await self.update_alert_status(alert_id, farmer_id, True)
                            
    async def get_alert_statistics(self, farmer_id: uuid.UUID) -> Dict[str, int]:
        """
        Get alert statistics for a farmer.
        
        Args:
            farmer_id: Farmer UUID
            
        Returns:
            Dictionary with alert statistics
        """
        try:
            # Get total alerts
            total_result = self.supabase.table("katara_alerts").select("id", count="exact").eq("farmer_id", str(farmer_id)).execute()
            total_alerts = total_result.count or 0
            
            # Get unread alerts
            unread_result = self.supabase.table("katara_alerts").select("id", count="exact").eq("farmer_id", str(farmer_id)).eq("read_status", False).execute()
            unread_alerts = unread_result.count or 0
            
            # Get alerts by severity
            severity_stats = {}
            for severity in AlertSeverity:
                severity_result = self.supabase.table("katara_alerts").select("id", count="exact").eq("farmer_id", str(farmer_id)).eq("severity", severity.value).execute()
                severity_stats[f"{severity.value}_severity"] = severity_result.count or 0
            
            return {
                "total_alerts": total_alerts,
                "unread_alerts": unread_alerts,
                **severity_stats
            }
            
        except Exception as e:
            self.logger.error("get_alert_statistics_error", farmer_id=str(farmer_id), error=str(e))
            return {
                "total_alerts": 0,
                "unread_alerts": 0,
                "low_severity": 0,
                "medium_severity": 0,
                "high_severity": 0,
                "critical_severity": 0
            }


# Factory function for dependency injection
def get_alert_service() -> AlertService:
    """Create alert service instance."""
    supabase = get_supabase_client()
    return AlertService(supabase)
