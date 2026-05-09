"""
Pydantic schemas for VitaChain API
"""

from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict
from enum import Enum
from typing import Optional
import uuid
import re
from datetime import datetime


class UserRole(str, Enum):
    """User roles for VitaChain platform"""
    FARMER = "FARMER"
    RESTAURANT = "RESTAURANT"
    CITIZEN = "CITIZEN"
    ADMIN = "ADMIN"


class UserRegistrationRequest(BaseModel):
    """Request schema for user registration"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=128, description="User password")
    role: UserRole = Field(..., description="User role")
    full_name: str = Field(..., min_length=2, max_length=100, description="User full name")

    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v):
        if not v.strip():
            raise ValueError('Full name cannot be empty')
        return v.strip()

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if not v.strip():
            raise ValueError('Password cannot be empty')
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v.strip()

    model_config = ConfigDict(use_enum_values=True)


class UserRegistrationResponse(BaseModel):
    """Response schema for successful user registration"""
    message: str = Field(..., description="Success message")
    user_id: uuid.UUID = Field(..., description="New user ID")
    email_sent: bool = Field(..., description="Whether verification email was sent")


class ErrorResponse(BaseModel):
    """Standard error response schema"""
    error: dict = Field(..., description="Error details")


class ValidationErrorDetail(BaseModel):
    """Validation error detail"""
    field: str = Field(..., description="Field that failed validation")
    value: str = Field(..., description="Invalid value provided")
    constraint: str = Field(..., description="Validation constraint that failed")


class ValidationErrorResponse(ErrorResponse):
    """Validation error response with details"""
    error: dict = Field(
        default={
            "code": "VALIDATION_ERROR",
            "message": "Invalid input data",
            "details": {}
        }
    )


class EmailExistsResponse(ErrorResponse):
    """Email already exists error response"""
    error: dict = Field(
        default={
            "code": "EMAIL_EXISTS",
            "message": "Email already registered"
        }
    )


class RateLimitResponse(ErrorResponse):
    """Rate limit exceeded error response"""
    error: dict = Field(
        default={
            "code": "RATE_LIMIT_EXCEEDED",
            "message": "Too many registration attempts. Please try again later."
        }
    )


# Email service schemas
class EmailRequest(BaseModel):
    """Email service request schema"""
    to: list[dict[str, str]] = Field(..., description="List of recipients")
    subject: str = Field(..., description="Email subject")
    html_content: str = Field(..., description="HTML email content")


class VerificationEmailData(BaseModel):
    """Data for verification email template"""
    recipient_email: str
    verification_link: str
    user_name: str
    role: UserRole


# Login schemas
class UserLoginRequest(BaseModel):
    """Request schema for user login"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=1, description="User password")


class UserLoginResponse(BaseModel):
    """Response schema for successful user login"""
    message: str = Field(..., description="Success message")
    user: dict = Field(..., description="User information")
    redirect_to: str = Field(..., description="Dashboard redirect URL")


class InvalidCredentialsResponse(ErrorResponse):
    """Invalid credentials error response"""
    error: dict = Field(
        default={
            "code": "INVALID_CREDENTIALS",
            "message": "Invalid email or password"
        }
    )


class EmailNotVerifiedResponse(ErrorResponse):
    """Email not verified error response"""
    error: dict = Field(
        default={
            "code": "EMAIL_NOT_VERIFIED",
            "message": "Please verify your email before logging in"
        }
    )


# Magic Link Authentication schemas
class MagicLinkRequest(BaseModel):
    """Request schema for magic link authentication"""
    email: EmailStr = Field(..., description="User email address")


class MagicLinkResponse(BaseModel):
    """Response schema for magic link request"""
    message: str = Field(..., description="Success message")
    email_sent: bool = Field(..., description="Whether magic link email was sent")
    expires_in: int = Field(..., description="Token expiry time in seconds")


class MagicLinkVerificationRequest(BaseModel):
    """Request schema for magic link verification"""
    token: str = Field(..., description="Magic link token")


class MagicLinkVerificationResponse(BaseModel):
    """Response schema for successful magic link verification"""
    message: str = Field(..., description="Success message")
    user: dict = Field(..., description="User information")
    redirect_to: str = Field(..., description="Dashboard redirect URL")


class UserNotFoundResponse(ErrorResponse):
    """User not found error response"""
    error: dict = Field(
        default={
            "code": "USER_NOT_FOUND",
            "message": "No account found with this email"
        }
    )


class InvalidMagicLinkResponse(ErrorResponse):
    """Invalid or expired magic link error response"""
    error: dict = Field(
        default={
            "code": "INVALID_MAGIC_LINK",
            "message": "Invalid or expired magic link"
        }
    )


class TokenUsedResponse(ErrorResponse):
    """Magic link already used error response"""
    error: dict = Field(
        default={
            "code": "TOKEN_USED",
            "message": "This magic link has already been used"
        }
    )


class MagicLinkRateLimitResponse(ErrorResponse):
    """Magic link rate limit exceeded error response"""
    error: dict = Field(
        default={
            "code": "RATE_LIMIT_EXCEEDED",
            "message": "Too many magic link requests. Please try again later."
        }
    )


# Email service extension for magic links
class MagicLinkEmailData(BaseModel):
    """Data for magic link email template"""
    recipient_email: str
    magic_link: str
    user_name: str
    role: UserRole
    expires_in_minutes: int = Field(default=15, description="Token expiry time in minutes")


# Password Reset schemas
class PasswordResetRequest(BaseModel):
    """Request schema for password reset"""
    email: EmailStr = Field(..., description="User email address")


class PasswordResetResponse(BaseModel):
    """Response schema for password reset request"""
    message: str = Field(..., description="Success message")
    email_sent: bool = Field(..., description="Whether password reset email was sent")
    expires_in: int = Field(..., description="Token expiry time in seconds")


class PasswordResetConfirmRequest(BaseModel):
    """Request schema for password reset confirmation"""
    new_password: str = Field(..., min_length=8, description="New password")
    confirm_password: str = Field(..., min_length=8, description="Confirm new password")
    token: str = Field(..., description="Password reset token")

    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v, info):
        if 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('Passwords do not match')
        return v


class PasswordResetConfirmResponse(BaseModel):
    """Response schema for successful password reset"""
    message: str = Field(..., description="Success message")
    user_id: uuid.UUID = Field(..., description="User ID")


class PasswordMismatchResponse(ErrorResponse):
    """Password mismatch error response"""
    error: dict = Field(
        default={
            "code": "PASSWORD_MISMATCH",
            "message": "Passwords do not match"
        }
    )


class WeakPasswordResponse(ErrorResponse):
    """Weak password error response"""
    error: dict = Field(
        default={
            "code": "WEAK_PASSWORD",
            "message": "Password must be at least 8 characters with uppercase, lowercase, and numbers"
        }
    )


class InvalidResetTokenResponse(ErrorResponse):
    """Invalid or expired reset token error response"""
    error: dict = Field(
        default={
            "code": "INVALID_RESET_TOKEN",
            "message": "Invalid or expired password reset link"
        }
    )


