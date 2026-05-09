"""Performance monitoring service with metrics collection and alerting."""

import asyncio
import time
import json
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import psutil

from app.core.performance import performance_monitor, get_current_system_metrics, performance_health_check
from app.core.cache import cache_service
from app.core.database import get_database_optimizer
from app.core.logging import get_logger
from app.core.config import get_settings

logger = get_logger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class PerformanceAlert:
    """Performance alert data structure."""
    id: str
    severity: AlertSeverity
    metric_name: str
    current_value: float
    threshold_value: float
    message: str
    timestamp: float
    resolved: bool = False
    resolved_at: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class MetricThreshold:
    """Metric threshold configuration."""
    name: str
    warning_threshold: float
    critical_threshold: float
    severity: AlertSeverity
    enabled: bool = True
    description: str = ""
    
    def check_alert(self, current_value: float) -> Optional[AlertSeverity]:
        """Check if current value triggers an alert."""
        if not self.enabled:
            return None
        
        if current_value >= self.critical_threshold:
            return AlertSeverity.CRITICAL
        elif current_value >= self.warning_threshold:
            return AlertSeverity.MEDIUM
        
        return None


class MonitoringService:
    """Comprehensive performance monitoring service."""
    
    def __init__(self):
        self.alerts: List[PerformanceAlert] = []
        self.thresholds: Dict[str, MetricThreshold] = {}
        self.alert_handlers: List[Callable] = []
        self._monitoring_active = False
        self._monitoring_task: Optional[asyncio.Task] = None
        
        # Initialize default thresholds
        self._initialize_thresholds()
    
    def _initialize_thresholds(self):
        """Initialize default metric thresholds."""
        default_thresholds = {
            "response_time_p95": MetricThreshold(
                name="response_time_p95",
                warning_threshold=200.0,  # 200ms
                critical_threshold=500.0,  # 500ms
                severity=AlertSeverity.HIGH,
                description="95th percentile API response time"
            ),
            "cpu_usage": MetricThreshold(
                name="cpu_usage",
                warning_threshold=70.0,   # 70%
                critical_threshold=90.0,  # 90%
                severity=AlertSeverity.HIGH,
                description="System CPU usage percentage"
            ),
            "memory_usage": MetricThreshold(
                name="memory_usage",
                warning_threshold=75.0,   # 75%
                critical_threshold=90.0,  # 90%
                severity=AlertSeverity.HIGH,
                description="System memory usage percentage"
            ),
            "disk_usage": MetricThreshold(
                name="disk_usage",
                warning_threshold=80.0,   # 80%
                critical_threshold=95.0,  # 95%
                severity=AlertSeverity.MEDIUM,
                description="Disk usage percentage"
            ),
            "cache_hit_rate": MetricThreshold(
                name="cache_hit_rate",
                warning_threshold=70.0,   # 70%
                critical_threshold=50.0,  # 50% (inverted - lower is worse)
                severity=AlertSeverity.MEDIUM,
                description="Cache hit rate percentage"
            ),
            "error_rate": MetricThreshold(
                name="error_rate",
                warning_threshold=5.0,    # 5%
                critical_threshold=10.0,  # 10%
                severity=AlertSeverity.HIGH,
                description="API error rate percentage"
            ),
            "database_query_time": MetricThreshold(
                name="database_query_time",
                warning_threshold=100.0,  # 100ms
                critical_threshold=500.0,  # 500ms
                severity=AlertSeverity.MEDIUM,
                description="Database query response time"
            ),
            "active_connections": MetricThreshold(
                name="active_connections",
                warning_threshold=800,    # 800 connections
                critical_threshold=1000,   # 1000 connections
                severity=AlertSeverity.MEDIUM,
                description="Active network connections"
            )
        }
        
        self.thresholds.update(default_thresholds)
    
    def add_alert_handler(self, handler: Callable):
        """Add custom alert handler."""
        self.alert_handlers.append(handler)
    
    def update_threshold(self, metric_name: str, warning: float, critical: float, enabled: bool = True):
        """Update metric threshold."""
        if metric_name in self.thresholds:
            self.thresholds[metric_name].warning_threshold = warning
            self.thresholds[metric_name].critical_threshold = critical
            self.thresholds[metric_name].enabled = enabled
            logger.info("threshold_updated", metric=metric_name, warning=warning, critical=critical)
        else:
            logger.warning("threshold_not_found", metric=metric_name)
    
    async def collect_metrics(self) -> Dict[str, Any]:
        """Collect comprehensive performance metrics."""
        timestamp = time.time()
        
        # System metrics
        system_metrics = get_current_system_metrics()
        
        # Performance monitor stats
        endpoint_stats = {}
        slow_endpoints = performance_monitor.get_top_slow_endpoints(limit=10, minutes=15)
        for endpoint_stat in slow_endpoints:
            endpoint_stats[endpoint_stat["endpoint"]] = endpoint_stat
        
        # Calculate P95 response time
        response_times = [ep["avg_response_time_ms"] for ep in slow_endpoints]
        p95_response_time = self._calculate_percentile(response_times, 95) if response_times else 0.0
        
        # Cache metrics
        cache_stats = await cache_service.get_stats()
        cache_memory_info = await cache_service.get_memory_info()
        
        # Database metrics
        db_stats = {}
        db_optimizer = get_database_optimizer()
        if db_optimizer:
            db_stats_obj = await db_optimizer.get_database_stats(minutes=15)
            db_stats = asdict(db_stats_obj)
        
        # Calculate error rate
        total_requests = sum(ep["request_count"] for ep in slow_endpoints)
        error_requests = sum(ep["request_count"] for ep in slow_endpoints if "error" in ep.get("endpoint", "").lower())
        error_rate = (error_requests / total_requests * 100) if total_requests > 0 else 0.0
        
        # Compile metrics
        metrics = {
            "timestamp": timestamp,
            "system": asdict(system_metrics),
            "performance": {
                "p95_response_time_ms": p95_response_time,
                "slow_endpoints": slow_endpoints[:5],
                "total_requests": total_requests,
                "error_rate_percent": error_rate
            },
            "cache": {
                **cache_stats,
                "memory_info": cache_memory_info
            },
            "database": db_stats,
            "health": await performance_health_check()
        }
        
        return metrics
    
    async def check_thresholds(self, metrics: Dict[str, Any]) -> List[PerformanceAlert]:
        """Check metrics against thresholds and generate alerts."""
        new_alerts = []
        
        # Check system metrics
        system = metrics.get("system", {})
        self._check_metric_thresholds("cpu_usage", system.get("cpu_percent", 0), new_alerts)
        self._check_metric_thresholds("memory_usage", system.get("memory_percent", 0), new_alerts)
        self._check_metric_thresholds("disk_usage", system.get("disk_usage_percent", 0), new_alerts)
        self._check_metric_thresholds("active_connections", system.get("active_connections", 0), new_alerts)
        
        # Check performance metrics
        performance = metrics.get("performance", {})
        self._check_metric_thresholds("response_time_p95", performance.get("p95_response_time_ms", 0), new_alerts)
        self._check_metric_thresholds("error_rate", performance.get("error_rate_percent", 0), new_alerts)
        
        # Check cache metrics
        cache = metrics.get("cache", {})
        hit_rate = cache.get("hit_rate_percent", 0)
        # For cache hit rate, lower is worse, so we invert the check
        if hit_rate < 50:  # Critical threshold for low hit rate
            alert = PerformanceAlert(
                id=f"cache_hit_rate_{int(time.time())}",
                severity=AlertSeverity.CRITICAL,
                metric_name="cache_hit_rate",
                current_value=hit_rate,
                threshold_value=50.0,
                message=f"Cache hit rate critically low: {hit_rate:.1f}%",
                timestamp=time.time()
            )
            new_alerts.append(alert)
        elif hit_rate < 70:  # Warning threshold for low hit rate
            alert = PerformanceAlert(
                id=f"cache_hit_rate_{int(time.time())}",
                severity=AlertSeverity.MEDIUM,
                metric_name="cache_hit_rate",
                current_value=hit_rate,
                threshold_value=70.0,
                message=f"Cache hit rate low: {hit_rate:.1f}%",
                timestamp=time.time()
            )
            new_alerts.append(alert)
        
        # Check database metrics
        database = metrics.get("database", {})
        avg_query_time = database.get("avg_execution_time_ms", 0)
        self._check_metric_thresholds("database_query_time", avg_query_time, new_alerts)
        
        return new_alerts
    
    def _check_metric_thresholds(self, metric_name: str, current_value: float, alerts: List[PerformanceAlert]):
        """Check a single metric against its thresholds."""
        threshold = self.thresholds.get(metric_name)
        if not threshold or not threshold.enabled:
            return
        
        alert_severity = threshold.check_alert(current_value)
        if alert_severity:
            # Check if we already have an unresolved alert for this metric
            existing_alert = self._get_unresolved_alert(metric_name)
            
            if not existing_alert:
                # Create new alert
                alert = PerformanceAlert(
                    id=f"{metric_name}_{int(time.time())}",
                    severity=alert_severity,
                    metric_name=metric_name,
                    current_value=current_value,
                    threshold_value=threshold.warning_threshold,
                    message=f"{threshold.description}: {current_value:.2f} (threshold: {threshold.warning_threshold})",
                    timestamp=time.time()
                )
                alerts.append(alert)
                self.alerts.append(alert)
                
                logger.warning(
                    "performance_alert_triggered",
                    metric=metric_name,
                    severity=alert_severity.value,
                    current_value=current_value,
                    threshold=threshold.warning_threshold
                )
    
    def _get_unresolved_alert(self, metric_name: str) -> Optional[PerformanceAlert]:
        """Get unresolved alert for a metric."""
        for alert in self.alerts:
            if alert.metric_name == metric_name and not alert.resolved:
                return alert
        return None
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert."""
        for alert in self.alerts:
            if alert.id == alert_id and not alert.resolved:
                alert.resolved = True
                alert.resolved_at = time.time()
                logger.info("alert_resolved", alert_id=alert_id, metric=alert.metric_name)
                return True
        return False
    
    async def get_active_alerts(self) -> List[PerformanceAlert]:
        """Get all active (unresolved) alerts."""
        return [alert for alert in self.alerts if not alert.resolved]
    
    async def get_alert_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get alert summary for the specified time period."""
        cutoff_time = time.time() - (hours * 3600)
        
        recent_alerts = [
            alert for alert in self.alerts 
            if alert.timestamp >= cutoff_time
        ]
        
        active_alerts = [alert for alert in recent_alerts if not alert.resolved]
        resolved_alerts = [alert for alert in recent_alerts if alert.resolved]
        
        severity_counts = {}
        for alert in recent_alerts:
            severity = alert.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return {
            "period_hours": hours,
            "total_alerts": len(recent_alerts),
            "active_alerts": len(active_alerts),
            "resolved_alerts": len(resolved_alerts),
            "severity_breakdown": severity_counts,
            "most_common_metric": self._get_most_common_metric(recent_alerts),
            "alerts_by_severity": {
                severity.value: [alert.to_dict() for alert in recent_alerts if alert.severity.value == severity]
                for severity in AlertSeverity
            }
        }
    
    def _get_most_common_metric(self, alerts: List[PerformanceAlert]) -> str:
        """Get the most common metric in alerts."""
        if not alerts:
            return "none"
        
        metric_counts = {}
        for alert in alerts:
            metric = alert.metric_name
            metric_counts[metric] = metric_counts.get(metric, 0) + 1
        
        return max(metric_counts, key=metric_counts.get)
    
    def _calculate_percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile of values."""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = (percentile / 100) * (len(sorted_values) - 1)
        
        if index.is_integer():
            return sorted_values[int(index)]
        else:
            lower = sorted_values[int(index)]
            upper = sorted_values[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    async def start_monitoring(self, interval: int = 60):
        """Start continuous monitoring."""
        if self._monitoring_active:
            logger.warning("monitoring_already_active")
            return
        
        self._monitoring_active = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop(interval))
        logger.info("monitoring_started", interval=interval)
    
    async def stop_monitoring(self):
        """Stop continuous monitoring."""
        if not self._monitoring_active:
            return
        
        self._monitoring_active = False
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
            self._monitoring_task = None
        
        logger.info("monitoring_stopped")
    
    async def _monitoring_loop(self, interval: int):
        """Main monitoring loop."""
        while self._monitoring_active:
            try:
                # Collect metrics
                metrics = await self.collect_metrics()
                
                # Check thresholds and generate alerts
                new_alerts = await self.check_thresholds(metrics)
                
                # Call alert handlers
                for alert in new_alerts:
                    for handler in self.alert_handlers:
                        try:
                            await handler(alert)
                        except Exception as e:
                            logger.error("alert_handler_failed", alert_id=alert.id, error=str(e))
                
                # Sleep until next iteration
                await asyncio.sleep(interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("monitoring_loop_error", error=str(e))
                await asyncio.sleep(60)  # Wait before retrying
    
    async def generate_performance_report(self, hours: int = 24) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        # Collect current metrics
        current_metrics = await self.collect_metrics()
        
        # Get alert summary
        alert_summary = await self.get_alert_summary(hours)
        
        # Get historical trends (simplified)
        trends = await self._calculate_trends(hours)
        
        # Performance recommendations
        recommendations = await self._generate_recommendations(current_metrics, alert_summary)
        
        return {
            "report_period_hours": hours,
            "generated_at": datetime.utcnow().isoformat(),
            "current_metrics": current_metrics,
            "alert_summary": alert_summary,
            "trends": trends,
            "recommendations": recommendations,
            "health_score": current_metrics.get("health", {}).get("health_score", 0)
        }
    
    async def _calculate_trends(self, hours: int) -> Dict[str, Any]:
        """Calculate performance trends (simplified implementation)."""
        # This would typically use historical data
        # For now, return placeholder trends
        return {
            "response_time_trend": "stable",
            "error_rate_trend": "decreasing",
            "cache_hit_rate_trend": "improving",
            "resource_usage_trend": "stable"
        }
    
    async def _generate_recommendations(self, metrics: Dict[str, Any], alert_summary: Dict[str, Any]) -> List[str]:
        """Generate performance recommendations."""
        recommendations = []
        
        # System resource recommendations
        system = metrics.get("system", {})
        if system.get("cpu_percent", 0) > 80:
            recommendations.append("Consider scaling up CPU resources or optimizing CPU-intensive operations")
        
        if system.get("memory_percent", 0) > 80:
            recommendations.append("Monitor memory usage and consider adding more RAM or optimizing memory consumption")
        
        # Performance recommendations
        performance = metrics.get("performance", {})
        if performance.get("p95_response_time_ms", 0) > 200:
            recommendations.append("Investigate slow endpoints and optimize database queries or caching")
        
        if performance.get("error_rate_percent", 0) > 5:
            recommendations.append("Review error logs and fix underlying issues causing high error rates")
        
        # Cache recommendations
        cache = metrics.get("cache", {})
        hit_rate = cache.get("hit_rate_percent", 0)
        if hit_rate < 70:
            recommendations.append("Review caching strategy and increase cache hit rate for better performance")
        
        # Alert-based recommendations
        if alert_summary.get("active_alerts", 0) > 5:
            recommendations.append("Address active performance alerts to improve system stability")
        
        return recommendations


# Alert handlers
class AlertHandler:
    """Built-in alert handlers."""
    
    @staticmethod
    async def log_alert(alert: PerformanceAlert):
        """Log alert to system logs."""
        log_level = "warning" if alert.severity in [AlertSeverity.LOW, AlertSeverity.MEDIUM] else "error"
        logger.log(
            getattr(logger, log_level.upper()),
            "performance_alert",
            alert_id=alert.id,
            severity=alert.severity.value,
            metric=alert.metric_name,
            message=alert.message
        )
    
    @staticmethod
    async def store_alert(alert: PerformanceAlert):
        """Store alert in cache for persistence."""
        alert_key = f"alert:{alert.id}"
        await cache_service.set(alert_key, alert.to_dict(), expire=86400)  # 24 hours
    
    @staticmethod
    async def email_alert(alert: PerformanceAlert):
        """Send email notification for critical alerts (placeholder)."""
        if alert.severity == AlertSeverity.CRITICAL:
            # This would integrate with email service
            logger.critical("critical_alert_notification", alert_id=alert.id, message=alert.message)


# Global monitoring service instance
_monitoring_service: Optional[MonitoringService] = None


def get_monitoring_service() -> MonitoringService:
    """Get global monitoring service instance."""
    global _monitoring_service
    if _monitoring_service is None:
        _monitoring_service = MonitoringService()
        
        # Add default alert handlers
        _monitoring_service.add_alert_handler(AlertHandler.log_alert)
        _monitoring_service.add_alert_handler(AlertHandler.store_alert)
        _monitoring_service.add_alert_handler(AlertHandler.email_alert)
    
    return _monitoring_service


# Background task initialization
async def init_monitoring_service():
    """Initialize monitoring service and start monitoring."""
    service = get_monitoring_service()
    
    # Start monitoring with configured interval
    interval = get_settings().metrics_interval or 60
    await service.start_monitoring(interval)
    
    logger.info("monitoring_service_initialized", interval=interval)


# API endpoints for monitoring data
async def get_metrics_endpoint() -> Dict[str, Any]:
    """Endpoint to get current performance metrics."""
    service = get_monitoring_service()
    return await service.collect_metrics()


async def get_alerts_endpoint() -> Dict[str, Any]:
    """Endpoint to get active alerts."""
    service = get_monitoring_service()
    active_alerts = await service.get_active_alerts()
    
    return {
        "active_alerts": [alert.to_dict() for alert in active_alerts],
        "total_active": len(active_alerts),
        "timestamp": time.time()
    }


async def get_health_endpoint() -> Dict[str, Any]:
    """Enhanced health endpoint with monitoring data."""
    metrics = await get_metrics_endpoint()
    alerts = await get_alerts_endpoint()
    
    # Determine overall health status
    health_score = metrics.get("health", {}).get("health_score", 100)
    active_alerts_count = alerts.get("total_active", 0)
    
    if health_score < 50 or active_alerts_count > 5:
        status = "unhealthy"
    elif health_score < 70 or active_alerts_count > 2:
        status = "degraded"
    else:
        status = "healthy"
    
    return {
        "status": status,
        "health_score": health_score,
        "active_alerts": active_alerts_count,
        "metrics": metrics,
        "timestamp": time.time()
    }


# Cleanup function
async def cleanup_monitoring_service():
    """Cleanup monitoring service."""
    service = get_monitoring_service()
    await service.stop_monitoring()
    logger.info("monitoring_service_cleanup_complete")
