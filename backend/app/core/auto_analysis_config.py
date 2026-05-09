"""
Automatic Analysis Configuration Constants
Centralized configuration for automatic AI recommendation generation
"""

from typing import Dict, Any


class AutoAnalysisConfig:
    """Configuration constants for automatic AI analysis"""
    
    # Critical thresholds for triggering automatic analysis
    CRITICAL_TEMPERATURE_THRESHOLD = 40.0  # °C
    CRITICAL_HUMIDITY_THRESHOLD = 20.0    # %  
    CRITICAL_NDVI_THRESHOLD = 0.3         # Vegetation stress
    
    # Critical thresholds for priority determination
    CRITICAL_TEMP_HIGH = 42.0             # °C - critical priority
    CRITICAL_HUMIDITY_LOW = 15.0          # % - critical priority
    CRITICAL_NDVI_LOW = 0.2              # - critical priority
    
    # Condition change detection thresholds
    CONDITION_VARIANCE_THRESHOLD = 0.1    # 10% variance for significant change
    NDVI_VARIANCE_THRESHOLD = 0.05        # 0.05 NDVI variance for significant change
    
    # Rate limiting and frequency control
    DEFAULT_FREQUENCY_HOURS = 6            # Default hours between analyses
    MIN_FREQUENCY_HOURS = 2                # Minimum allowed frequency
    MAX_FREQUENCY_HOURS = 24               # Maximum allowed frequency
    
    # Background job scheduling
    DAILY_ANALYSIS_HOUR = 2                # UTC hour for daily analysis (2 AM)
    HOURLY_CHECK_INTERVAL = 1               # Hours between immediate analysis checks
    CLEANUP_DAYS_OLD = 90                  # Days for data cleanup
    
    # Performance and timeout settings
    TELEMETRY_PROCESSING_THRESHOLD_MS = 50  # Max processing time for telemetry
    AI_ANALYSIS_TIMEOUT_SECONDS = 30       # AI analysis timeout
    DEVICE_DELAY_SECONDS = 1               # Delay between devices in batch processing
    
    # Data collection periods
    TELEMETRY_ANALYSIS_DAYS = 7            # Days of telemetry to analyze
    RECENT_TELEMETRY_HOURS = 1             # Hours for recent activity check
    ACTIVE_DEVICE_DAYS = 7                  # Days to consider device active
    
    # Alert and notification settings
    DEFAULT_ALERT_PRIORITY = "medium"        # Default priority for periodic analysis
    CRITICAL_ALERT_PRIORITY = "high"        # Priority for critical conditions
    
    # Context enrichment settings
    WEATHER_CACHE_TTL = 300                 # Weather cache TTL in seconds (5 minutes)
    NDVI_CACHE_TTL = 3600                   # NDVI cache TTL in seconds (1 hour)
    
    # Retry and fallback settings
    MAX_RETRY_ATTEMPTS = 3                  # Max retry attempts for failed operations
    RETRY_DELAY_SECONDS = 5                 # Delay between retries
    
    # Monitoring and metrics
    METRICS_ENABLED = True                  # Enable performance metrics
    LOG_LEVEL = "INFO"                      # Default log level
    
    @classmethod
    def get_critical_thresholds(cls) -> Dict[str, float]:
        """Get all critical thresholds for analysis triggering"""
        return {
            "temperature": cls.CRITICAL_TEMPERATURE_THRESHOLD,
            "humidity": cls.CRITICAL_HUMIDITY_THRESHOLD,
            "ndvi": cls.CRITICAL_NDVI_THRESHOLD
        }
    
    @classmethod
    def get_priority_thresholds(cls) -> Dict[str, Dict[str, float]]:
        """Get thresholds for determining analysis priority"""
        return {
            "critical": {
                "temperature": cls.CRITICAL_TEMP_HIGH,
                "humidity": cls.CRITICAL_HUMIDITY_LOW,
                "ndvi": cls.CRITICAL_NDVI_LOW
            },
            "high": {
                "temperature": cls.CRITICAL_TEMPERATURE_THRESHOLD,
                "humidity": cls.CRITICAL_HUMIDITY_THRESHOLD,
                "ndvi": cls.CRITICAL_NDVI_THRESHOLD
            }
        }
    
    @classmethod
    def validate_frequency_hours(cls, hours: int) -> bool:
        """Validate analysis frequency hours"""
        return cls.MIN_FREQUENCY_HOURS <= hours <= cls.MAX_FREQUENCY_HOURS
    
    @classmethod
    def get_analysis_priority(cls, temperature: float, humidity: float, ndvi: float = None) -> str:
        """Determine analysis priority based on conditions"""
        # Check for critical conditions
        if (temperature >= cls.CRITICAL_TEMP_HIGH or 
            humidity <= cls.CRITICAL_HUMIDITY_LOW or
            (ndvi is not None and ndvi <= cls.CRITICAL_NDVI_LOW)):
            return "critical"
        
        # Check for high conditions
        if (temperature >= cls.CRITICAL_TEMPERATURE_THRESHOLD or 
            humidity <= cls.CRITICAL_HUMIDITY_THRESHOLD or
            (ndvi is not None and ndvi <= cls.CRITICAL_NDVI_THRESHOLD)):
            return "high"
        
        return "medium"
    
    @classmethod
    def conditions_significantly_changed(
        cls, 
        current: Dict[str, float], 
        previous: Dict[str, float]
    ) -> bool:
        """Check if conditions have significantly changed"""
        # Check temperature variance
        if "temperature" in current and "temperature" in previous:
            temp_variance = abs(current["temperature"] - previous["temperature"])
            if previous["temperature"] > 0:
                temp_variance = temp_variance / previous["temperature"]
                if temp_variance > cls.CONDITION_VARIANCE_THRESHOLD:
                    return True
        
        # Check humidity variance
        if "humidity" in current and "humidity" in previous:
            humidity_variance = abs(current["humidity"] - previous["humidity"])
            if previous["humidity"] > 0:
                humidity_variance = humidity_variance / previous["humidity"]
                if humidity_variance > cls.CONDITION_VARIANCE_THRESHOLD:
                    return True
        
        # Check NDVI variance
        if "ndvi" in current and "ndvi" in previous and current["ndvi"] is not None and previous["ndvi"] is not None:
            ndvi_variance = abs(current["ndvi"] - previous["ndvi"])
            if ndvi_variance > cls.NDVI_VARIANCE_THRESHOLD:
                return True
        
        return False
