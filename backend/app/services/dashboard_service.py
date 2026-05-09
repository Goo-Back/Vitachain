"""
Dashboard service for KATARA module - aggregates data for real-time dashboard visualization
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from app.core.logging import get_logger
from app.models.schemas import (
    DashboardResponse, DashboardDevice, SummaryStats, AlertsInfo,
    DashboardAlert, TrendData, TelemetryPoint, CurrentTelemetry,
    DeviceStatus, AlertSeverity
)

logger = get_logger(__name__)


class DashboardService:
    """Service for aggregating KATARA dashboard data"""

    def __init__(self, supabase_client):
        """Initialize dashboard service with Supabase client"""
        self.supabase = supabase_client
        self.offline_threshold_minutes = 10  # Device considered offline after 10 minutes

    async def get_dashboard_data(self, farmer_id: uuid.UUID) -> DashboardResponse:
        """
        Get complete dashboard data for a farmer
        
        Args:
            farmer_id: UUID of the farmer
            
        Returns:
            DashboardResponse with all dashboard data
        """
        try:
            logger.info(f"Fetching dashboard data for farmer: {farmer_id}")
            
            # Get devices with latest telemetry
            devices = await self._get_farmer_devices_with_telemetry(farmer_id)
            
            # Calculate summary statistics
            summary_stats = self._calculate_summary_stats(devices)
            
            # Get alerts information
            alerts = await self._get_farmer_alerts(farmer_id)
            
            # Get 24-hour trend data
            trend_data = await self._get_trend_data(farmer_id)
            
            dashboard_response = DashboardResponse(
                devices=devices,
                summary_stats=summary_stats,
                alerts=alerts,
                trend_data=trend_data
            )
            
            logger.info(f"Dashboard data assembled for farmer {farmer_id}: "
                       f"{len(devices)} devices, {alerts.unread_count} alerts")
            
            return dashboard_response
            
        except Exception as e:
            logger.error(f"Error fetching dashboard data for farmer {farmer_id}: {str(e)}")
            raise

    async def _get_farmer_devices_with_telemetry(self, farmer_id: uuid.UUID) -> List[DashboardDevice]:
        """
        Get farmer's devices with their latest telemetry data
        
        Args:
            farmer_id: UUID of the farmer
            
        Returns:
            List of DashboardDevice objects
        """
        try:
            # Get farmer's devices
            devices_result = (
                self.supabase.table('iot_devices')
                .select('*')
                .eq('farmer_id', str(farmer_id))
                .order('registered_at', desc=True)
                .execute()
            )
            
            if not devices_result.data:
                return []
            
            devices = []
            for device_data in devices_result.data:
                device_id = device_data['device_id']
                
                # Get latest telemetry for this device
                telemetry_result = (
                    self.supabase.table('telemetry_readings')
                    .select('*')
                    .eq('device_id', device_id)
                    .order('timestamp', desc=True)
                    .limit(1)
                    .execute()
                )
                
                # Determine device status and telemetry
                latest_telemetry = telemetry_result.data[0] if telemetry_result.data else None
                
                if latest_telemetry:
                    last_seen_dt = datetime.fromisoformat(latest_telemetry['timestamp'].replace('Z', '+00:00'))
                    time_diff = datetime.now(last_seen_dt.tzinfo) - last_seen_dt
                    status = DeviceStatus.ONLINE if time_diff.total_seconds() < (self.offline_threshold_minutes * 60) else DeviceStatus.OFFLINE
                    
                    current_telemetry = CurrentTelemetry(
                        temperature=latest_telemetry.get('temperature'),
                        humidity=latest_telemetry.get('humidity'),
                        ndvi=latest_telemetry.get('ndvi'),
                        battery_level=latest_telemetry.get('battery_level'),
                        timestamp=last_seen_dt
                    )
                else:
                    last_seen_dt = datetime.now()
                    status = DeviceStatus.UNKNOWN
                    current_telemetry = None
                
                dashboard_device = DashboardDevice(
                    id=uuid.UUID(device_data['id']),
                    device_id=device_data['device_id'],
                    name=device_data.get('name'),
                    location_lat=device_data.get('location_lat'),
                    location_lng=device_data.get('location_lng'),
                    status=status,
                    last_seen=last_seen_dt,
                    current_telemetry=current_telemetry
                )
                
                devices.append(dashboard_device)
            
            return devices
            
        except Exception as e:
            logger.error(f"Error fetching devices with telemetry: {str(e)}")
            raise

    def _calculate_summary_stats(self, devices: List[DashboardDevice]) -> SummaryStats:
        """
        Calculate summary statistics from device data
        
        Args:
            devices: List of DashboardDevice objects
            
        Returns:
            SummaryStats object
        """
        try:
            total_devices = len(devices)
            online_devices = sum(1 for device in devices if device.status == DeviceStatus.ONLINE)
            offline_devices = total_devices - online_devices
            
            # Calculate averages from devices with current telemetry
            temperatures = []
            humidities = []
            ndvis = []
            
            for device in devices:
                if device.current_telemetry:
                    if device.current_telemetry.temperature is not None:
                        temperatures.append(device.current_telemetry.temperature)
                    if device.current_telemetry.humidity is not None:
                        humidities.append(device.current_telemetry.humidity)
                    if device.current_telemetry.ndvi is not None:
                        ndvis.append(device.current_telemetry.ndvi)
            
            avg_temperature = sum(temperatures) / len(temperatures) if temperatures else None
            avg_humidity = sum(humidities) / len(humidities) if humidities else None
            avg_ndvi = sum(ndvis) / len(ndvis) if ndvis else None
            
            return SummaryStats(
                avg_temperature=avg_temperature,
                avg_humidity=avg_humidity,
                avg_ndvi=avg_ndvi,
                total_devices=total_devices,
                online_devices=online_devices,
                offline_devices=offline_devices
            )
            
        except Exception as e:
            logger.error(f"Error calculating summary stats: {str(e)}")
            raise

    async def _get_farmer_alerts(self, farmer_id: uuid.UUID) -> AlertsInfo:
        """
        Get farmer's alerts information
        
        Args:
            farmer_id: UUID of the farmer
            
        Returns:
            AlertsInfo object
        """
        try:
            # Get unread alerts count
            unread_result = self.supabase.table('katara_alerts').select('count').eq('farmer_id', str(farmer_id)).eq('is_read', False).execute()
            unread_count = len(unread_result.data) if unread_result.data else 0
            
            # Get recent alerts (last 10)
            recent_result = (
                self.supabase.table('katara_alerts')
                .select('*')
                .eq('farmer_id', str(farmer_id))
                .order('created_at', desc=True)
                .limit(10)
                .execute()
            )
            
            recent_alerts = []
            if recent_result.data:
                for alert_data in recent_result.data:
                    dashboard_alert = DashboardAlert(
                        id=uuid.UUID(alert_data['id']),
                        type=alert_data['type'],
                        severity=AlertSeverity(alert_data['severity']),
                        message=alert_data['message'],
                        created_at=datetime.fromisoformat(alert_data['created_at'].replace('Z', '+00:00'))
                    )
                    recent_alerts.append(dashboard_alert)
            
            return AlertsInfo(
                unread_count=unread_count,
                recent_alerts=recent_alerts
            )
            
        except Exception as e:
            logger.error(f"Error fetching alerts: {str(e)}")
            # Return empty alerts if error occurs
            return AlertsInfo(unread_count=0, recent_alerts=[])

    async def _get_trend_data(self, farmer_id: uuid.UUID, hours: int = 24) -> TrendData:
        """
        Get trend data for dashboard charts
        
        Args:
            farmer_id: UUID of the farmer
            hours: Number of hours of historical data to fetch
            
        Returns:
            TrendData object
        """
        try:
            # Calculate time threshold
            time_threshold = datetime.now() - timedelta(hours=hours)
            
            # Get telemetry data for the last N hours
            result = (
                self.supabase.table('telemetry_readings')
                .select('device_id, temperature, humidity, ndvi, timestamp')
                .eq('farmer_id', str(farmer_id))
                .gte('timestamp', time_threshold.isoformat())
                .order('timestamp', desc=True)
                .execute()
            )
            
            telemetry_points = []
            if result.data:
                for telemetry_data in result.data:
                    telemetry_point = TelemetryPoint(
                        device_id=telemetry_data['device_id'],
                        temperature=telemetry_data.get('temperature'),
                        humidity=telemetry_data.get('humidity'),
                        ndvi=telemetry_data.get('ndvi'),
                        timestamp=datetime.fromisoformat(telemetry_data['timestamp'].replace('Z', '+00:00'))
                    )
                    telemetry_points.append(telemetry_point)
            
            return TrendData(last_24_hours=telemetry_points)
            
        except Exception as e:
            logger.error(f"Error fetching trend data: {str(e)}")
            # Return empty trend data if error occurs
            return TrendData(last_24_hours=[])

    async def get_device_status(self, farmer_id: uuid.UUID, device_id: str) -> Dict[str, Any]:
        """
        Get detailed status for a specific device
        
        Args:
            farmer_id: UUID of the farmer
            device_id: Device identifier
            
        Returns:
            Device status information
        """
        try:
            # Get device info
            device_result = (
                self.supabase.table('iot_devices')
                .select('*')
                .eq('farmer_id', str(farmer_id))
                .eq('device_id', device_id)
                .execute()
            )
            
            if not device_result.data:
                raise ValueError(f"Device {device_id} not found for farmer {farmer_id}")
            
            device_data = device_result.data[0]
            
            # Get latest telemetry
            telemetry_result = (
                self.supabase.table('telemetry_readings')
                .select('*')
                .eq('device_id', device_id)
                .order('timestamp', desc=True)
                .limit(1)
                .execute()
            )
            
            latest_telemetry = telemetry_result.data[0] if telemetry_result.data else None
            
            return {
                'device': device_data,
                'latest_telemetry': latest_telemetry,
                'status': self._determine_device_status(latest_telemetry)
            }
            
        except Exception as e:
            logger.error(f"Error getting device status: {str(e)}")
            raise

    def _determine_device_status(self, telemetry_data: Optional[Dict[str, Any]]) -> DeviceStatus:
        """
        Determine device status based on latest telemetry
        
        Args:
            telemetry_data: Latest telemetry data or None
            
        Returns:
            DeviceStatus enum value
        """
        if not telemetry_data:
            return DeviceStatus.UNKNOWN
        
        try:
            timestamp = datetime.fromisoformat(telemetry_data['timestamp'].replace('Z', '+00:00'))
            time_diff = datetime.now(timestamp.tzinfo) - timestamp
            
            if time_diff.total_seconds() < (self.offline_threshold_minutes * 60):
                return DeviceStatus.ONLINE
            else:
                return DeviceStatus.OFFLINE
                
        except Exception:
            return DeviceStatus.UNKNOWN
