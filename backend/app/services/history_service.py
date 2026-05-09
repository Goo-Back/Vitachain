"""
History service for VitaChain KATARA telemetry analysis
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from supabase import Client
from app.models.schemas import (
    HistoryParams, 
    HistoryResponse, 
    PeriodInfo, 
    DeviceChartData, 
    HourlyData, 
    DailyStats,
    TrendAnalysis,
    AlertPattern
)
from app.services.analytics_service import AnalyticsService
from app.core.database import get_supabase_client


class HistoryService:
    """Service for historical telemetry data analysis"""
    
    def __init__(self):
        self.supabase = get_supabase_client()
        self.analytics_service = AnalyticsService()
    
    async def get_historical_telemetry(
        self, 
        farmer_id: uuid.UUID, 
        params: HistoryParams
    ) -> HistoryResponse:
        """
        Get comprehensive historical telemetry analysis
        """
        # Validate date range
        if params.end_date <= params.start_date:
            raise ValueError("End date must be after start date")
        
        # Limit date range to prevent excessive data loading
        max_days = 365  # Maximum 1 year of data
        if (params.end_date - params.start_date).days > max_days:
            raise ValueError(f"Date range cannot exceed {max_days} days")
        
        # Get aggregated chart data
        chart_data = await self._get_aggregated_telemetry(
            farmer_id, params.start_date, params.end_date, 
            params.device_id, params.aggregation
        )
        
        # Get daily statistics
        daily_stats = await self._get_daily_statistics(
            farmer_id, params.start_date, params.end_date, params.device_id
        )
        
        # Calculate trend analysis
        trend_analysis = await self._calculate_trends(chart_data)
        
        # Get alert patterns
        alert_patterns = await self._get_alert_patterns(
            farmer_id, params.start_date, params.end_date
        )
        
        # Calculate period info
        total_readings = sum(
            len(device.hourly_data) for device in chart_data
        )
        devices_analyzed = len(chart_data)
        
        period_info = PeriodInfo(
            start_date=params.start_date,
            end_date=params.end_date,
            total_readings=total_readings,
            devices_analyzed=devices_analyzed
        )
        
        return HistoryResponse(
            period_info=period_info,
            chart_data=chart_data,
            daily_stats=daily_stats,
            trend_analysis=trend_analysis,
            alert_patterns=alert_patterns
        )
    
    async def _get_aggregated_telemetry(
        self,
        farmer_id: uuid.UUID,
        start_date: datetime,
        end_date: datetime,
        device_id: Optional[str],
        aggregation: str
    ) -> List[DeviceChartData]:
        """
        Get aggregated telemetry data for charts
        """
        # Build base query
        query = self.supabase.table('telemetry_readings') \
            .select('device_id, temperature, humidity, ndvi, timestamp') \
            .eq('farmer_id', str(farmer_id)) \
            .gte('timestamp', start_date.isoformat()) \
            .lte('timestamp', end_date.isoformat()) \
            .order('timestamp')
        
        # Filter by specific device if provided
        if device_id:
            query = query.eq('device_id', device_id)
        
        result = query.execute()
        
        if not result.data:
            return []
        
        # Get device information for names
        device_ids = list(set(reading['device_id'] for reading in result.data))
        device_info = await self._get_device_info(farmer_id, device_ids)
        
        # Group data by device and aggregate
        device_data: Dict[str, List[Dict]] = {}
        for reading in result.data:
            device_id = reading['device_id']
            if device_id not in device_data:
                device_data[device_id] = []
            device_data[device_id].append(reading)
        
        # Aggregate data for each device
        chart_data = []
        for device_id, readings in device_data.items():
            hourly_aggregated = self._aggregate_readings(readings, aggregation)
            
            device_chart = DeviceChartData(
                device_id=device_id,
                device_name=device_info.get(device_id, {}).get('name'),
                hourly_data=hourly_aggregated
            )
            chart_data.append(device_chart)
        
        return chart_data
    
    async def _get_device_info(
        self, 
        farmer_id: uuid.UUID, 
        device_ids: List[str]
    ) -> Dict[str, Dict]:
        """
        Get device information for names
        """
        if not device_ids:
            return {}
        
        result = self.supabase.table('iot_devices') \
            .select('device_id, name') \
            .eq('farmer_id', str(farmer_id)) \
            .in_('device_id', device_ids) \
            .execute()
        
        device_info = {}
        for device in result.data:
            device_info[device['device_id']] = device
        
        return device_info
    
    def _aggregate_readings(
        self, 
        readings: List[Dict], 
        aggregation: str
    ) -> List[HourlyData]:
        """
        Aggregate telemetry readings by time period
        """
        if not readings:
            return []
        
        # Group readings by time bucket
        time_buckets: Dict[datetime, List[Dict]] = {}
        
        for reading in readings:
            timestamp = datetime.fromisoformat(reading['timestamp'].replace('Z', '+00:00'))
            
            if aggregation == 'hour':
                bucket = timestamp.replace(minute=0, second=0, microsecond=0)
            else:  # day
                bucket = timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
            
            if bucket not in time_buckets:
                time_buckets[bucket] = []
            time_buckets[bucket].append(reading)
        
        # Calculate aggregates for each bucket
        aggregated_data = []
        for bucket_time, bucket_readings in sorted(time_buckets.items()):
            temps = [r['temperature'] for r in bucket_readings if r['temperature'] is not None]
            humidities = [r['humidity'] for r in bucket_readings if r['humidity'] is not None]
            ndvis = [r['ndvi'] for r in bucket_readings if r['ndvi'] is not None]
            
            hourly_data = HourlyData(
                hour_bucket=bucket_time,
                avg_temp=sum(temps) / len(temps) if temps else None,
                min_temp=min(temps) if temps else None,
                max_temp=max(temps) if temps else None,
                avg_humidity=sum(humidities) / len(humidities) if humidities else None,
                avg_ndvi=sum(ndvis) / len(ndvis) if ndvis else None,
                reading_count=len(bucket_readings)
            )
            aggregated_data.append(hourly_data)
        
        return aggregated_data
    
    async def _get_daily_statistics(
        self,
        farmer_id: uuid.UUID,
        start_date: datetime,
        end_date: datetime,
        device_id: Optional[str]
    ) -> List[DailyStats]:
        """
        Get daily statistics for telemetry data
        """
        # Build base query
        query = self.supabase.table('telemetry_readings') \
            .select('temperature, humidity, ndvi, timestamp') \
            .eq('farmer_id', str(farmer_id)) \
            .gte('timestamp', start_date.isoformat()) \
            .lte('timestamp', end_date.isoformat()) \
            .order('timestamp')
        
        # Filter by specific device if provided
        if device_id:
            query = query.eq('device_id', device_id)
        
        result = query.execute()
        
        if not result.data:
            return []
        
        # Group by date
        daily_data: Dict[str, List[Dict]] = {}
        for reading in result.data:
            date_str = datetime.fromisoformat(reading['timestamp'].replace('Z', '+00:00')).date().isoformat()
            if date_str not in daily_data:
                daily_data[date_str] = []
            daily_data[date_str].append(reading)
        
        # Calculate daily statistics
        daily_stats = []
        for date_str, day_readings in sorted(daily_data.items()):
            temps = [r['temperature'] for r in day_readings if r['temperature'] is not None]
            humidities = [r['humidity'] for r in day_readings if r['humidity'] is not None]
            ndvis = [r['ndvi'] for r in day_readings if r['ndvi'] is not None]
            
            daily_stat = DailyStats(
                date=date_str,
                avg_temp=sum(temps) / len(temps) if temps else None,
                min_temp=min(temps) if temps else None,
                max_temp=max(temps) if temps else None,
                avg_humidity=sum(humidities) / len(humidities) if humidities else None,
                avg_ndvi=sum(ndvis) / len(ndvis) if ndvis else None,
                total_readings=len(day_readings)
            )
            daily_stats.append(daily_stat)
        
        return daily_stats
    
    async def _calculate_trends(
        self, 
        chart_data: List[DeviceChartData]
    ) -> TrendAnalysis:
        """
        Calculate trend analysis from chart data
        """
        # Collect all data points across devices
        all_temps = []
        all_humidities = []
        all_ndvis = []
        
        for device in chart_data:
            for hour_data in device.hourly_data:
                if hour_data.avg_temp is not None:
                    all_temps.append(hour_data.avg_temp)
                if hour_data.avg_humidity is not None:
                    all_humidities.append(hour_data.avg_humidity)
                if hour_data.avg_ndvi is not None:
                    all_ndvis.append(hour_data.avg_ndvi)
        
        # Calculate trends using analytics service
        temp_trend = self.analytics_service.calculate_trend(all_temps)
        humidity_trend = self.analytics_service.calculate_trend(all_humidities)
        ndvi_trend = self.analytics_service.calculate_trend(all_ndvis)
        
        # Calculate correlations
        temp_humidity_corr = self.analytics_service.calculate_correlation(all_temps, all_humidities)
        temp_ndvi_corr = self.analytics_service.calculate_correlation(all_temps, all_ndvis)
        
        return TrendAnalysis(
            temperature_trend=temp_trend,
            humidity_trend=humidity_trend,
            ndvi_trend=ndvi_trend,
            correlations={
                "temp_humidity": temp_humidity_corr,
                "temp_ndvi": temp_ndvi_corr
            }
        )
    
    async def _get_alert_patterns(
        self,
        farmer_id: uuid.UUID,
        start_date: datetime,
        end_date: datetime
    ) -> List[AlertPattern]:
        """
        Get alert patterns for the specified period
        """
        result = self.supabase.table('katara_alerts') \
            .select('severity, type, created_at') \
            .eq('farmer_id', str(farmer_id)) \
            .gte('created_at', start_date.isoformat()) \
            .lte('created_at', end_date.isoformat()) \
            .order('created_at') \
            .execute()
        
        if not result.data:
            return []
        
        # Group alerts by date and severity
        alert_data: Dict[str, Dict] = {}
        for alert in result.data:
            date_str = datetime.fromisoformat(alert['created_at'].replace('Z', '+00:00')).date().isoformat()
            
            if date_str not in alert_data:
                alert_data[date_str] = {
                    'high': 0,
                    'medium': 0,
                    'low': 0,
                    'causes': []
                }
            
            severity = alert['severity'].lower()
            if severity in alert_data[date_str]:
                alert_data[date_str][severity] += 1
            
            alert_data[date_str]['causes'].append(alert['type'])
        
        # Create alert patterns
        alert_patterns = []
        for date_str, data in sorted(alert_data.items()):
            # Get unique causes (top 3 most common)
            causes = list(set(data['causes']))[:3]
            
            alert_pattern = AlertPattern(
                date=date_str,
                high_alerts=data['high'],
                medium_alerts=data['medium'],
                low_alerts=data['low'],
                main_causes=causes
            )
            alert_patterns.append(alert_pattern)
        
        return alert_patterns
