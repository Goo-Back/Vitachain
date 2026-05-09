"""
Row-Level Security (RLS) Integration for RBAC
Integrates VitaChain RBAC with Supabase RLS policies
"""

from typing import Dict, Any, Optional
from enum import Enum
import structlog
from fastapi import HTTPException, status

from .permissions import UserRole, Permission, rbac_manager

logger = structlog.get_logger("rls")


class RLSOperation(str, Enum):
    """RLS operation types"""
    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    ALL = "ALL"


class RLSTable(str, Enum):
    """RLS-protected tables"""
    PROFILES = "profiles"
    TELEMETRY = "telemetry"
    DEVICES = "devices"
    ALERTS = "alerts"
    LISTINGS = "listings"
    ORDERS = "orders"
    MEALS = "meals"
    RESERVATIONS = "reservations"
    USERS = "users"
    AUDIT_LOGS = "audit_logs"


class RLSManager:
    """Row-Level Security Manager for VitaChain"""
    
    def __init__(self, supabase_client):
        self.supabase = supabase_client
    
    async def check_rls_permission(
        self, 
        user_role: UserRole, 
        table: RLSTable, 
        operation: RLSOperation,
        resource_user_id: Optional[str] = None
    ) -> bool:
        """
        Check if RLS policy allows operation
        
        Args:
            user_role: User's role
            table: Table being accessed
            operation: Type of operation
            resource_user_id: Owner ID for ownership checks
            
        Returns:
            True if RLS allows operation, False otherwise
        """
        try:
            # Call Supabase RLS function
            rls_query = f"""
                SELECT rls.uses_role(
                    '{user_role}', 
                    '{table.value}', 
                    '{operation.value}'
                ) as can_access
            """
            
            result = await self.supabase.rpc('check_rls_policy')(query=rls_query)
            
            if not result or not result.get('can_access'):
                logger.warning(
                    "rls_denied",
                    user_role=user_role,
                    table=table.value,
                    operation=operation.value,
                    resource_user_id=resource_user_id
                )
                return False
            
            # Additional ownership check for user resources
            if resource_user_id and user_role not in [UserRole.ADMIN, UserRole.SUPPORT]:
                ownership_query = f"""
                    SELECT rls.check_ownership(
                        '{user_role}',
                        '{resource_user_id}',
                        '{table.value}'
                    ) as can_access
                """
                
                ownership_result = await self.supabase.rpc('check_rls_policy')(query=ownership_query)
                
                if not ownership_result or not ownership_result.get('can_access'):
                    logger.warning(
                        "rls_ownership_denied",
                        user_role=user_role,
                        table=table.value,
                        resource_user_id=resource_user_id
                    )
                    return False
            
            logger.debug(
                "rls_granted",
                user_role=user_role,
                table=table.value,
                operation=operation.value,
                resource_user_id=resource_user_id
            )
            
            return True
            
        except Exception as e:
            logger.error(
                "rls_check_error",
                error=str(e),
                user_role=user_role,
                table=table.value,
                operation=operation.value
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "RLS_CHECK_ERROR",
                    "message": "Error checking RLS policy"
                }
            )
    
    async def create_rls_policy(
        self,
        user_role: UserRole,
        table: RLSTable,
        policy_definition: Dict[str, Any]
    ) -> bool:
        """
        Create or update RLS policy for a role and table
        
        Args:
            user_role: Role to create policy for
            table: Table to create policy for
            policy_definition: RLS policy definition
            
        Returns:
            True if policy created successfully, False otherwise
        """
        try:
            # Create RLS policy using Supabase function
            policy_sql = self._generate_rls_policy_sql(user_role, table, policy_definition)
            
            result = await self.supabase.rpc('create_rls_policy')(
                query=policy_sql,
                params={
                    'role': user_role.value,
                    'table': table.value,
                    'policy': policy_definition
                }
            )
            
            if result:
                logger.info(
                    "rls_policy_created",
                    user_role=user_role,
                    table=table.value
                )
                return True
            else:
                logger.error(
                    "rls_policy_creation_failed",
                    user_role=user_role,
                    table=table.value
                )
                return False
                
        except Exception as e:
            logger.error(
                "rls_policy_creation_error",
                error=str(e),
                user_role=user_role,
                table=table.value
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "RLS_POLICY_CREATION_ERROR",
                    "message": "Error creating RLS policy"
                }
            )
    
    def _generate_rls_policy_sql(self, user_role: UserRole, table: RLSTable, policy: Dict[str, Any]) -> str:
        """Generate SQL for RLS policy creation"""
        
        # Basic RLS policy template
        base_policy = f"""
            -- Enable RLS for {table.value} table
            ALTER TABLE {table.value} ENABLE ROW LEVEL SECURITY;
            
            -- Create policy for {user_role.value} role
            CREATE POLICY {table.value}_{user_role.value.lower()}_policy AS (
                USING (
                    rls.uses_role(
                        auth.jwt() ->> 'role',
                        '{user_role.value}',
                        '{table.value}'
                    )
                )
                WITH CHECK (
                    rls.check_permission(
                        auth.jwt() ->> 'role',
                        auth.jwt() ->> 'user_id',
                        '{policy.get("condition", "true")}'
                    )
                )
            );
        """
        
        return base_policy
    
    async def audit_rls_access(
        self,
        user_id: str,
        user_role: UserRole,
        table: RLSTable,
        operation: RLSOperation,
        result: str,
        resource_id: Optional[str] = None
    ) -> bool:
        """
        Audit RLS access for security monitoring
        
        Args:
            user_id: User ID performing operation
            user_role: User's role
            table: Table being accessed
            operation: Type of operation
            result: Result of operation (GRANTED/DENIED)
            resource_id: ID of resource being accessed
            
        Returns:
            True if audit logged successfully, False otherwise
        """
        try:
            audit_data = {
                'user_id': user_id,
                'user_role': user_role.value,
                'table': table.value,
                'operation': operation.value,
                'result': result,
                'resource_id': resource_id,
                'timestamp': 'NOW()',
                'ip_address': 'client_ip()'  # Would need to pass IP from request
            }
            
            await self.supabase.table('rls_audit_logs').insert(audit_data)
            
            logger.info(
                "rls_audit_logged",
                user_id=user_id,
                user_role=user_role,
                table=table.value,
                operation=operation.value,
                result=result
            )
            
            return True
            
        except Exception as e:
            logger.error(
                "rls_audit_error",
                error=str(e),
                user_id=user_id,
                user_role=user_role,
                table=table.value,
                operation=operation.value
            )
            return False


