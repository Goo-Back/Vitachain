"""
Custom exceptions for Account Blocking functionality
"""

class AccountBlockingError(Exception):
    """Base exception for account blocking errors"""
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        super().__init__(message)
        self.error_code = error_code or "BLOCKING_ERROR"
        self.details = details or {}

class UserNotFoundError(AccountBlockingError):
    """Raised when user is not found"""
    def __init__(self, user_id: str):
        super().__init__(
            f"User {user_id} not found",
            "USER_NOT_FOUND",
            {"user_id": user_id}
        )

class UserAlreadyBlockedError(AccountBlockingError):
    """Raised when user is already blocked"""
    def __init__(self, user_id: str, blocked_until: str):
        super().__init__(
            f"User {user_id} is already blocked until {blocked_until}",
            "USER_ALREADY_BLOCKED",
            {"user_id": user_id, "blocked_until": blocked_until}
        )

class UserNotBlockedError(AccountBlockingError):
    """Raised when trying to unblock a user that is not blocked"""
    def __init__(self, user_id: str):
        super().__init__(
            f"User {user_id} is not currently blocked",
            "USER_NOT_BLOCKED",
            {"user_id": user_id}
        )

class InvalidBlockDurationError(AccountBlockingError):
    """Raised when block duration is invalid"""
    def __init__(self, duration: int, max_duration: int):
        super().__init__(
            f"Block duration {duration} hours exceeds maximum of {max_duration} hours",
            "INVALID_DURATION",
            {"duration": duration, "max_duration": max_duration}
        )

class InvalidBlockReasonError(AccountBlockingError):
    """Raised when block reason contains invalid content"""
    def __init__(self, reason: str):
        super().__init__(
            "Block reason contains invalid content",
            "INVALID_REASON",
            {"reason": reason}
        )

class InsufficientPermissionError(AccountBlockingError):
    """Raised when user lacks required permissions"""
    def __init__(self, required_permission: str):
        super().__init__(
            f"Insufficient permissions. Required: {required_permission}",
            "INSUFFICIENT_PERMISSIONS",
            {"required_permission": required_permission}
        )

class DatabaseError(AccountBlockingError):
    """Raised when database operation fails"""
    def __init__(self, operation: str, original_error: str):
        super().__init__(
            f"Database error during {operation}",
            "DATABASE_ERROR",
            {"operation": operation, "original_error": original_error}
        )

class NotificationError(AccountBlockingError):
    """Raised when notification sending fails"""
    def __init__(self, notification_type: str, original_error: str):
        super().__init__(
            f"Failed to send {notification_type} notification",
            "NOTIFICATION_ERROR",
            {"notification_type": notification_type, "original_error": original_error}
        )
