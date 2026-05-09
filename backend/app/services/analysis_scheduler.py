"""
Analysis Scheduler Service for KATARA Automatic AI Analysis
Handles background job scheduling for periodic optimization analysis
"""

import asyncio
from datetime import datetime, time, timedelta
from typing import Dict, Any, List
import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.services.auto_analysis_service import get_auto_analysis_service
from app.core.database import get_supabase_client
from app.core.logging import get_logger
from app.core.auto_analysis_config import AutoAnalysisConfig

logger = get_logger(__name__)


class AnalysisScheduler:
    """Scheduler for periodic AI analysis jobs"""
    
    def __init__(self, supabase_client):
        self.supabase = supabase_client
        self.auto_analysis_service = get_auto_analysis_service(supabase_client)
        self.logger = get_logger(f"{__name__}.AnalysisScheduler")
        self.scheduler = AsyncIOScheduler()
        self._setup_jobs()
    
    def _setup_jobs(self):
        """Setup scheduled jobs for automatic analysis"""
        
        # Daily periodic analysis at configured hour
        self.scheduler.add_job(
            func=self.periodic_optimization_analysis,
            trigger=CronTrigger(hour=AutoAnalysisConfig.DAILY_ANALYSIS_HOUR, minute=0),
            id="daily_periodic_analysis",
            name="Daily Periodic AI Analysis",
            replace_existing=True,
            max_instances=1  # Prevent overlapping executions
        )
        
        # Hourly check for devices that need immediate analysis
        self.scheduler.add_job(
            func=self.check_immediate_analysis_needs,
            trigger=IntervalTrigger(hours=AutoAnalysisConfig.HOURLY_CHECK_INTERVAL),
            id="hourly_immediate_check",
            name="Hourly Immediate Analysis Check",
            replace_existing=True,
            max_instances=1
        )
        
        # Cleanup old analysis data (weekly)
        self.scheduler.add_job(
            func=self.cleanup_old_analysis_data,
            trigger=CronTrigger(day_of_week=0, hour=3, minute=0),  # Sunday 3 AM UTC
            id="weekly_cleanup",
            name="Weekly Analysis Data Cleanup",
            replace_existing=True,
            max_instances=1
        )
        
        self.logger.info("analysis_scheduler_jobs_configured", jobs_count=len(self.scheduler.get_jobs()))
    
    async def start(self):
        """Start the scheduler"""
        try:
            self.scheduler.start()
            self.logger.info("analysis_scheduler_started")
        except Exception as e:
            self.logger.error("analysis_scheduler_start_failed", error=str(e))
            raise
    
    async def stop(self):
        """Stop the scheduler"""
        try:
            self.scheduler.shutdown(wait=True)
            self.logger.info("analysis_scheduler_stopped")
        except Exception as e:
            self.logger.error("analysis_scheduler_stop_failed", error=str(e))
    
    async def periodic_optimization_analysis(self):
        """
        Perform periodic AI analysis for devices without critical conditions
        This runs daily at 2 AM UTC
        """
        start_time = datetime.utcnow()
        analysis_count = 0
        success_count = 0
        error_count = 0
        
        try:
            self.logger.info("periodic_analysis_started", start_time=start_time.isoformat())
            
            # Get devices due for periodic analysis
            devices = await self.auto_analysis_service.get_devices_due_for_periodic_analysis()
            
            if not devices:
                self.logger.info("no_devices_due_for_periodic_analysis")
                return
            
            self.logger.info("devices_found_for_analysis", device_count=len(devices))
            
            # Process each device
            for device in devices:
                try:
                    device_id = device["device_id"]
                    farmer_id = device["farmer_id"]
                    
                    # Get latest telemetry for the device
                    latest_telemetry = await self._get_latest_telemetry(device_id)
                    
                    if not latest_telemetry:
                        self.logger.warning("no_telemetry_for_device", device_id=device_id)
                        continue
                    
                    # Trigger periodic analysis
                    result = await self.auto_analysis_service.handle_automatic_analysis_trigger(
                        device_id=device_id,
                        farmer_id=device["farmer_id"],
                        telemetry_reading=latest_telemetry,
                        trigger_type="automatic_periodic"
                    )
                    
                    if result:
                        success_count += 1
                        self.logger.info(
                            "periodic_analysis_success",
                            device_id=device_id,
                            analysis_id=result.get("analysis_id")
                        )
                    else:
                        # Analysis was skipped (rate limited, conditions unchanged, etc.)
                        self.logger.info("periodic_analysis_skipped", device_id=device_id)
                    
                    analysis_count += 1
                    
                    # Configurable delay between devices to prevent overwhelming the AI API
                    await asyncio.sleep(AutoAnalysisConfig.DEVICE_DELAY_SECONDS)
                    
                except Exception as e:
                    error_count += 1
                    self.logger.error(
                        "periodic_analysis_device_failed",
                        device_id=device.get("device_id"),
                        error=str(e)
                    )
                    continue
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            self.logger.info(
                "periodic_analysis_completed",
                duration_seconds=duration,
                total_devices=analysis_count,
                successful=success_count,
                errors=error_count
            )
            
        except Exception as e:
            self.logger.error("periodic_analysis_failed", error=str(e))
            raise
    
    async def check_immediate_analysis_needs(self):
        """
        Check for devices that may need immediate analysis due to changing conditions
        This runs hourly
        """
        try:
            self.logger.debug("immediate_analysis_check_started")
            
            # Get devices that have been active in the last hour but haven't had analysis
            devices_needing_check = await self._get_devices_needing_immediate_check()
            
            for device in devices_needing_check:
                try:
                    # Check if conditions have significantly changed
                    latest_telemetry = await self._get_latest_telemetry(device["device_id"])
                    
                    if not latest_telemetry:
                        continue
                    
                    # Let the auto analysis service determine if analysis is needed
                    await self.auto_analysis_service.handle_automatic_analysis_trigger(
                        device_id=device["device_id"],
                        farmer_id=device["farmer_id"],
                        telemetry_reading=latest_telemetry,
                        trigger_type="automatic_periodic"
                    )
                    
                except Exception as e:
                    self.logger.error(
                        "immediate_check_device_failed",
                        device_id=device.get("device_id"),
                        error=str(e)
                    )
                    continue
            
            self.logger.debug("immediate_analysis_check_completed")
            
        except Exception as e:
            self.logger.error("immediate_analysis_check_failed", error=str(e))
    
    async def cleanup_old_analysis_data(self):
        """
        Clean up old analysis data to maintain database performance
        This runs weekly on Sunday at 3 AM UTC
        """
        try:
            self.logger.info("analysis_cleanup_started")
            
            # Delete analysis records older than configured days
            cutoff_date = datetime.utcnow() - timedelta(days=AutoAnalysisConfig.CLEANUP_DAYS_OLD)
            
            result = self.supabase.table("ai_recommendations").delete().lt(
                "created_at", cutoff_date.isoformat()
            ).execute()
            
            deleted_count = len(result.data) if result.data else 0
            
            self.logger.info(
                "analysis_cleanup_completed",
                deleted_records=deleted_count,
                cutoff_date=cutoff_date.isoformat()
            )
            
        except Exception as e:
            self.logger.error("analysis_cleanup_failed", error=str(e))
    
    async def _get_latest_telemetry(self, device_id: str) -> Dict[str, Any]:
        """Get latest telemetry reading for a device"""
        try:
            result = self.supabase.table("telemetry_readings").select(
                "temperature", "humidity", "ndvi", "battery_level", "timestamp"
            ).eq("device_id", device_id).order("timestamp", desc=True).limit(1).execute()
            
            if result.data:
                telemetry = result.data[0]
                return {
                    "temperature": telemetry["temperature"],
                    "humidity": telemetry["humidity"],
                    "ndvi": telemetry["ndvi"],
                    "battery_level": telemetry["battery_level"],
                    "timestamp": telemetry["timestamp"]
                }
            
            return None
            
        except Exception as e:
            self.logger.error("get_latest_telemetry_failed", device_id=device_id, error=str(e))
            return None
    
    async def _get_devices_needing_immediate_check(self) -> List[Dict[str, Any]]:
        """Get devices that may need immediate analysis check"""
        try:
            # Get devices with recent telemetry but no recent analysis
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            
            # This is a simplified query - in production you might want a more sophisticated approach
            result = self.supabase.table("iot_devices").select(
                "device_id", "farmer_id", "auto_analysis_enabled"
            ).eq("auto_analysis_enabled", True).execute()
            
            devices = []
            for device in result.data or []:
                # Check if device has recent telemetry
                recent_telemetry = await self._has_recent_telemetry(device["device_id"], hours=1)
                if recent_telemetry:
                    devices.append(device)
            
            return devices
            
        except Exception as e:
            self.logger.error("get_devices_needing_check_failed", error=str(e))
            return []
    
    async def _has_recent_telemetry(self, device_id: str, hours: int) -> bool:
        """Check if device has recent telemetry data"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            result = self.supabase.table("telemetry_readings").select("id").eq(
                "device_id", device_id
            ).gte("timestamp", cutoff_time.isoformat()).limit(1).execute()
            
            return bool(result.data)
            
        except Exception as e:
            self.logger.error("check_recent_telemetry_failed", device_id=device_id, error=str(e))
            return False
    
    def get_job_status(self) -> Dict[str, Any]:
        """Get status of all scheduled jobs"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger),
                "active": job.active
            })
        
        return {
            "scheduler_running": self.scheduler.running,
            "jobs": jobs,
            "total_jobs": len(jobs)
        }


# Global scheduler instance
_analysis_scheduler: AnalysisScheduler = None


def get_analysis_scheduler() -> AnalysisScheduler:
    """Get the global analysis scheduler instance"""
    global _analysis_scheduler
    if _analysis_scheduler is None:
        supabase = get_supabase_client()
        _analysis_scheduler = AnalysisScheduler(supabase)
    return _analysis_scheduler


async def start_analysis_scheduler():
    """Start the analysis scheduler (call from FastAPI startup)"""
    scheduler = get_analysis_scheduler()
    await scheduler.start()


async def stop_analysis_scheduler():
    """Stop the analysis scheduler (call from FastAPI shutdown)"""
    scheduler = get_analysis_scheduler()
    await scheduler.stop()