# Global RLS manager instance
def get_rls_manager(supabase_client) -> RLSManager:
    """Get RLS manager instance"""
    return RLSManager(supabase_client)


# RLS helper functions for integration with RBAC
async def check_rls_permission_with_rbac(
    user_role: UserRole,
    table: RLSTable,
    operation: RLSOperation,
    user_id: str,
    resource_user_id: Optional[str] = None,
    supabase_client = None
) -> bool:
    """
    Check both RLS policy and RBAC permissions
    
    This function combines RLS database-level security with 
    application-level RBAC for comprehensive access control
    """
    
    # First check RBAC permissions
    required_permissions = _get_required_permissions_for_table(table, operation)
    
    for permission in required_permissions:
        if not rbac_manager.has_permission(user_role, permission):
            logger.warning(
                "rbac_denied",
                user_role=user_role,
                table=table.value,
                operation=operation.value,
                permission=permission.value
            )
            return False
    
    # If RBAC allows access, check RLS policy
    if supabase_client:
        rls_manager = get_rls_manager(supabase_client)
        return await rls_manager.check_rls_permission(
            user_role, table, operation, resource_user_id
        )
    
    # Fallback to RBAC-only check if no RLS manager
    return True


def _get_required_permissions_for_table(table: RLSTable, operation: RLSOperation) -> list[Permission]:
    """Get required RBAC permissions for table and operation"""
    
    permission_map = {
        (RLSTable.TELEMETRY, RLSOperation.SELECT): [Permission.READ_OWN_TELEMETRY],
        (RLSTable.TELEMETRY, RLSOperation.INSERT): [Permission.WRITE_OWN_DEVICES],
        (RLSTable.TELEMETRY, RLSOperation.UPDATE): [Permission.WRITE_OWN_DEVICES],
        (RLSTable.DEVICES, RLSOperation.SELECT): [Permission.WRITE_OWN_DEVICES],
        (RLSTable.DEVICES, RLSOperation.UPDATE): [Permission.WRITE_OWN_DEVICES],
        (RLSTable.ALERTS, RLSOperation.SELECT): [Permission.READ_OWN_ALERTS],
        (RLSTable.ALERTS, RLSOperation.INSERT): [Permission.WRITE_OWN_ALERTS],
        (RLSTable.ALERTS, RLSOperation.UPDATE): [Permission.WRITE_OWN_ALERTS],
        (RLSTable.LISTINGS, RLSOperation.SELECT): [Permission.READ_OWN_LISTINGS],
        (RLSTable.LISTINGS, RLSOperation.INSERT): [Permission.WRITE_OWN_LISTINGS],
        (RLSTable.LISTINGS, RLSOperation.UPDATE): [Permission.WRITE_OWN_LISTINGS],
        (RLSTable.MEALS, RLSOperation.SELECT): [Permission.READ_OWN_MEALS],
        (RLSTable.MEALS, RLSOperation.INSERT): [Permission.WRITE_OWN_MEALS],
        (RLSTable.MEALS, RLSOperation.UPDATE): [Permission.WRITE_OWN_MEALS],
        (RLSTable.RESERVATIONS, RLSOperation.SELECT): [Permission.READ_OWN_RESERVATIONS],
        (RLSTable.RESERVATIONS, RLSOperation.INSERT): [Permission.WRITE_OWN_RESERVATIONS],
        (RLSTable.USERS, RLSOperation.SELECT): [Permission.READ_USERS],
        (RLSTable.AUDIT_LOGS, RLSOperation.SELECT): [Permission.READ_AUDIT_LOGS],
    }
    
    return permission_map.get((table, operation), [])