class PasswordResetRateLimitResponse(ErrorResponse):
    """Password reset rate limit exceeded error response"""
    error: dict = Field(
        default={
            "code": "RATE_LIMIT_EXCEEDED",
            "message": "Too many password reset requests. Please try again later."
        }
    )


# Email service extension for password reset
class PasswordResetEmailData(BaseModel):
    """Data for password reset email template"""
    recipient_email: str
    reset_link: str
    user_name: str
    role: UserRole
    expires_in_hours: int = Field(default=1, description="Token expiry time in hours")


# Profile Management schemas
class ProfileViewResponse(BaseModel):
    """Response schema for profile view"""
    id: uuid.UUID = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    full_name: str = Field(..., description="User full name")
    phone: Optional[str] = Field(None, description="User phone number")
    role: UserRole = Field(..., description="User role")
    created_at: str = Field(..., description="Account creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    role_data: Optional[dict] = Field(None, description="Role-specific data")

    model_config = ConfigDict(use_enum_values=True)


class ProfileUpdateRequest(BaseModel):
    """Request schema for profile update"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=100, description="User full name")
    phone: Optional[str] = Field(None, description="User phone number")
    role_data: Optional[dict] = Field(None, description="Role-specific data")

    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Full name cannot be empty')
        return v.strip() if v else v

    @field_validator('phone')
    @classmethod
    def validate_phone_format(cls, v):
        if v is not None and v.strip():
            # Basic format validation - detailed validation in service
            if not re.match(r'^[\+]?[0-9\s\-\(\)]+$', v):
                raise ValueError('Invalid phone number format')
        return v.strip() if v else v


class ProfileUpdateResponse(BaseModel):
    """Response schema for successful profile update"""
    message: str = Field(..., description="Success message")
    profile: ProfileViewResponse = Field(..., description="Updated profile data")


class ProfileNotFoundResponse(ErrorResponse):
    """Profile not found error response"""
    error: dict = Field(
        default={
            "code": "PROFILE_NOT_FOUND",
            "message": "User profile not found"
        }
    )


class ProfileValidationErrorResponse(ErrorResponse):
    """Profile validation error response"""
    error: dict = Field(
        default={
            "code": "VALIDATION_ERROR",
            "message": "Invalid profile data",
            "details": {}
        }
    )


class ProfileUnauthorizedResponse(ErrorResponse):
    """Profile access unauthorized error response"""
    error: dict = Field(
        default={
            "code": "UNAUTHORIZED",
            "message": "Invalid or missing authentication token"
        }
    )


class ProfileForbiddenResponse(ErrorResponse):
    """Profile access forbidden error response"""
    error: dict = Field(
        default={
            "code": "FORBIDDEN",
            "message": "Access denied to this profile"
        }
    )


# Role-specific profile data schemas
class FarmerProfileData(BaseModel):
    """Farmer-specific profile data"""
    farm_location: Optional[str] = Field(None, description="Farm location")
    farm_size_hectares: Optional[float] = Field(None, ge=0, description="Farm size in hectares")
    main_crops: Optional[list[str]] = Field(None, description="Main crops grown")


class RestaurantProfileData(BaseModel):
    """Restaurant-specific profile data"""
    restaurant_name: Optional[str] = Field(None, description="Restaurant name")
    address: Optional[str] = Field(None, description="Restaurant address")
    cuisine_type: Optional[str] = Field(None, description="Type of cuisine")


class CitizenProfileData(BaseModel):
    """Citizen-specific profile data"""
    preferred_pickup_locations: Optional[list[str]] = Field(None, description="Preferred pickup locations")


# Import regex for phone validation
import re


# Admin User Management schemas
class UserStatus(str, Enum):
    """User account status"""
    ACTIVE = "active"
    BLOCKED = "blocked"
    PENDING = "pending"


class AdminUserView(BaseModel):
    """Admin view of user with extended information"""
    id: uuid.UUID = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    full_name: str = Field(..., description="User full name")
    phone: Optional[str] = Field(None, description="User phone number")
    role: UserRole = Field(..., description="User role")
    account_status: UserStatus = Field(..., description="Account status")
    created_at: str = Field(..., description="Account creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    last_login: Optional[str] = Field(None, description="Last login timestamp")
    devices_count: int = Field(default=0, description="Number of IoT devices")
    listings_count: int = Field(default=0, description="Number of farm listings")
    reservations_count: int = Field(default=0, description="Number of meal reservations")
    orders_count: int = Field(default=0, description="Number of orders")

    model_config = ConfigDict(use_enum_values=True)


class UserStats(BaseModel):
    """User statistics for admin dashboard"""
    total_users: int = Field(..., description="Total number of users")
    active_users: int = Field(..., description="Number of active users")
    blocked_users: int = Field(..., description="Number of blocked users")
    pending_users: int = Field(..., description="Number of pending users")
    users_by_role: dict = Field(..., description="User count by role")
    registrations_today: int = Field(..., description="New registrations today")
    registrations_this_week: int = Field(..., description="New registrations this week")
    registrations_this_month: int = Field(..., description="New registrations this month")


class UserFilters(BaseModel):
    """User search and filter parameters"""
    search: Optional[str] = Field(None, description="Search term for email or name")
    role: Optional[UserRole] = Field(None, description="Filter by role")
    status: Optional[UserStatus] = Field(None, description="Filter by account status")
    date_from: Optional[str] = Field(None, description="Filter users from date")
    date_to: Optional[str] = Field(None, description="Filter users to date")
    page: int = Field(default=1, ge=1, description="Page number")
    limit: int = Field(default=20, ge=1, le=100, description="Items per page")

    model_config = ConfigDict(use_enum_values=True)


class UserStatusUpdateRequest(BaseModel):
    """Request schema for updating user status"""
    new_status: UserStatus = Field(..., description="New account status")
    reason: str = Field(..., min_length=5, max_length=500, description="Reason for status change")

    model_config = ConfigDict(use_enum_values=True)


class UserRoleUpdateRequest(BaseModel):
    """Request schema for updating user role"""
    new_role: UserRole = Field(..., description="New user role")
    reason: str = Field(..., min_length=5, max_length=500, description="Reason for role change")

    model_config = ConfigDict(use_enum_values=True)


class BulkUserUpdateRequest(BaseModel):
    """Request schema for bulk user operations"""
    user_ids: list[uuid.UUID] = Field(..., min_items=1, max_items=100, description="List of user IDs")
    action: str = Field(..., description="Action to perform (update_role, update_status)")
    data: dict = Field(..., description="Action-specific data")


class BulkUserUpdateResponse(BaseModel):
    """Response schema for bulk user operations"""
    message: str = Field(..., description="Operation result message")
    updated_count: int = Field(..., description="Number of successfully updated users")
    failed_count: int = Field(..., description="Number of failed updates")
    results: list[dict] = Field(..., description="Individual operation results")


class UserListResponse(BaseModel):
    """Response schema for user list with pagination"""
    users: list[AdminUserView] = Field(..., description="List of users")
    pagination: dict = Field(..., description="Pagination information")
    stats: UserStats = Field(..., description="User statistics")


class UserExportRequest(BaseModel):
    """Request schema for user data export"""
    format: str = Field(default="csv", pattern="^(csv|excel)$", description="Export format")
    role: Optional[UserRole] = Field(None, description="Filter by role")
    status: Optional[UserStatus] = Field(None, description="Filter by status")
    date_from: Optional[str] = Field(None, description="Filter from date")
    date_to: Optional[str] = Field(None, description="Filter to date")

    model_config = ConfigDict(use_enum_values=True)


class AdminAuditLog(BaseModel):
    """Admin audit log entry"""
    id: uuid.UUID = Field(..., description="Log entry ID")
    admin_id: uuid.UUID = Field(..., description="Admin user ID")
    admin_email: str = Field(..., description="Admin email")
    action: str = Field(..., description="Admin action performed")
    target_user_id: Optional[uuid.UUID] = Field(None, description="Target user ID")
    target_user_email: Optional[str] = Field(None, description="Target user email")
    details: dict = Field(..., description="Action details")
    ip_address: str = Field(..., description="Admin IP address")
    timestamp: str = Field(..., description="Action timestamp")


# Admin error response schemas
class AdminAccessDeniedResponse(ErrorResponse):
    """Admin access denied error response"""
    error: dict = Field(
        default={
            "code": "ADMIN_ACCESS_DENIED",
            "message": "Admin access required for this operation"
        }
    )


class UserNotFoundAdminResponse(ErrorResponse):
    """User not found for admin operations error response"""
    error: dict = Field(
        default={
            "code": "USER_NOT_FOUND",
            "message": "User not found"
        }
    )


class InvalidStatusTransitionResponse(ErrorResponse):
    """Invalid status transition error response"""
    error: dict = Field(
        default={
            "code": "INVALID_STATUS_TRANSITION",
            "message": "Invalid account status transition"
        }
    )


class BulkOperationFailedResponse(ErrorResponse):
    """Bulk operation failed error response"""
    error: dict = Field(
        default={
            "code": "BULK_OPERATION_FAILED",
            "message": "Bulk operation failed for some users"
        }
    )


# KATARA IoT Device schemas
class DeviceCreate(BaseModel):
    """Request schema for device registration"""
    device_id: str = Field(..., pattern=r'^katara-[a-f0-9-]{36}$', description="Device ID in format 'katara-{uuid4}'")
    name: Optional[str] = Field(None, max_length=100, description="Device name (e.g., 'Parcelle Nord')")
    location_lat: Optional[float] = Field(None, ge=-90, le=90, description="Device latitude")
    location_lng: Optional[float] = Field(None, ge=-180, le=180, description="Device longitude")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Device name cannot be empty')
        return v.strip() if v else v

    @field_validator('device_id')
    @classmethod
    def validate_device_id_format(cls, v):
        """Validate device_id follows katara-{uuid4} format"""
        if not v.startswith('katara-'):
            raise ValueError('Device ID must start with "katara-"')
        uuid_part = v[7:]  # Remove 'katara-' prefix
        try:
            uuid.UUID(uuid_part)
        except ValueError:
            raise ValueError('Device ID must contain a valid UUID after "katara-"')
        return v


class DeviceResponse(BaseModel):
    """Response schema for device operations"""
    id: uuid.UUID = Field(..., description="Device database ID")
    device_id: str = Field(..., description="Device unique identifier")
    farmer_id: uuid.UUID = Field(..., description="Owner farmer ID")
    name: Optional[str] = Field(None, description="Device name")
    location_lat: Optional[float] = Field(None, description="Device latitude")
    location_lng: Optional[float] = Field(None, description="Device longitude")
    registered_at: datetime = Field(..., description="Device registration timestamp")


class DeviceListResponse(BaseModel):
    """Response schema for device list"""
    devices: list[DeviceResponse] = Field(..., description="List of devices")
    total: int = Field(..., description="Total number of devices")


# KATARA error response schemas
class DeviceAlreadyExistsResponse(ErrorResponse):
    """Device ID already exists error response"""
    error: dict = Field(
        default={
            "code": "DEVICE_ALREADY_EXISTS",
            "message": "Device with this ID already exists"
        }
    )


class DeviceNotFoundResponse(ErrorResponse):
    """Device not found error response"""
    error: dict = Field(
        default={
            "code": "DEVICE_NOT_FOUND",
            "message": "Device not found"
        }
    )


class DeviceForbiddenResponse(ErrorResponse):
    """Device access forbidden error response"""
    error: dict = Field(
        default={
            "code": "FORBIDDEN",
            "message": "Access denied to this device"
        }
    )


class DeviceValidationErrorResponse(ErrorResponse):
    """Device validation error response"""
    error: dict = Field(
        default={
            "code": "VALIDATION_ERROR",
            "message": "Invalid device data",
            "details": {}
        }
    )


# KATARA Telemetry schemas
class TelemetryCreate(BaseModel):
    """Request schema for telemetry data ingestion"""
    device_id: str = Field(..., pattern=r'^katara-[a-f0-9-]{36}$', description="Device ID in format 'katara-{uuid4}'")
    temperature: float = Field(..., ge=-10, le=60, description="Temperature in Celsius (-10 to 60°C)")
    humidity: float = Field(..., ge=0, le=100, description="Humidity percentage (0 to 100%)")
    ndvi: float = Field(..., ge=-1, le=1, description="NDVI value (-1 to 1)")
    battery_level: Optional[float] = Field(None, ge=0, le=100, description="Battery level percentage (0 to 100%)")
    timestamp: Optional[datetime] = Field(None, description="ISO 8601 timestamp (defaults to current time)")

    @field_validator('device_id')
    @classmethod
    def validate_device_id_format(cls, v):
        """Validate device_id follows katara-{uuid4} format"""
        if not v.startswith('katara-'):
            raise ValueError('Device ID must start with "katara-"')
        uuid_part = v[7:]  # Remove 'katara-' prefix
        try:
            uuid.UUID(uuid_part)
        except ValueError:
            raise ValueError('Device ID must contain a valid UUID after "katara-"')
        return v


class TelemetryResponse(BaseModel):
    """Response schema for successful telemetry ingestion"""
    status: str = Field(default="ok", description="Processing status")
    reading_id: uuid.UUID = Field(..., description="Database ID of the reading")
    farmer_notified: bool = Field(default=False, description="Whether farmer was notified")
    alerts_triggered: int = Field(default=0, description="Number of alerts triggered")
    alert_ids: list[uuid.UUID] = Field(default=[], description="IDs of created alerts")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")


# Telemetry error response schemas
class TelemetryUnauthorizedResponse(ErrorResponse):
    """Telemetry API key authentication failed"""
    error: dict = Field(
        default={
            "code": "UNAUTHORIZED",
            "message": "Invalid or missing API key"
        }
    )


class TelemetryForbiddenResponse(ErrorResponse):
    """Telemetry device access forbidden"""
    error: dict = Field(
        default={
            "code": "FORBIDDEN",
            "message": "Device ID does not match authenticated device"
        }
    )


class TelemetryValidationErrorResponse(ErrorResponse):
    """Telemetry data validation error"""
    error: dict = Field(
        default={
            "code": "VALIDATION_ERROR",
            "message": "Invalid telemetry data",
            "details": {}
        }
    )


class TelemetryDeviceNotFoundResponse(ErrorResponse):
    """Telemetry device not found"""
    error: dict = Field(
        default={
            "code": "DEVICE_NOT_FOUND",
            "message": "Device not found or inactive"
        }
    )


# KATARA Dashboard schemas
class DeviceStatus(str, Enum):
    """Device connection status"""
    ONLINE = "online"
    OFFLINE = "offline"
    UNKNOWN = "unknown"


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CurrentTelemetry(BaseModel):
    """Current telemetry data for a device"""
    temperature: Optional[float] = Field(None, description="Temperature in Celsius")
    humidity: Optional[float] = Field(None, description="Humidity percentage")
    ndvi: Optional[float] = Field(None, description="NDVI value")
    battery_level: Optional[float] = Field(None, description="Battery level percentage")
    timestamp: datetime = Field(..., description="Last telemetry timestamp")


class DashboardDevice(BaseModel):
    """Device information for dashboard"""
    id: uuid.UUID = Field(..., description="Device database ID")
    device_id: str = Field(..., description="Device unique identifier")
    name: Optional[str] = Field(None, description="Device name")
    location_lat: Optional[float] = Field(None, description="Device latitude")
    location_lng: Optional[float] = Field(None, description="Device longitude")
    status: DeviceStatus = Field(..., description="Device connection status")
    last_seen: datetime = Field(..., description="Last time device was seen")
    current_telemetry: Optional[CurrentTelemetry] = Field(None, description="Latest telemetry data")


class SummaryStats(BaseModel):
    """Summary statistics for dashboard"""
    avg_temperature: Optional[float] = Field(None, description="Average temperature across all devices")
    avg_humidity: Optional[float] = Field(None, description="Average humidity across all devices")
    avg_ndvi: Optional[float] = Field(None, description="Average NDVI across all devices")
    total_devices: int = Field(..., description="Total number of devices")
    online_devices: int = Field(..., description="Number of online devices")
    offline_devices: int = Field(..., description="Number of offline devices")


class DashboardAlert(BaseModel):
    """Alert information for dashboard"""
    id: uuid.UUID = Field(..., description="Alert ID")
    type: str = Field(..., description="Alert type")
    severity: AlertSeverity = Field(..., description="Alert severity")
    message: str = Field(..., description="Alert message")
    created_at: datetime = Field(..., description="Alert creation timestamp")

    model_config = ConfigDict(use_enum_values=True)


class AlertsInfo(BaseModel):
    """Alerts information for dashboard"""
    unread_count: int = Field(..., description="Number of unread alerts")
    recent_alerts: list[DashboardAlert] = Field(..., description="Recent alerts")


class TelemetryPoint(BaseModel):
    """Single telemetry data point for trends"""
    device_id: str = Field(..., description="Device ID")
    temperature: Optional[float] = Field(None, description="Temperature")
    humidity: Optional[float] = Field(None, description="Humidity")
    ndvi: Optional[float] = Field(None, description="NDVI")
    timestamp: datetime = Field(..., description="Data timestamp")


class TrendData(BaseModel):
    """Trend data for dashboard charts"""
    last_24_hours: list[TelemetryPoint] = Field(..., description="Last 24 hours of telemetry data")


class DashboardResponse(BaseModel):
    """Complete dashboard response"""
    devices: list[DashboardDevice] = Field(..., description="List of devices with current data")
    summary_stats: SummaryStats = Field(..., description="Summary statistics")
    alerts: AlertsInfo = Field(..., description="Alert information")
    trend_data: TrendData = Field(..., description="Historical trend data")

    model_config = ConfigDict(use_enum_values=True)


# Dashboard error response schemas
class DashboardNotFoundResponse(ErrorResponse):
    """Dashboard data not found"""
    error: dict = Field(
        default={
            "code": "DASHBOARD_NOT_FOUND",
            "message": "Dashboard data not available"
        }
    )


class DashboardAccessDeniedResponse(ErrorResponse):
    """Dashboard access denied"""
    error: dict = Field(
        default={
            "code": "FORBIDDEN",
            "message": "Access denied to dashboard data"
        }
    )


# History Analysis schemas
class HistoryParams(BaseModel):
    """Parameters for history API request"""
    start_date: datetime = Field(..., description="Start date for historical analysis")
    end_date: datetime = Field(..., description="End date for historical analysis")
    device_id: Optional[str] = Field(None, description="Specific device ID to analyze")
    aggregation: str = Field(default="hour", description="Aggregation level (hour, day)")

    @field_validator('aggregation')
    @classmethod
    def validate_aggregation(cls, v):
        if v not in ['hour', 'day']:
            raise ValueError('Aggregation must be either "hour" or "day"')
        return v


class PeriodInfo(BaseModel):
    """Information about the analysis period"""
    start_date: datetime = Field(..., description="Period start date")
    end_date: datetime = Field(..., description="Period end date")
    total_readings: int = Field(..., description="Total readings analyzed")
    devices_analyzed: int = Field(..., description="Number of devices analyzed")


class HourlyData(BaseModel):
    """Hourly aggregated telemetry data"""
    hour_bucket: datetime = Field(..., description="Hour timestamp")
    avg_temp: Optional[float] = Field(None, description="Average temperature")
    min_temp: Optional[float] = Field(None, description="Minimum temperature")
    max_temp: Optional[float] = Field(None, description="Maximum temperature")
    avg_humidity: Optional[float] = Field(None, description="Average humidity")
    avg_ndvi: Optional[float] = Field(None, description="Average NDVI")
    reading_count: int = Field(..., description="Number of readings in this hour")


class DeviceChartData(BaseModel):
    """Chart data for a specific device"""
    device_id: str = Field(..., description="Device ID")
    device_name: Optional[str] = Field(None, description="Device name")
    hourly_data: list[HourlyData] = Field(..., description="Hourly aggregated data")


class DailyStats(BaseModel):
    """Daily statistics for telemetry data"""
    date: str = Field(..., description="Date string")
    avg_temp: Optional[float] = Field(None, description="Average temperature")
    min_temp: Optional[float] = Field(None, description="Minimum temperature")
    max_temp: Optional[float] = Field(None, description="Maximum temperature")
    avg_humidity: Optional[float] = Field(None, description="Average humidity")
    avg_ndvi: Optional[float] = Field(None, description="Average NDVI")
    total_readings: int = Field(..., description="Total readings for the day")


class TrendAnalysis(BaseModel):
    """Trend analysis results"""
    temperature_trend: str = Field(..., description="Temperature trend direction")
    humidity_trend: str = Field(..., description="Humidity trend direction")
    ndvi_trend: str = Field(..., description="NDVI trend direction")
    correlations: dict[str, float] = Field(..., description="Correlation coefficients")


class AlertPattern(BaseModel):
    """Alert pattern information"""
    date: str = Field(..., description="Date")
    high_alerts: int = Field(..., description="Number of high severity alerts")
    medium_alerts: int = Field(..., description="Number of medium severity alerts")
    low_alerts: int = Field(..., description="Number of low severity alerts")
    main_causes: list[str] = Field(..., description="Main causes of alerts")


class HistoryResponse(BaseModel):
    """Complete history analysis response"""
    period_info: PeriodInfo = Field(..., description="Analysis period information")
    chart_data: list[DeviceChartData] = Field(..., description="Chart data for all devices")
    daily_stats: list[DailyStats] = Field(..., description="Daily statistics")
    trend_analysis: TrendAnalysis = Field(..., description="Trend analysis results")
    alert_patterns: list[AlertPattern] = Field(..., description="Alert patterns")

    model_config = ConfigDict(use_enum_values=True)


# History error response schemas
class HistoryNotFoundResponse(ErrorResponse):
    """History data not found"""
    error: dict = Field(
        default={
            "code": "HISTORY_NOT_FOUND",
            "message": "No historical data found for the specified period"
        }
    )


class HistoryAccessDeniedResponse(ErrorResponse):
    """History access denied"""
    error: dict = Field(
        default={
            "code": "FORBIDDEN",
            "message": "Access denied to historical data"
        }
    )


class HistoryValidationErrorResponse(ErrorResponse):
    """History request validation error"""
    error: dict = Field(
        default={
            "code": "VALIDATION_ERROR",
            "message": "Invalid history request parameters",
            "details": {}
        }
    )


# KATARA AI Recommendation schemas
class AnalysisType(str, Enum):
    """AI analysis types"""
    COMPREHENSIVE = "comprehensive"
    IRRIGATION = "irrigation"
    HEALTH = "health"
    SOIL = "soil"


class AIAnalysisRequest(BaseModel):
    """Request schema for AI analysis"""
    start_date: Optional[datetime] = Field(None, description="Analysis start date (ISO 8601)")
    end_date: Optional[datetime] = Field(None, description="Analysis end date (ISO 8601)")
    analysis_type: AnalysisType = Field(default=AnalysisType.COMPREHENSIVE, description="Type of analysis to perform")

    @field_validator('end_date')
    @classmethod
    def validate_date_range(cls, v, values):
        if v and 'start_date' in values and values['start_date']:
            if v <= values['start_date']:
                raise ValueError('End date must be after start date')
        return v

    model_config = ConfigDict(use_enum_values=True)


class AIAnalysisJob(BaseModel):
    """AI analysis job response"""
    analysis_id: uuid.UUID = Field(..., description="Analysis job ID")
    status: str = Field(..., description="Job status (processing, completed, failed)")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")


class RecommendationPriority(str, Enum):
    """Recommendation priority levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RecommendationItem(BaseModel):
    """Individual recommendation item"""
    priority: RecommendationPriority = Field(..., description="Recommendation priority")
    action: str = Field(..., description="Specific actionable recommendation")
    reasoning: str = Field(..., description="Why this action is needed")

    model_config = ConfigDict(use_enum_values=True)


class StructuredRecommendations(BaseModel):
    """Structured AI recommendations"""
    irrigation: Optional[RecommendationItem] = Field(None, description="Irrigation recommendation")
    crop_health: Optional[RecommendationItem] = Field(None, description="Crop health recommendation")
    soil_management: Optional[RecommendationItem] = Field(None, description="Soil management recommendation")
    pest_control: Optional[RecommendationItem] = Field(None, description="Pest control recommendation")


class TelemetrySummary(BaseModel):
    """Aggregated telemetry data summary"""
    avg_temperature: float = Field(..., description="Average temperature")
    avg_humidity: float = Field(..., description="Average humidity")
    ndvi_trend: str = Field(..., description="NDVI trend (increasing/decreasing/stable)")
    data_points: int = Field(..., description="Number of data points analyzed")
    min_temperature: float = Field(..., description="Minimum temperature")
    max_temperature: float = Field(..., description="Maximum temperature")
    min_humidity: float = Field(..., description="Minimum humidity")
    max_humidity: float = Field(..., description="Maximum humidity")


class AIRecommendation(BaseModel):
    """Complete AI recommendation response"""
    id: uuid.UUID = Field(..., description="Recommendation ID")
    device_id: str = Field(..., description="Device ID")
    analysis_period: dict = Field(..., description="Analysis period information")
    telemetry_summary: TelemetrySummary = Field(..., description="Aggregated telemetry data")
    ai_response: str = Field(..., description="Full Claude API response")
    recommendations: StructuredRecommendations = Field(..., description="Structured recommendations")
    confidence_score: float = Field(..., ge=0, le=1, description="AI confidence score")
    created_at: datetime = Field(..., description="Recommendation creation timestamp")


class AIRecommendationsResponse(BaseModel):
    """Response schema for AI recommendations list"""
    recommendations: list[AIRecommendation] = Field(..., description="List of recommendations")
    total: int = Field(..., description="Total number of recommendations")


# AI Recommendation error response schemas
class AIAnalysisTimeoutResponse(ErrorResponse):
    """AI analysis timeout error"""
    error: dict = Field(
        default={
            "code": "AI_ANALYSIS_TIMEOUT",
            "message": "AI analysis timed out after 30 seconds"
        }
    )


class AIAnalysisFailedResponse(ErrorResponse):
    """AI analysis failed error"""
    error: dict = Field(
        default={
            "code": "AI_ANALYSIS_FAILED",
            "message": "AI analysis failed to complete"
        }
    )


class AIRecommendationNotFoundResponse(ErrorResponse):
    """AI recommendation not found"""
    error: dict = Field(
        default={
            "code": "RECOMMENDATION_NOT_FOUND",
            "message": "No recommendations found for this device"
        }
    )


class AIRecommendationForbiddenResponse(ErrorResponse):
    """AI recommendation access forbidden"""
    error: dict = Field(
        default={
            "code": "FORBIDDEN",
            "message": "Access denied to these recommendations"
        }
    )


class AIAnalysisValidationErrorResponse(ErrorResponse):
    """AI analysis validation error"""
    error: dict = Field(
        default={
            "code": "VALIDATION_ERROR",
            "message": "Invalid AI analysis request parameters",
            "details": {}
        }
    )


# Weather Data Schemas
class WeatherLocation(BaseModel):
    """Location coordinates for weather data"""
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lng: float = Field(..., ge=-180, le=180, description="Longitude")


class CurrentWeather(BaseModel):
    """Current weather conditions"""
    temperature: float = Field(..., description="Temperature in Celsius")
    humidity: float = Field(..., ge=0, le=100, description="Humidity percentage")
    pressure: float = Field(..., description="Atmospheric pressure in hPa")
    wind_speed: float = Field(..., ge=0, description="Wind speed in m/s")
    wind_direction: float = Field(..., ge=0, le=360, description="Wind direction in degrees")
    rainfall_1h: float = Field(..., ge=0, description="Rainfall in last 1 hour in mm")
    rainfall_24h: float = Field(..., ge=0, description="Rainfall in last 24 hours in mm")
    weather_main: str = Field(..., description="Main weather condition (Rain, Clear, etc.)")
    weather_description: str = Field(..., description="Detailed weather description")
    visibility: float = Field(..., ge=0, description="Visibility in km")
    uv_index: Optional[float] = Field(None, ge=0, description="UV index")
    location: WeatherLocation = Field(..., description="Location coordinates")
    timestamp: datetime = Field(..., description="Weather data timestamp")


class WeatherForecastPoint(BaseModel):
    """Single weather forecast data point"""
    time: datetime = Field(..., description="Forecast time")
    temperature: float = Field(..., description="Temperature in Celsius")
    humidity: float = Field(..., ge=0, le=100, description="Humidity percentage")
    rain_probability: float = Field(..., ge=0, le=100, description="Rain probability percentage")
    weather_main: str = Field(..., description="Main weather condition")


class WeatherAlert(BaseModel):
    """Weather risk alert"""
    type: str = Field(..., description="Alert type (heat_warning, frost_warning, etc.)")
    severity: str = Field(..., description="Alert severity (low, medium, high, critical)")
    message: str = Field(..., description="Alert message")
    valid_from: datetime = Field(..., description="Alert validity start time")
    valid_until: datetime = Field(..., description="Alert validity end time")


class WeatherData(BaseModel):
    """Complete weather data response"""
    current: CurrentWeather = Field(..., description="Current weather conditions")
    forecast: list[WeatherForecastPoint] = Field(..., description="24-hour weather forecast")
    alerts: list[WeatherAlert] = Field(default=[], description="Weather risk alerts")
    cached_at: datetime = Field(..., description="When data was cached")
    cache_expires: datetime = Field(..., description="When cache expires")


class WeatherDataResponse(BaseModel):
    """Weather data API response"""
    current: CurrentWeather = Field(..., description="Current weather conditions")
    forecast: list[WeatherForecastPoint] = Field(..., description="24-hour weather forecast")
    alerts: list[WeatherAlert] = Field(default=[], description="Weather risk alerts")
    cached_at: datetime = Field(..., description="When data was cached")
    cache_expires: datetime = Field(..., description="When cache expires")


class WeatherErrorResponse(ErrorResponse):
    """Weather API error response"""
    error: dict = Field(
        default={
            "code": "WEATHER_ERROR",
            "message": "Failed to retrieve weather data",
            "details": {}
        }
    )


class WeatherValidationErrorResponse(ErrorResponse):
    """Weather API validation error"""
    error: dict = Field(
        default={
            "code": "VALIDATION_ERROR",
            "message": "Invalid weather request parameters",
            "details": {}
        }
    )


class WeatherTimeoutErrorResponse(ErrorResponse):
    """Weather API timeout error"""
    error: dict = Field(
        default={
            "code": "TIMEOUT_ERROR",
            "message": "Weather service timeout",
            "details": {}
        }
    )


class WeatherRateLimitErrorResponse(ErrorResponse):
    """Weather API rate limit error"""
    error: dict = Field(
        default={
            "code": "RATE_LIMIT_ERROR",
            "message": "Weather service rate limit exceeded",
            "details": {}
        }
    )


# NDVI Data Schemas
class NDVILocation(BaseModel):
    """Location coordinates for NDVI data"""
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lng: float = Field(..., ge=-180, le=180, description="Longitude")


class CurrentNDVI(BaseModel):
    """Current NDVI data"""
    ndvi_value: float = Field(..., ge=-1, le=1, description="Current NDVI value")
    ndvi_trend: str = Field(..., description="NDVI trend direction")
    vegetation_health: str = Field(..., description="Vegetation health assessment")
    imagery_url: str = Field(..., description="URL to NDVI satellite imagery")
    cloud_cover: float = Field(..., ge=0, le=100, description="Cloud cover percentage")
    data_quality: str = Field(..., description="Data quality assessment")
    location: NDVILocation = Field(..., description="Location coordinates")
    acquisition_date: str = Field(..., description="Satellite image acquisition timestamp")
    timestamp: datetime = Field(..., description="NDVI data retrieval timestamp")


class NDVITrend(BaseModel):
    """NDVI trend analysis"""
    ndvi_30d_avg: float = Field(..., description="30-day average NDVI")
    ndvi_7d_avg: float = Field(..., description="7-day average NDVI")
    ndvi_change_7d: float = Field(..., description="7-day NDVI change")
    trend_direction: str = Field(..., description="Trend direction")
    stress_detected: bool = Field(..., description="Whether vegetation stress is detected")


class NDVIHistoricalPoint(BaseModel):
    """Historical NDVI data point"""
    date: str = Field(..., description="Date string")
    ndvi_value: float = Field(..., description="NDVI value")
    data_quality: str = Field(..., description="Data quality")


class NDVIAlert(BaseModel):
    """NDVI-based alert"""
    type: str = Field(..., description="Alert type")
    severity: str = Field(..., description="Alert severity")
    message: str = Field(..., description="Alert message")
    ndvi_threshold: Optional[float] = Field(None, description="NDVI threshold that triggered alert")
    current_ndvi: Optional[float] = Field(None, description="Current NDVI value")
    trend_period: Optional[str] = Field(None, description="Trend analysis period")


class NDVIData(BaseModel):
    """Complete NDVI data response"""
    current: CurrentNDVI = Field(..., description="Current NDVI data")
    trend: NDVITrend = Field(..., description="NDVI trend analysis")
    historical: list[NDVIHistoricalPoint] = Field(..., description="Historical NDVI data")
    alerts: list[NDVIAlert] = Field(default=[], description="NDVI-based alerts")
    cached_at: datetime = Field(..., description="When data was cached")
    cache_expires: datetime = Field(..., description="When cache expires")


class NDVIDataResponse(BaseModel):
    """NDVI data API response"""
    current: CurrentNDVI = Field(..., description="Current NDVI data")
    trend: NDVITrend = Field(..., description="NDVI trend analysis")
    historical: list[NDVIHistoricalPoint] = Field(..., description="Historical NDVI data")
    alerts: list[NDVIAlert] = Field(default=[], description="NDVI-based alerts")
    cached_at: datetime = Field(..., description="When data was cached")
    cache_expires: datetime = Field(..., description="When cache expires")


class NDVIHistoryPoint(BaseModel):
    """NDVI historical data point with full details"""
    id: uuid.UUID = Field(..., description="Database ID")
    date: str = Field(..., description="Date string")
    ndvi_value: float = Field(..., description="NDVI value")
    ndvi_trend: str = Field(..., description="NDVI trend at time of reading")
    data_quality: str = Field(..., description="Data quality")
    cloud_cover: float = Field(..., description="Cloud cover percentage")
    acquisition_date: str = Field(..., description="Satellite acquisition date")
    imagery_url: str = Field(..., description="Imagery URL")


class NDVIHistoryResponse(BaseModel):
    """NDVI history API response"""
    history: list[NDVIHistoryPoint] = Field(..., description="Historical NDVI readings")
    total_count: int = Field(..., description="Total number of readings")
    query_params: dict = Field(..., description="Query parameters used")
    trend_analysis: Optional[dict] = Field(None, description="Trend analysis statistics")


class NDVIDeviceSummary(BaseModel):
    """NDVI summary for a single device"""
    device_id: str = Field(..., description="Device ID")
    name: Optional[str] = Field(None, description="Device name")
    latest_ndvi: float = Field(..., description="Latest NDVI value")
    trend: str = Field(..., description="Current NDVI trend")
    data_quality: str = Field(..., description="Data quality")
    last_updated: str = Field(..., description="Last update timestamp")
    health_status: str = Field(..., description="Device health status")


class NDVISummary(BaseModel):
    """NDVI summary statistics"""
    total_devices: int = Field(..., description="Total devices")
    devices_with_data: int = Field(..., description="Devices with NDVI data")
    avg_ndvi: float = Field(..., description="Average NDVI across devices")
    healthy_devices: int = Field(..., description="Number of healthy devices")
    stress_devices: int = Field(..., description="Number of stressed devices")


class NDVISummaryResponse(BaseModel):
    """NDVI summary API response"""
    devices: list[NDVIDeviceSummary] = Field(..., description="Device summaries")
    summary: NDVISummary = Field(..., description="Overall summary statistics")


# NDVI error response schemas
class NDVIErrorResponse(ErrorResponse):
    """NDVI API error response"""
    error: dict = Field(
        default={
            "code": "NDVI_ERROR",
            "message": "Failed to retrieve NDVI data",
            "details": {}
        }
    )


class NDVIValidationErrorResponse(ErrorResponse):
    """NDVI API validation error"""
    error: dict = Field(
        default={
            "code": "VALIDATION_ERROR",
            "message": "Invalid NDVI request parameters",
            "details": {}
        }
    )


class NDVITimeoutErrorResponse(ErrorResponse):
    """NDVI API timeout error"""
    error: dict = Field(
        default={
            "code": "TIMEOUT_ERROR",
            "message": "NDVI service timeout",
            "details": {}
        }
    )


class NDVIRateLimitErrorResponse(ErrorResponse):
    """NDVI API rate limit error"""
    error: dict = Field(
        default={
            "code": "RATE_LIMIT_ERROR",
            "message": "NDVI service rate limit exceeded",
            "details": {}
        }
    )


# KATARA Alert System Schemas
class AlertType(str, Enum):
    """Alert types for KATARA system"""
    THRESHOLD_EXCEEDED = "threshold_exceeded"
    AI_RECOMMENDATION = "ai_recommendation"
    WEATHER_RISK = "weather_risk"


class MetricType(str, Enum):
    """Metric types for threshold alerts"""
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    NDVI = "ndvi"


class Alert(BaseModel):
    """Alert data model"""
    id: uuid.UUID = Field(..., description="Alert ID")
    farmer_id: uuid.UUID = Field(..., description="Farmer ID who owns the alert")
    device_id: Optional[str] = Field(None, description="Device ID that triggered the alert")
    type: AlertType = Field(..., description="Alert type")
    severity: AlertSeverity = Field(..., description="Alert severity level")
    message: str = Field(..., description="Alert message")
    read_status: bool = Field(default=False, description="Whether alert has been read (true=read, false=unread)")
    read_at: Optional[datetime] = Field(None, description="Timestamp when alert was marked as read")
    created_at: datetime = Field(..., description="Alert creation timestamp")
    
    # Additional fields for threshold alerts
    metric: Optional[MetricType] = Field(None, description="Metric type that triggered alert")
    value: Optional[float] = Field(None, description="Actual metric value")
    threshold: Optional[float] = Field(None, description="Threshold that was exceeded")

    model_config = ConfigDict(use_enum_values=True)


class AlertCreate(BaseModel):
    """Internal alert creation schema"""
    farmer_id: uuid.UUID = Field(..., description="Farmer ID")
    device_id: Optional[str] = Field(None, description="Device ID")
    type: AlertType = Field(..., description="Alert type")
    severity: AlertSeverity = Field(..., description="Alert severity")
    message: str = Field(..., description="Alert message")
    metric: Optional[MetricType] = Field(None, description="Metric type")
    value: Optional[float] = Field(None, description="Metric value")
    threshold: Optional[float] = Field(None, description="Threshold value")

    model_config = ConfigDict(use_enum_values=True)


class AlertUpdateRequest(BaseModel):
    """Request schema for updating alert"""
    read_status: bool = Field(..., description="New read status (true=read, false=unread)")


class AlertUpdateResponse(BaseModel):
    """Response schema for alert update"""
    id: uuid.UUID = Field(..., description="Alert ID")
    read_status: bool = Field(..., description="Updated read status")
    read_at: Optional[datetime] = Field(None, description="Timestamp when alert was marked as read")
    updated_at: datetime = Field(..., description="Update timestamp")


class AlertListParams(BaseModel):
    """Parameters for alert list API"""
    limit: int = Field(default=20, ge=1, le=100, description="Number of alerts per page")
    offset: int = Field(default=0, ge=0, description="Number of alerts to skip")
    severity: Optional[AlertSeverity] = Field(None, description="Filter by severity")
    read_status: Optional[bool] = Field(None, description="Filter by read status (true=read, false=unread)")
    device_id: Optional[str] = Field(None, description="Filter by device ID")

    model_config = ConfigDict(use_enum_values=True)


class AlertPagination(BaseModel):
    """Pagination information for alert list"""
    limit: int = Field(..., description="Number of items per page")
    offset: int = Field(..., description="Number of items skipped")
    has_more: bool = Field(..., description="Whether more items are available")


class AlertListResponse(BaseModel):
    """Response schema for alert list"""
    alerts: list[Alert] = Field(..., description="List of alerts")
    unread_count: int = Field(..., description="Number of unread alerts")
    total: int = Field(..., description="Total number of alerts")
    pagination: AlertPagination = Field(..., description="Pagination information")

    model_config = ConfigDict(use_enum_values=True)


class AlertStats(BaseModel):
    """Alert statistics for dashboard"""
    total_alerts: int = Field(..., description="Total number of alerts")
    unread_alerts: int = Field(..., description="Number of unread alerts")
    high_severity: int = Field(..., description="Number of high severity alerts")
    medium_severity: int = Field(..., description="Number of medium severity alerts")
    low_severity: int = Field(..., description="Number of low severity alerts")
    critical_severity: int = Field(..., description="Number of critical severity alerts")


class ThresholdConfig(BaseModel):
    """Threshold configuration for alert generation"""
    temperature_high: float = Field(default=40.0, ge=-10, le=60, description="High temperature threshold in Celsius")
    humidity_low: float = Field(default=20.0, ge=0, le=100, description="Low humidity threshold in percentage")
    ndvi_low: float = Field(default=0.3, ge=-1, le=1, description="Low NDVI threshold")


class ThresholdViolation(BaseModel):
    """Threshold violation information"""
    metric: MetricType = Field(..., description="Type of metric that violated threshold")
    value: float = Field(..., description="Actual metric value")
    threshold: float = Field(..., description="Threshold that was violated")
    severity: AlertSeverity = Field(..., description="Severity level of the violation")
    operator: str = Field(..., description="Comparison operator (>, <)")
    violation_amount: float = Field(..., description="Amount by which threshold was violated")
    
    def __repr__(self) -> str:
        return f"ThresholdViolation(metric={self.metric.value}, value={self.value}, threshold={self.threshold}, severity={self.severity.value})"


class AlertGenerationRequest(BaseModel):
    """Request schema for alert generation during telemetry processing"""
    device_id: str = Field(..., description="Device ID")
    farmer_id: uuid.UUID = Field(..., description="Farmer ID")
    temperature: float = Field(..., ge=-10, le=60, description="Temperature reading")
    humidity: float = Field(..., ge=0, le=100, description="Humidity reading")
    ndvi: Optional[float] = Field(None, ge=-1, le=1, description="NDVI reading")
    timestamp: datetime = Field(..., description="Telemetry timestamp")


class AlertGenerationResponse(BaseModel):
    """Response schema for alert generation"""
    alerts_created: int = Field(..., description="Number of alerts created")
    alert_ids: list[uuid.UUID] = Field(..., description="IDs of created alerts")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")


# Alert error response schemas
class AlertNotFoundResponse(ErrorResponse):
    """Alert not found error response"""
    error: dict = Field(
        default={
            "code": "ALERT_NOT_FOUND",
            "message": "Alert not found"
        }
    )


class AlertForbiddenResponse(ErrorResponse):
    """Alert access forbidden error response"""
    error: dict = Field(
        default={
            "code": "FORBIDDEN",
            "message": "Access denied to this alert"
        }
    )


class AlertValidationErrorResponse(ErrorResponse):
    """Alert validation error response"""
    error: dict = Field(
        default={
            "code": "VALIDATION_ERROR",
            "message": "Invalid alert data",
            "details": {}
        }
    )


# Device Settings and Auto Analysis Schemas
class DeviceSettingsUpdate(BaseModel):
    """Request schema for updating device analysis settings"""
    auto_analysis_enabled: bool = Field(..., description="Enable/disable automatic AI analysis")
    analysis_frequency_hours: int = Field(
        default=6, 
        ge=2, 
        le=24, 
        description="Minimum hours between automatic analyses"
    )
    critical_threshold_only: bool = Field(
        default=False, 
        description="Only trigger analysis on critical thresholds"
    )


class DeviceSettingsResponse(BaseModel):
    """Response schema for device analysis settings"""
    device_id: str = Field(..., description="Device ID")
    auto_analysis_enabled: bool = Field(..., description="Automatic analysis enabled status")
    analysis_frequency_hours: int = Field(..., description="Analysis frequency in hours")
    last_auto_analysis: Optional[datetime] = Field(None, description="Last automatic analysis timestamp")
    critical_threshold_only: bool = Field(..., description="Critical threshold only mode")


class AutoAnalysisTrigger(BaseModel):
    """Automatic analysis trigger information"""
    device_id: str = Field(..., description="Device ID")
    trigger_type: str = Field(..., description="Type of trigger")
    trigger_conditions: Dict[str, Any] = Field(..., description="Conditions that triggered analysis")
    analysis_priority: str = Field(..., description="Analysis priority level")
    timestamp: datetime = Field(..., description="Trigger timestamp")


class AutoAnalysisStats(BaseModel):
    """Statistics for automatic analysis"""
    total_analyses: int = Field(..., description="Total automatic analyses performed")
    critical_triggers: int = Field(..., description="Analyses triggered by critical conditions")
    periodic_triggers: int = Field(..., description="Analyses triggered periodically")
    success_rate: float = Field(..., description="Success rate percentage")
    avg_response_time: float = Field(..., description="Average response time in seconds")
    last_analysis: Optional[datetime] = Field(None, description="Last analysis timestamp")


# Device Settings Error Responses
class DeviceSettingsNotFoundResponse(ErrorResponse):
    """Device not found error response"""
    error: dict = Field(
        default={
            "code": "DEVICE_NOT_FOUND",
            "message": "Device not found or access denied"
        }
    )


class DeviceSettingsValidationErrorResponse(ErrorResponse):
    """Device settings validation error response"""
    error: dict = Field(
        default={
            "code": "VALIDATION_ERROR",
            "message": "Invalid device settings",
            "details": {}
        }
    )


class DeviceSettingsUpdateFailedResponse(ErrorResponse):
    """Device settings update failed error response"""
    error: dict = Field(
        default={
            "code": "SETTINGS_UPDATE_FAILED",
            "message": "Failed to update device settings"
        }
    )


# Telemetry and AI Analysis Schemas
class TelemetryReading(BaseModel):
    """Telemetry data reading from IoT devices"""
    device_id: str = Field(..., description="Device identifier")
    sensor_type: str = Field(..., description="Type of sensor (temperature, humidity, etc.)")
    value: float = Field(..., description="Sensor reading value")
    unit: str = Field(..., description="Unit of measurement")
    timestamp: datetime = Field(..., description="Reading timestamp")
    location_lat: Optional[float] = Field(None, description="Latitude")
    location_lng: Optional[float] = Field(None, description="Longitude")


class AlertType(str, Enum):
    """Alert types for the system"""
    TEMPERATURE_HIGH = "TEMPERATURE_HIGH"
    TEMPERATURE_LOW = "TEMPERATURE_LOW"
    HUMIDITY_HIGH = "HUMIDITY_HIGH"
    HUMIDITY_LOW = "HUMIDITY_LOW"
    SOIL_MOISTURE_LOW = "SOIL_MOISTURE_LOW"
    DEVICE_OFFLINE = "DEVICE_OFFLINE"
    BATTERY_LOW = "BATTERY_LOW"
    SENSOR_FAILURE = "SENSOR_FAILURE"


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Alert(BaseModel):
    """Alert schema for system notifications"""
    id: Optional[str] = Field(None, description="Alert ID")
    device_id: str = Field(..., description="Device ID")
    alert_type: AlertType = Field(..., description="Type of alert")
    severity: AlertSeverity = Field(..., description="Alert severity")
    message: str = Field(..., description="Alert message")
    timestamp: datetime = Field(..., description="Alert timestamp")
    acknowledged: bool = Field(default=False, description="Alert acknowledgment status")
    resolved_at: Optional[datetime] = Field(None, description="Alert resolution timestamp")


class AIAnalysisRequest(BaseModel):
    """Request for AI analysis of telemetry data"""
    device_id: str = Field(..., description="Device identifier")
    analysis_type: str = Field(..., description="Type of analysis required")
    time_range_hours: int = Field(default=24, description="Time range in hours")
    include_recommendations: bool = Field(default=True, description="Include AI recommendations")
    priority: str = Field(default="normal", description="Analysis priority")
