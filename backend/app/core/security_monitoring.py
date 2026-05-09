# Security Monitoring Module for VitaChain
# Tracks security events, failed authentication, and suspicious activities

import structlog
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict, deque
import json
import hashlib
import re

logger = structlog.get_logger("security")

class SecurityMonitor:
    """Monitors security events and detects suspicious activities"""
    
    def __init__(self, failed_auth_threshold: int = 5, 
                 rate_violation_threshold: int = 100,
                 window_minutes: int = 15):
        self.failed_auth_threshold = failed_auth_threshold
        self.rate_violation_threshold = rate_violation_threshold
        self.window_minutes = window_minutes
        
        # Track failed authentication attempts
        self.failed_auth_attempts = defaultdict(list)
        
        # Track API rate violations
        self.api_rate_violations = defaultdict(list)
        
        # Track suspicious patterns
        self.suspicious_patterns = defaultdict(int)
        
        # Security event queue for recent events
        self.recent_events = deque(maxlen=1000)
        
        # Blocked IPs
        self.blocked_ips = set()
        
        # Alert thresholds
        self.alert_cooldown = timedelta(minutes=30)
        self.last_alerts = {}
        
        # NEW: Advanced tracking for suspicious login detection
        self.user_login_patterns = defaultdict(dict)  # Track user behavior baselines
        self.ip_geolocation_cache = {}  # Cache IP location data
        self.device_fingerprints = defaultdict(list)  # Track device patterns
    
    def log_failed_authentication(self, ip: str, user_agent: str, 
                                endpoint: str = None, error_type: str = "invalid_credentials"):
        """Track failed authentication attempts"""
        timestamp = datetime.utcnow()
        event_key = f"{ip}:{user_agent}"
        
        # Add to failed attempts
        self.failed_auth_attempts[event_key].append({
            "timestamp": timestamp,
            "endpoint": endpoint,
            "error_type": error_type
        })
        
        # Clean old attempts outside window
        cutoff_time = timestamp - timedelta(minutes=self.window_minutes)
        self.failed_auth_attempts[event_key] = [
            attempt for attempt in self.failed_auth_attempts[event_key]
            if attempt["timestamp"] > cutoff_time
        ]
        
        # Check if threshold exceeded
        attempt_count = len(self.failed_auth_attempts[event_key])
        
        if attempt_count >= self.failed_auth_threshold:
            self._handle_suspicious_activity(
                "multiple_failed_auth",
                ip=ip,
                user_agent=user_agent,
                attempt_count=attempt_count,
                endpoint=endpoint,
                severity="high"
            )
            
            # Log structured event
            logger.warning("multiple_failed_auth_attempts",
                         ip=ip,
                         user_agent=user_agent,
                         attempt_count=attempt_count,
                         endpoint=endpoint,
                         severity="high")
    
    def log_api_abuse(self, ip: str, endpoint: str, rate_violation: bool = False,
                     request_count: int = 0, window_seconds: int = 60):
        """Track API abuse patterns"""
        timestamp = datetime.utcnow()
        event_key = f"{ip}:{endpoint}"
        
        if rate_violation:
            self.api_rate_violations[event_key].append({
                "timestamp": timestamp,
                "request_count": request_count,
                "window_seconds": window_seconds
            })
            
            # Clean old violations
            cutoff_time = timestamp - timedelta(hours=1)
            self.api_rate_violations[event_key] = [
                violation for violation in self.api_rate_violations[event_key]
                if violation["timestamp"] > cutoff_time
            ]
            
            # Check if threshold exceeded
            violation_count = len(self.api_rate_violations[event_key])
            
            if violation_count >= self.rate_violation_threshold:
                self._handle_suspicious_activity(
                    "api_rate_limit_violation",
                    ip=ip,
                    endpoint=endpoint,
                    violation_count=violation_count,
                    request_count=request_count,
                    severity="medium"
                )
                
                logger.warning("api_rate_limit_violation",
                             ip=ip,
                             endpoint=endpoint,
                             violation_count=violation_count,
                             request_count=request_count,
                             severity="medium")
    
    def log_suspicious_request(self, ip: str, user_agent: str, 
                              request_path: str, suspicious_pattern: str,
                              request_data: Dict[str, Any] = None):
        """Log suspicious request patterns"""
        self.suspicious_patterns[suspicious_pattern] += 1
        
        self._handle_suspicious_activity(
            "suspicious_request_pattern",
            ip=ip,
            user_agent=user_agent,
            request_path=request_path,
            pattern=suspicious_pattern,
            severity="medium"
        )
        
        logger.info("suspicious_request_pattern",
                   ip=ip,
                   user_agent=user_agent,
                   request_path=request_path,
                   pattern=suspicious_pattern,
                   severity="medium")
    
    def log_security_event(self, event_type: str, severity: str, **kwargs):
        """Log general security events"""
        timestamp = datetime.utcnow()
        
        event = {
            "timestamp": timestamp.isoformat(),
            "event_type": event_type,
            "severity": severity,
            **kwargs
        }
        
        # Add to recent events
        self.recent_events.append(event)
        
        # Log structured event
        log_level = "warning" if severity == "high" else "info"
        getattr(logger, log_level)("security_event",
                                  event_type=event_type,
                                  severity=severity,
                                  timestamp=timestamp.isoformat(),
                                  **kwargs)
    
    def _handle_suspicious_activity(self, activity_type: str, severity: str, **kwargs):
        """Handle suspicious activity detection"""
        ip = kwargs.get("ip", "unknown")
        
        # Check if we should send alert (cooldown period)
        alert_key = f"{activity_type}:{ip}"
        now = datetime.utcnow()
        
        if (alert_key not in self.last_alerts or 
            now - self.last_alerts[alert_key] > self.alert_cooldown):
            
            self._send_security_alert(activity_type, severity, **kwargs)
            self.last_alerts[alert_key] = now
            
            # Consider blocking for high severity
            if severity == "high" and activity_type in ["multiple_failed_auth"]:
                self.block_ip_temporarily(ip, hours=1)
    
    def _send_security_alert(self, activity_type: str, severity: str, **kwargs):
        """Send security alert (placeholder implementation)"""
        alert_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "activity_type": activity_type,
            "severity": severity,
            **kwargs
        }
        
        # Log alert
        logger.error("security_alert",
                    activity_type=activity_type,
                    severity=severity,
                    **kwargs)
        
        # In production, this would send to:
        # - Email notification
        # - Slack webhook
        # - SIEM system
        # - Security dashboard
        pass
    
    def block_ip_temporarily(self, ip: str, hours: int = 1):
        """Temporarily block an IP address"""
        self.blocked_ips.add(ip)
        
        # In production, this would update firewall rules
        # or use rate limiting to block the IP
        logger.warning("ip_blocked_temporarily",
                      ip=ip,
                      duration_hours=hours,
                      severity="high")
    
    def is_ip_blocked(self, ip: str) -> bool:
        """Check if an IP is currently blocked"""
        return ip in self.blocked_ips
    
    def get_security_metrics(self) -> Dict[str, Any]:
        """Get current security metrics"""
        now = datetime.utcnow()
        cutoff_time = now - timedelta(hours=24)
        
        # Count events in last 24 hours
        recent_failed_auth = 0
        recent_rate_violations = 0
        recent_suspicious_patterns = 0
        
        for event in self.recent_events:
            event_time = datetime.fromisoformat(event["timestamp"])
            if event_time > cutoff_time:
                if event["event_type"] == "multiple_failed_auth":
                    recent_failed_auth += 1
                elif event["event_type"] == "api_rate_limit_violation":
                    recent_rate_violations += 1
                elif event["event_type"] == "suspicious_request_pattern":
                    recent_suspicious_patterns += 1
        
        return {
            "failed_auth_attempts_24h": recent_failed_auth,
            "rate_violations_24h": recent_rate_violations,
            "suspicious_patterns_24h": recent_suspicious_patterns,
            "currently_blocked_ips": len(self.blocked_ips),
            "active_failed_auth_sessions": len(self.failed_auth_attempts),
            "active_rate_violations": len(self.api_rate_violations),
            "top_suspicious_patterns": dict(
                sorted(self.suspicious_patterns.items(), 
                      key=lambda x: x[1], reverse=True)[:10]
            )
        }
    
    def get_ip_reputation(self, ip: str) -> Dict[str, Any]:
        """Get reputation score for an IP address"""
        failed_attempts = 0
        rate_violations = 0
        
        # Check failed auth attempts
        for key, attempts in self.failed_auth_attempts.items():
            if key.startswith(f"{ip}:"):
                failed_attempts += len(attempts)
        
        # Check rate violations
        for key, violations in self.api_rate_violations.items():
            if key.startswith(f"{ip}:"):
                rate_violations += len(violations)
        
        # Calculate reputation score (0-100, higher is better)
        score = 100
        score -= min(failed_attempts * 10, 50)  # Max 50 points deduction
        score -= min(rate_violations * 5, 30)   # Max 30 points deduction
        
        if ip in self.blocked_ips:
            score = 0
        
        reputation = "good"
        if score < 30:
            reputation = "poor"
        elif score < 70:
            reputation = "suspicious"
        
        return {
            "ip": ip,
            "reputation_score": max(0, score),
            "reputation": reputation,
            "failed_auth_attempts": failed_attempts,
            "rate_violations": rate_violations,
            "is_blocked": ip in self.blocked_ips
        }
    
    def analyze_login_attempt(self, user_id: str, ip: str, user_agent: str, 
                           success: bool = False, location_data: dict = None) -> Dict[str, Any]:
        """
        Analyze login attempt for suspicious patterns
        
        Args:
            user_id: User ID attempting login
            ip: Source IP address
            user_agent: Browser user agent string
            success: Whether login was successful
            location_data: Optional geolocation data for IP
            
        Returns:
            Analysis results with risk score and recommendations
        """
        timestamp = datetime.utcnow()
        analysis_result = {
            "timestamp": timestamp,
            "user_id": user_id,
            "ip": ip,
            "user_agent": user_agent,
            "success": success,
            "risk_score": 0,
            "anomalies": [],
            "recommendations": [],
            "should_block": False,
            "should_notify": False
        }
        
        # 1. Check if IP is already blocked
        if self.is_ip_blocked(ip):
            analysis_result["risk_score"] = 100
            analysis_result["anomalies"].append("blocked_ip_attempt")
            analysis_result["should_block"] = True
            return analysis_result
        
        # 2. Geographic anomaly detection
        location_anomaly = self._detect_geographic_anomaly(user_id, ip, location_data)
        if location_anomaly:
            analysis_result["anomalies"].append(location_anomaly)
            analysis_result["risk_score"] += 30
            analysis_result["should_notify"] = True
        
        # 3. Device fingerprinting anomaly
        device_anomaly = self._detect_device_anomaly(user_id, user_agent)
        if device_anomaly:
            analysis_result["anomalies"].append(device_anomaly)
            analysis_result["risk_score"] += 20
            analysis_result["should_notify"] = True
        
        # 4. Velocity anomaly detection
        velocity_anomaly = self._detect_velocity_anomaly(user_id, ip, timestamp)
        if velocity_anomaly:
            analysis_result["anomalies"].append(velocity_anomaly)
            analysis_result["risk_score"] += 25
        
        # 5. Credential stuffing detection
        stuffing_anomaly = self._detect_credential_stuffing(ip, timestamp)
        if stuffing_anomaly:
            analysis_result["anomalies"].append(stuffing_anomaly)
            analysis_result["risk_score"] += 40
            analysis_result["should_block"] = True
            analysis_result["should_notify"] = True
        
        # 6. Determine final recommendations
        if analysis_result["risk_score"] >= 50:
            analysis_result["recommendations"].append("immediate_block_ip")
        elif analysis_result["risk_score"] >= 30:
            analysis_result["recommendations"].append("additional_verification")
        elif analysis_result["risk_score"] >= 20:
            analysis_result["recommendations"].append("notify_user")
        
        return analysis_result
    
    def _detect_geographic_anomaly(self, user_id: str, ip: str, location_data: dict = None) -> Optional[dict]:
        """Detect unusual geographic login patterns"""
        if not location_data:
            return None
            
        # Get user's typical locations
        user_patterns = self.user_login_patterns.get(user_id, {})
        typical_countries = user_patterns.get("countries", [])
        typical_cities = user_patterns.get("cities", [])
        
        current_country = location_data.get("country_code")
        current_city = location_data.get("city")
        
        # Check for new country
        if typical_countries and current_country not in typical_countries:
            return {
                "type": "new_country",
                "country": current_country,
                "previous_countries": typical_countries
            }
        
        # Check for impossible travel (too fast between distant locations)
        last_login = user_patterns.get("last_location")
        if last_login and self._is_impossible_travel(last_login, location_data):
            return {
                "type": "impossible_travel",
                "from": last_login,
                "to": location_data,
                "time_diff_hours": self._calculate_travel_time(last_login, location_data)
            }
        
        return None
    
    def _detect_device_anomaly(self, user_id: str, user_agent: str) -> Optional[dict]:
        """Detect unusual device/browser patterns"""
        device_fingerprint = self._generate_device_fingerprint(user_agent)
        
        # Get user's typical devices
        user_patterns = self.user_login_patterns.get(user_id, {})
        typical_devices = user_patterns.get("devices", [])
        
        if typical_devices and device_fingerprint not in typical_devices:
            return {
                "type": "new_device",
                "device": device_fingerprint,
                "previous_devices": typical_devices
            }
        
        return None
    
    def _detect_velocity_anomaly(self, user_id: str, ip: str, timestamp: datetime) -> Optional[dict]:
        """Detect unusual login frequency patterns"""
        user_patterns = self.user_login_patterns.get(user_id, {})
        recent_logins = user_patterns.get("recent_logins", [])
        
        # Filter logins in last 24 hours
        cutoff = timestamp - timedelta(hours=24)
        recent_logins = [login for login in recent_logins if login > cutoff]
        
        if len(recent_logins) > 10:  # More than 10 logins in 24 hours
            return {
                "type": "high_velocity",
                "count_24h": len(recent_logins),
                "threshold": 10
            }
        
        # Check for rapid successive logins
        if len(recent_logins) >= 3:
            time_diff = (timestamp - recent_logins[-1]).total_seconds() / 60  # minutes
            if time_diff < 5:  # 3+ logins within 5 minutes
                return {
                    "type": "rapid_succession",
                    "count": len(recent_logins),
                    "timeframe_minutes": 5
                }
        
        return None
    
    def _detect_credential_stuffing(self, ip: str, timestamp: datetime) -> Optional[dict]:
        """Detect credential stuffing patterns (many accounts from same IP)"""
        # Count unique accounts targeted by this IP in recent time
        unique_accounts = set()
        recent_events = [event for event in self.recent_events 
                       if event.get("ip") == ip 
                       and event.get("timestamp") > timestamp - timedelta(minutes=5)]
        
        for event in recent_events:
            if event.get("user_id"):
                unique_accounts.add(event["user_id"])
        
        if len(unique_accounts) >= 10:  # 10+ different accounts in 5 minutes
            return {
                "type": "credential_stuffing",
                "unique_accounts": len(unique_accounts),
                "timeframe_minutes": 5
            }
        
        return None
    
    def _generate_device_fingerprint(self, user_agent: str) -> str:
        """Generate a device fingerprint from user agent"""
        if not user_agent:
            return "unknown"
        
        # Extract browser and OS info
        browser = "unknown"
        os = "unknown"
        
        if "Chrome" in user_agent:
            browser = "chrome"
        elif "Firefox" in user_agent:
            browser = "firefox"
        elif "Safari" in user_agent:
            browser = "safari"
        elif "Edge" in user_agent:
            browser = "edge"
        
        if "Windows" in user_agent:
            os = "windows"
        elif "Mac" in user_agent:
            os = "mac"
        elif "Linux" in user_agent:
            os = "linux"
        elif "Android" in user_agent:
            os = "android"
        elif "iOS" in user_agent:
            os = "ios"
        
        # Create simple fingerprint hash
        fingerprint_data = f"{browser}:{os}"
        return hashlib.md5(fingerprint_data.encode()).hexdigest()[:16]
    
    def _is_impossible_travel(self, last_location: dict, current_location: dict) -> bool:
        """Check if travel between locations is impossible"""
        if not last_location or not current_location:
            return False
        
        # Simple distance/time check (simplified)
        # In production, use proper geodesic calculations
        last_country = last_location.get("country_code")
        current_country = current_location.get("country_code")
        
        # If different continents, require more time
        if last_country != current_country:
            return True  # Simplified: always flag international travel as suspicious
        
        return False
    
    def _calculate_travel_time(self, last_location: dict, current_location: dict) -> float:
        """Calculate hours between locations (simplified)"""
        # In production, use proper geodesic distance calculations
        return 1.0  # Placeholder
    
    def update_user_login_pattern(self, user_id: str, ip: str, user_agent: str, 
                              location_data: dict = None, success: bool = True):
        """Update user's baseline login patterns"""
        if user_id not in self.user_login_patterns:
            self.user_login_patterns[user_id] = {
                "countries": [],
                "cities": [],
                "devices": [],
                "recent_logins": [],
                "last_location": None
            }
        
        patterns = self.user_login_patterns[user_id]
        timestamp = datetime.utcnow()
        
        # Update location patterns
        if location_data and success:
            country = location_data.get("country_code")
            city = location_data.get("city")
            
            if country and country not in patterns["countries"]:
                patterns["countries"].append(country)
            if city and city not in patterns["cities"]:
                patterns["cities"].append(city)
            
            patterns["last_location"] = location_data
        
        # Update device patterns
        if success and user_agent:
            device_fingerprint = self._generate_device_fingerprint(user_agent)
            if device_fingerprint not in patterns["devices"]:
                patterns["devices"].append(device_fingerprint)
        
        # Update recent logins
        patterns["recent_logins"].append(timestamp)
        
        # Keep only last 30 days of logins
        cutoff = timestamp - timedelta(days=30)
        patterns["recent_logins"] = [
            login for login in patterns["recent_logins"] if login > cutoff
        ]
    
    def cleanup_old_data(self):
        """Clean up old monitoring data"""
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        # Clean failed auth attempts
        for key in list(self.failed_auth_attempts.keys()):
            self.failed_auth_attempts[key] = [
                attempt for attempt in self.failed_auth_attempts[key]
                if attempt["timestamp"] > cutoff_time
            ]
            if not self.failed_auth_attempts[key]:
                del self.failed_auth_attempts[key]
        
        # Clean rate violations
        for key in list(self.api_rate_violations.keys()):
            self.api_rate_violations[key] = [
                violation for violation in self.api_rate_violations[key]
                if violation["timestamp"] > cutoff_time
            ]
            if not self.api_rate_violations[key]:
                del self.api_rate_violations[key]
        
        logger.info("security_monitor_cleanup_completed")

# Global security monitor instance
security_monitor = SecurityMonitor()
