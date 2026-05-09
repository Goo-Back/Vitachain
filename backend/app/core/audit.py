"""
Audit logging for VitaChain RBAC system
Tracks admin and support actions for security monitoring
"""

from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum
import structlog
from fastapi import HTTPException, status

from .permissions import UserRole, Permission

logger = structlog.get_logger("audit")


class AuditAction(str, Enum):
    """Audit action types"""
    LOGIN = "login"
    LOGOUT = "logout"
    PERMISSION_CHECK = "permission_check"
    DATA_ACCESS = "data_access"
    ROLE_CHANGE = "role_change"
    USER_MANAGEMENT = "user_management"
    SYSTEM_ACCESS = "system_access"
    RLS_VIOLATION = "rls_violation"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"


class AuditSeverity(str, Enum):
    """Audit severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AuditLogger:
    """Audit logger for VitaChain platform"""
    
    def __init__(self, supabase_client):
        self.supabase = supabase_client
    
    async def log_admin_action(
        self,
        admin_id: str,
        action: AuditAction,
        resource: str,
        result: str,
        details: Optional[Dict[str, Any]] = None,
        severity: AuditSeverity = AuditSeverity.INFO,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> bool:
        """
        Log admin action for audit trail
        
        Args:
            admin_id: ID of admin performing action
            action: Type of action being performed
            resource: Resource being accessed/modified
            result: Result of the action (SUCCESS/FAILED)
            details: Additional details about the action
            severity: Severity level of the action
            user_id: User ID (for context)
            ip_address: IP address of the request
            
        Returns:
            True if audit logged successfully, False otherwise
        """
        try:
            audit_data = {
                'admin_id': admin_id,
                'action': action.value,
                'resource': resource,
                'result': result,
                'details': details or {},
                'severity': severity.value,
                'user_id': user_id,
                'ip_address': ip_address,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            await self.supabase.table('audit_logs').insert(audit_data)
            
            logger.info(
                "audit_admin_action_logged",
                admin_id=admin_id,
                action=action.value,
                resource=resource,
                result=result,
                severity=severity.value
            )
            
            return True
            
        except Exception as e:
            logger.error(
                "audit_logging_error",
                error=str(e),
                admin_id=admin_id,
                action=action.value,
                resource=resource
            )
            return False
    
    async def log_permission_check(
        self,
        user_id: str,
        user_role: UserRole,
        permission: Permission,
        granted: bool,
        resource: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> bool:
        """
        Log permission check for security monitoring
        
        Args:
            user_id: ID of user performing action
            user_role: User's role
            permission: Permission being checked
            granted: Whether permission was granted
            resource: Resource being accessed
            ip_address: IP address of the request
            
        Returns:
            True if audit logged successfully, False otherwise
        """
        try:
            audit_data = {
                'user_id': user_id,
                'user_role': user_role.value,
                'permission': permission.value,
                'granted': granted,
                'resource': resource,
                'action': AuditAction.PERMISSION_CHECK.value,
                'result': 'GRANTED' if granted else 'DENIED',
                'severity': AuditSeverity.WARNING.value if not granted else AuditSeverity.INFO.value,
                'ip_address': ip_address,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            await self.supabase.table('audit_logs').insert(audit_data)
            
            logger.info(
                "audit_permission_check_logged",
                user_id=user_id,
                user_role=user_role.value,
                permission=permission.value,
                granted=granted,
                resource=resource
            )
            
            return True
            
        except Exception as e:
            logger.error(
                "audit_permission_check_error",
                error=str(e),
                user_id=user_id,
                permission=permission.value
            )
            return False
    
    async def log_data_access(
        self,
        user_id: str,
        user_role: UserRole,
        table: str,
        operation: str,
        resource_id: Optional[str] = None,
        granted: bool,
        ip_address: Optional[str] = None
    ) -> bool:
        """
        Log data access for security monitoring
        
        Args:
            user_id: ID of user performing action
            user_role: User's role
            table: Table being accessed
            operation: Operation being performed
            resource_id: ID of specific resource
            granted: Whether access was granted
            ip_address: IP address of the request
            
        Returns:
            True if audit logged successfully, False otherwise
        """
        try:
            audit_data = {
                'user_id': user_id,
                'user_role': user_role.value,
                'table': table,
                'operation': operation,
                'resource_id': resource_id,
                'action': AuditAction.DATA_ACCESS.value,
                'result': 'GRANTED' if granted else 'DENIED',
                'severity': AuditSeverity.WARNING.value if not granted else AuditSeverity.INFO.value,
                'ip_address': ip_address,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            await self.supabase.table('audit_logs').insert(audit_data)
            
            logger.info(
                "audit_data_access_logged",
                user_id=user_id,
                user_role=user_role.value,
                table=table,
                operation=operation,
                granted=granted,
                resource_id=resource_id
            )
            
            return True
            
        except Exception as e:
            logger.error(
                "audit_data_access_error",
                error=str(e),
                user_id=user_id,
                table=table,
                operation=operation
            )
            return False
    
    async def log_rls_violation(
        self,
        user_id: str,
        user_role: UserRole,
        table: str,
        operation: str,
        violation_details: str,
        ip_address: Optional[str] = None
    ) -> bool:
        """
        Log RLS policy violation for security monitoring
        
        Args:
            user_id: ID of user performing action
            user_role: User's role
            table: Table where violation occurred
            operation: Operation being performed
            violation_details: Details of the violation
            ip_address: IP address of the request
            
        Returns:
            True if audit logged successfully, False otherwise
        """
        try:
            audit_data = {
                'user_id': user_id,
                'user_role': user_role.value,
                'table': table,
                'operation': operation,
                'action': AuditAction.RLS_VIOLATION.value,
                'result': 'VIOLATION',
                'violation_details': violation_details,
                'severity': AuditSeverity.ERROR.value,
                'ip_address': ip_address,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            await self.supabase.table('audit_logs').insert(audit_data)
            
            logger.warning(
                "audit_rls_violation_logged",
                user_id=user_id,
                user_role=user_role.value,
                table=table,
                operation=operation,
                violation_details=violation_details
            )
            
            return True
            
        except Exception as e:
            logger.error(
                "audit_rls_violation_error",
                error=str(e),
                user_id=user_id,
                table=table,
                operation=operation
            )
            return False
    
    async def log_rate_limit_exceeded(
        self,
        user_id: str,
        user_role: UserRole,
        operation: str,
        limit_type: str,
        ip_address: Optional[str] = None
    ) -> bool:
        """
        Log rate limit exceeded for security monitoring
        
        Args:
            user_id: ID of user performing action
            user_role: User's role
            operation: Operation being rate limited
            limit_type: Type of rate limit exceeded
            ip_address: IP address of the request
            
        Returns:
            True if audit logged successfully, False otherwise
        """
        try:
            audit_data = {
                'user_id': user_id,
                'user_role': user_role.value,
                'operation': operation,
                'action': AuditAction.RATE_LIMIT_EXCEEDED.value,
                'result': 'EXCEEDED',
                'limit_type': limit_type,
                'severity': AuditSeverity.WARNING.value,
                'ip_address': ip_address,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            await self.supabase.table('audit_logs').insert(audit_data)
            
            logger.warning(
                "audit_rate_limit_exceeded_logged",
                user_id=user_id,
                user_role=user_role.value,
                operation=operation,
                limit_type=limit_type
            )
            
            return True
            
        except Exception as e:
            logger.error(
                "audit_rate_limit_error",
                error=str(e),
                user_id=user_id,
                operation=operation
            )
            return False


# Global audit logger instance
def get_audit_logger(supabase_client) -> AuditLogger:
    """Get audit logger instance"""
    return AuditLogger(supabase_client)


# Audit helper functions for integration with RBAC
async def log_admin_action_with_audit(
    user_id: str,
    user_role: UserRole,
    action: str,
    resource: str,
    result: str,
    supabase_client = None,
    ip_address: Optional[str] = None
) -> bool:
    """
    Log admin action if user has admin privileges
    
    This function combines RBAC permission check with audit logging
    """
    if user_role not in [UserRole.ADMIN, UserRole.SUPPORT]:
        return False  # Only admin/support can be audited for admin actions
    
    if supabase_client:
        audit_logger = get_audit_logger(supabase_client)
        return await audit_logger.log_admin_action(
            admin_id=user_id,
            action=AuditAction(action),
            resource=resource,
            result=result,
            ip_address=ip_address
        )
    
    return False


async def log_permission_check_with_audit(
    user_id: str,
    user_role: UserRole,
    permission: Permission,
    granted: bool,
    resource: Optional[str] = None,
    supabase_client = None,
    ip_address: Optional[str] = None
) -> bool:
    """
    Log permission check with audit trail
    
    This function combines permission checking with audit logging
    """
    if supabase_client:
        audit_logger = get_audit_logger(supabase_client)
        return await audit_logger.log_permission_check(
            user_id=user_id,
            user_role=user_role,
            permission=permission,
            granted=granted,
            resource=resource,
            ip_address=ip_address
        )
    
    return False
