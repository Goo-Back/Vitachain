# IP Geolocation Service for VitaChain
# Provides IP geolocation lookup and caching for security monitoring

import structlog
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import httpx
import json

logger = structlog.get_logger("geo_ip")

class GeoIPService:
    """Service for IP geolocation lookup and caching"""
    
    def __init__(self, api_key: str = None, cache_ttl_hours: int = 24):
        self.api_key = api_key
        self.cache_ttl = timedelta(hours=cache_ttl_hours)
        self.cache = {}  # Simple in-memory cache
        
        # In production, use Redis or similar for distributed caching
        # For now, using in-memory cache for simplicity
    
    async def get_ip_location(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """
        Get geolocation information for an IP address
        
        Args:
            ip_address: IP address to lookup
            
        Returns:
            Geolocation data or None if lookup fails
        """
        # Check cache first
        cached_data = self._get_from_cache(ip_address)
        if cached_data:
            logger.debug("ip_location_cache_hit", ip=ip_address)
            return cached_data
        
        # Perform lookup
        location_data = await self._lookup_ip_location(ip_address)
        
        if location_data:
            self._store_in_cache(ip_address, location_data)
            logger.info("ip_location_lookup_success", 
                       ip=ip_address, 
                       country=location_data.get("country_code"),
                       city=location_data.get("city"))
        else:
            logger.warning("ip_location_lookup_failed", ip=ip_address)
        
        return location_data
    
    def _get_from_cache(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """Get location data from cache"""
        cached_item = self.cache.get(ip_address)
        if cached_item:
            # Check if cache is still valid
            if datetime.utcnow() - cached_item["timestamp"] < self.cache_ttl:
                return cached_item["data"]
            else:
                # Remove expired cache entry
                del self.cache[ip_address]
        
        return None
    
    def _store_in_cache(self, ip_address: str, location_data: Dict[str, Any]):
        """Store location data in cache"""
        self.cache[ip_address] = {
            "data": location_data,
            "timestamp": datetime.utcnow()
        }
    
    async def _lookup_ip_location(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """
        Perform actual IP geolocation lookup
        
        Uses free IP-API.co service (or similar)
        In production, configure with paid service for better accuracy
        """
        try:
            if self.api_key:
                # Use paid service if API key provided
                url = f"http://ip-api.com/json/{ip_address}?key={self.api_key}"
            else:
                # Use free service
                url = f"http://ip-api.com/json/{ip_address}"
            
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Standardize the response format
                    return {
                        "ip_address": ip_address,
                        "country_code": data.get("countryCode", ""),
                        "country_name": data.get("countryName", ""),
                        "city": data.get("city", ""),
                        "region": data.get("regionName", ""),
                        "latitude": data.get("lat"),
                        "longitude": data.get("lon"),
                        "isp": data.get("isp", ""),
                        "is_proxy": data.get("proxy", False),
                        "lookup_timestamp": datetime.utcnow().isoformat()
                    }
                else:
                    logger.error("ip_api_error", 
                               ip=ip_address, 
                               status_code=response.status_code,
                               error=response.text)
                    return None
                    
        except httpx.RequestError as e:
            logger.error("ip_lookup_request_error", 
                       ip=ip_address, 
                       error=str(e))
            return None
        except Exception as e:
            logger.error("ip_lookup_unexpected_error", 
                       ip=ip_address, 
                       error=str(e))
            return None
    
    def is_high_risk_country(self, country_code: str) -> bool:
        """
        Determine if country is considered high risk
        
        Args:
            country_code: ISO country code
            
        Returns:
            True if country is considered high risk
        """
        # List of countries commonly associated with higher fraud/attack rates
        # This is a simplified approach - in production, use threat intelligence feeds
        high_risk_countries = {
            "CN",  # China
            "RU",  # Russia
            "IR",  # Iran
            "KP",  # North Korea
            "PK",  # Pakistan
            "NG",  # Nigeria
            "GH",  # Ghana
            "CI",  # Côte d'Ivoire
        }
        
        return country_code.upper() in high_risk_countries
    
    def get_risk_score_for_location(self, location_data: Dict[str, Any]) -> int:
        """
        Calculate risk score based on location data
        
        Args:
            location_data: Geolocation data from IP lookup
            
        Returns:
            Risk score (0-100, higher is more risky)
        """
        risk_score = 0
        
        # Check for high-risk country
        country_code = location_data.get("country_code", "")
        if self.is_high_risk_country(country_code):
            risk_score += 30
        
        # Check for proxy/VPN usage
        if location_data.get("is_proxy", False):
            risk_score += 20
        
        # Check for hosting provider (data centers)
        isp = location_data.get("isp", "").lower()
        hosting_providers = ["amazon", "google", "microsoft", "digitalocean", "vultr", "linode"]
        if any(provider in isp for provider in hosting_providers):
            risk_score += 15
        
        # Check for missing location data
        if not location_data.get("country_code"):
            risk_score += 10
        
        return min(risk_score, 100)
    
    def clear_cache(self):
        """Clear the geolocation cache"""
        self.cache.clear()
        logger.info("ip_location_cache_cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for monitoring"""
        return {
            "cache_size": len(self.cache),
            "cache_ttl_hours": self.cache_ttl.total_seconds() / 3600,
            "oldest_entry": min(
                [item["timestamp"] for item in self.cache.values()]
            ) if self.cache else None,
            "newest_entry": max(
                [item["timestamp"] for item in self.cache.values()]
            ) if self.cache else None
        }

# Global instance
geo_ip_service = GeoIPService()
