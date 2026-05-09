"""
Configuration management for Account Blocking functionality
"""

import os
from typing import Dict, Any
from pydantic import field_validator
from pydantic_settings import BaseSettings

class AccountBlockingConfig(BaseSettings):
    """Configuration settings for account blocking"""
    
    # Default block durations (in hours)
    DEFAULT_BLOCK_DURATION: int = 24
    MIN_BLOCK_DURATION: int = 1
    MAX_BLOCK_DURATION: int = 8760  # 1 year
    
    # Auto-blocking thresholds
    AUTO_BLOCK_THRESHOLD: int = 5  # Number of violations before auto-block
    AUTO_BLOCK_DURATION: int = 24  # Default duration for auto-blocks
    
    # Rate limiting
    MAX_BLOCKS_PER_HOUR: int = 10
    MAX_BLOCKS_PER_DAY: int = 50
    
    # Security settings
    MAX_REASON_LENGTH: int = 500
    BLOCK_REASON_BLACKLIST: list = [
        "script", "javascript", "eval", "alert", "prompt", 
        "confirm", "document", "window", "location", "href"
    ]
    
    # Cache settings
    BLOCK_STATUS_CACHE_TTL: int = 300  # 5 minutes
    ENABLE_BLOCK_STATUS_CACHE: bool = True
    
    # Notification settings
    ENABLE_BLOCK_NOTIFICATIONS: bool = True
    ENABLE_UNBLOCK_NOTIFICATIONS: bool = True
    NOTIFICATION_RETRY_ATTEMPTS: int = 3
    
    # Cleanup settings
    CLEANUP_INTERVAL_HOURS: int = 1
    BATCH_CLEANUP_SIZE: int = 100
    
    @field_validator('DEFAULT_BLOCK_DURATION')
    @classmethod
    def validate_default_duration(cls, v):
        if v < 1 or v > 8760:
            raise ValueError(f'DEFAULT_BLOCK_DURATION must be between 1 and 8760')
        return v
    
    @field_validator('MAX_BLOCK_DURATION')
    @classmethod
    def validate_max_duration(cls, v):
        if v < 1:
            raise ValueError('MAX_BLOCK_DURATION must be greater than 1')
        return v
    
    @field_validator('AUTO_BLOCK_THRESHOLD')
    @classmethod
    def validate_auto_threshold(cls, v):
        if v < 1:
            raise ValueError('AUTO_BLOCK_THRESHOLD must be at least 1')
        return v
    
    @field_validator('BLOCK_REASON_BLACKLIST')
    @classmethod
    def validate_blacklist(cls, v):
        if not isinstance(v, list):
            raise ValueError('BLOCK_REASON_BLACKLIST must be a list')
        return [item.lower() for item in v]
    
    @classmethod
    def get_env_config(cls) -> Dict[str, Any]:
        """Get configuration from environment variables"""
        return {
            'DEFAULT_BLOCK_DURATION': int(os.getenv('BLOCK_DEFAULT_DURATION_HOURS', '24')),
            'MIN_BLOCK_DURATION': int(os.getenv('BLOCK_MIN_DURATION_HOURS', '1')),
            'MAX_BLOCK_DURATION': int(os.getenv('BLOCK_MAX_DURATION_HOURS', '8760')),
            'AUTO_BLOCK_THRESHOLD': int(os.getenv('BLOCK_AUTO_THRESHOLD', '5')),
            'AUTO_BLOCK_DURATION': int(os.getenv('BLOCK_AUTO_DURATION_HOURS', '24')),
            'MAX_BLOCKS_PER_HOUR': int(os.getenv('BLOCK_MAX_PER_HOUR', '10')),
            'MAX_BLOCKS_PER_DAY': int(os.getenv('BLOCK_MAX_PER_DAY', '50')),
            'MAX_REASON_LENGTH': int(os.getenv('BLOCK_MAX_REASON_LENGTH', '500')),
            'BLOCK_STATUS_CACHE_TTL': int(os.getenv('BLOCK_CACHE_TTL_SECONDS', '300')),
            'ENABLE_BLOCK_STATUS_CACHE': os.getenv('BLOCK_ENABLE_CACHE', 'true').lower() == 'true',
            'ENABLE_BLOCK_NOTIFICATIONS': os.getenv('BLOCK_ENABLE_NOTIFICATIONS', 'true').lower() == 'true',
            'ENABLE_UNBLOCK_NOTIFICATIONS': os.getenv('BLOCK_ENABLE_UNBLOCK_NOTIFICATIONS', 'true').lower() == 'true',
            'NOTIFICATION_RETRY_ATTEMPTS': int(os.getenv('BLOCK_NOTIFICATION_RETRY_ATTEMPTS', '3')),
            'CLEANUP_INTERVAL_HOURS': int(os.getenv('BLOCK_CLEANUP_INTERVAL_HOURS', '1')),
            'BATCH_CLEANUP_SIZE': int(os.getenv('BLOCK_BATCH_CLEANUP_SIZE', '100')),
        }
    
    @classmethod
    def create_from_env(cls) -> 'AccountBlockingConfig':
        """Create configuration instance from environment variables"""
        env_config = cls.get_env_config()
        return cls(**env_config)
    
    def validate_block_duration(self, duration: int) -> bool:
        """Validate if block duration is within allowed limits"""
        return self.MIN_BLOCK_DURATION <= duration <= self.MAX_BLOCK_DURATION
    
    def validate_block_reason(self, reason: str) -> tuple[bool, str]:
        """Validate block reason for security and length"""
        if not reason or not reason.strip():
            return False, "Block reason cannot be empty"
        
        if len(reason) > self.MAX_REASON_LENGTH:
            return False, f"Block reason exceeds maximum length of {self.MAX_REASON_LENGTH} characters"
        
        # Check for blacklisted content
        reason_lower = reason.lower()
        for blacklisted_term in self.BLOCK_REASON_BLACKLIST:
            if blacklisted_term in reason_lower:
                return False, f"Block reason contains prohibited content: {blacklisted_term}"
        
        return True, "Valid"
    
    def get_default_duration(self, is_auto_block: bool = False) -> int:
        """Get default block duration based on block type"""
        if is_auto_block:
            return self.AUTO_BLOCK_DURATION
        return self.DEFAULT_BLOCK_DURATION
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'default_block_duration': self.DEFAULT_BLOCK_DURATION,
            'min_block_duration': self.MIN_BLOCK_DURATION,
            'max_block_duration': self.MAX_BLOCK_DURATION,
            'auto_block_threshold': self.AUTO_BLOCK_THRESHOLD,
            'auto_block_duration': self.AUTO_BLOCK_DURATION,
            'max_blocks_per_hour': self.MAX_BLOCKS_PER_HOUR,
            'max_blocks_per_day': self.MAX_BLOCKS_PER_DAY,
            'max_reason_length': self.MAX_REASON_LENGTH,
            'block_status_cache_ttl': self.BLOCK_STATUS_CACHE_TTL,
            'enable_block_status_cache': self.ENABLE_BLOCK_STATUS_CACHE,
            'enable_block_notifications': self.ENABLE_BLOCK_NOTIFICATIONS,
            'enable_unblock_notifications': self.ENABLE_UNBLOCK_NOTIFICATIONS,
            'notification_retry_attempts': self.NOTIFICATION_RETRY_ATTEMPTS,
            'cleanup_interval_hours': self.CLEANUP_INTERVAL_HOURS,
            'batch_cleanup_size': self.BATCH_CLEANUP_SIZE,
        }

# Global configuration instance
account_blocking_config = AccountBlockingConfig.create_from_env()
