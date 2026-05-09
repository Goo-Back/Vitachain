"""
Admin User Management Service
Handles all admin user management operations including search, filtering, status updates, and audit logging
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import structlog
from fastapi import HTTPException, status

from app.core.database import get_supabase_client
from app.services.cache_service import cache_service, get_user_stats_key, get_user_list_key, get_user_details_key, invalidate_user_cache
from app.models.schemas import (
    AdminUserView,
    UserStats,
    UserFilters,
    UserStatusUpdateRequest,
    UserRoleUpdateRequest,
    BulkUserUpdateRequest,
    BulkUserUpdateResponse,
    UserListResponse,
    UserExportRequest,
    AdminAuditLog,
    UserStatus,
    UserRole
)

logger = structlog.get_logger("admin_service")


class AdminUserService:
    """Service class for admin user management operations"""
    
    def __init__(self, supabase_client):
        self.supabase = supabase_client
    
    async def get_users(
        self,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None,
        role: Optional[UserRole] = None,
        status: Optional[UserStatus] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> UserListResponse:
        """
        Get paginated list of users with search and filters
        
        Args:
            page: Page number for pagination
            limit: Number of users per page
            search: Search term for email or name
            role: Filter by user role
            status: Filter by account status
            date_from: Filter users from this date
            date_to: Filter users to this date
            
        Returns:
            UserListResponse with users, pagination, and stats
        """
        try:
            logger.info(
                "Fetching users with filters",
                page=page,
                limit=limit,
                search=search,
                role=role,
                status=status,
                date_from=date_from,
                date_to=date_to
            )
            
            # Build base query
            query = self.supabase.table("profiles").select(
                """
                id,
                email,
                full_name,
                phone,
                role,
                account_status,
                created_at,
                updated_at,
                last_login
                """
            )
            
            # Apply filters
            if role:
                query = query.eq("role", role.value)
            
            if status:
                query = query.eq("account_status", status.value)
            
            if date_from:
                query = query.gte("created_at", date_from)
            
            if date_to:
                query = query.lte("created_at", date_to)
            
            if search:
                # Search in email and full_name
                query = query.or_(
                    f"email.ilike.%{search}%,full_name.ilike.%{search}%"
                )
            
            # Get total count
            count_query = query
            count_result = count_query.execute()
            total_users = len(count_result.data) if count_result.data else 0
            
            # Apply pagination
            offset = (page - 1) * limit
            query = query.order("created_at", desc=True).range(offset, offset + limit - 1)
            
            result = query.execute()
            
            # Get additional user statistics
            users_with_stats = []
            for user in result.data or []:
                # Get user-specific counts
                devices_count = await self._get_user_devices_count(user["id"])
                listings_count = await self._get_user_listings_count(user["id"])
                reservations_count = await self._get_user_reservations_count(user["id"])
                orders_count = await self._get_user_orders_count(user["id"])
                
                admin_user = AdminUserView(
                    id=user["id"],
                    email=user["email"],
                    full_name=user["full_name"],
                    phone=user.get("phone"),
                    role=UserRole(user["role"]),
                    account_status=UserStatus(user.get("account_status", "active")),
                    created_at=user["created_at"],
                    updated_at=user["updated_at"],
                    last_login=user.get("last_login"),
                    devices_count=devices_count,
                    listings_count=listings_count,
                    reservations_count=reservations_count,
                    orders_count=orders_count
                )
                users_with_stats.append(admin_user)
            
            # Get user statistics
            stats = await self._get_user_stats()
            
            # Calculate pagination
            pages = (total_users + limit - 1) // limit
            
            return UserListResponse(
                users=users_with_stats,
                pagination={
                    "page": page,
                    "limit": limit,
                    "total": total_users,
                    "pages": pages
                },
                stats=stats
            )
            
        except Exception as e:
            logger.error("Error fetching users", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to fetch users"
                }
            )
    
    async def get_user_details(self, user_id: str) -> AdminUserView:
        """
        Get detailed information about a specific user
        
        Args:
            user_id: UUID of the user
            
        Returns:
            AdminUserView with detailed user information
        """
        try:
            logger.info("Fetching user details", user_id=user_id)
            
            result = self.supabase.table("profiles").select(
                """
                id,
                email,
                full_name,
                phone,
                role,
                account_status,
                created_at,
                updated_at,
                last_login
                """
            ).eq("id", user_id).execute()
            
            if not result.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "code": "USER_NOT_FOUND",
                        "message": "User not found"
                    }
                )
            
            user = result.data[0]
            
            # Get user-specific counts
            devices_count = await self._get_user_devices_count(user["id"])
            listings_count = await self._get_user_listings_count(user["id"])
            reservations_count = await self._get_user_reservations_count(user["id"])
            orders_count = await self._get_user_orders_count(user["id"])
            
            return AdminUserView(
                id=user["id"],
                email=user["email"],
                full_name=user["full_name"],
                phone=user.get("phone"),
                role=UserRole(user["role"]),
                account_status=UserStatus(user.get("account_status", "active")),
                created_at=user["created_at"],
                updated_at=user["updated_at"],
                last_login=user.get("last_login"),
                devices_count=devices_count,
                listings_count=listings_count,
                reservations_count=reservations_count,
                orders_count=orders_count
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Error fetching user details", user_id=user_id, error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to fetch user details"
                }
            )
    
    async def update_user_status(
        self,
        user_id: str,
        new_status: UserStatus,
        reason: str,
        admin_id: str
    ) -> Dict[str, Any]:
        """
        Update user account status with audit logging
        
        Args:
            user_id: UUID of the user to update
            new_status: New account status
            reason: Reason for status change
            admin_id: UUID of the admin performing the action
            
        Returns:
            Success response with updated status
        """
        try:
            logger.info(
                "Updating user status",
                user_id=user_id,
                new_status=new_status,
                admin_id=admin_id
            )
            
            # Get current user status
            current_result = self.supabase.table("profiles")\
                .select("account_status, email")\
                .eq("id", user_id)\
                .execute()
            
            if not current_result.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "code": "USER_NOT_FOUND",
                        "message": "User not found"
                    }
                )
            
            current_status = current_result.data[0]["account_status"]
            user_email = current_result.data[0]["email"]
            
            # Validate status transition
            if not self._is_valid_status_transition(current_status, new_status):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "code": "INVALID_STATUS_TRANSITION",
                        "message": "Invalid account status transition"
                    }
                )
            
            # Update user status
            update_data = {
                "account_status": new_status.value,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            if new_status == UserStatus.ACTIVE:
                update_data["last_login"] = datetime.utcnow().isoformat()
            
            self.supabase.table("profiles")\
                .update(update_data)\
                .eq("id", user_id)\
                .execute()
            
            # Log admin action
            await self._log_admin_action(
                admin_id=admin_id,
                action="update_user_status",
                target_user_id=user_id,
                target_user_email=user_email,
                details={
                    "previous_status": current_status,
                    "new_status": new_status.value,
                    "reason": reason
                }
            )
            
            return {
                "message": "User status updated successfully",
                "user_id": user_id,
                "previous_status": current_status,
                "new_status": new_status.value
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Error updating user status", user_id=user_id, error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to update user status"
                }
            )
    
    async def update_user_role(
        self,
        user_id: str,
        new_role: UserRole,
        reason: str,
        admin_id: str
    ) -> Dict[str, Any]:
        """
        Update user role with audit logging
        
        Args:
            user_id: UUID of the user to update
            new_role: New user role
            reason: Reason for role change
            admin_id: UUID of the admin performing the action
            
        Returns:
            Success response with updated role
        """
        try:
            logger.info(
                "Updating user role",
                user_id=user_id,
                new_role=new_role,
                admin_id=admin_id
            )
            
            # Get current user role
            current_result = self.supabase.table("profiles")\
                .select("role, email")\
                .eq("id", user_id)\
                .execute()
            
            if not current_result.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "code": "USER_NOT_FOUND",
                        "message": "User not found"
                    }
                )
            
            current_role = current_result.data[0]["role"]
            user_email = current_result.data[0]["email"]
            
            # Update user role
            self.supabase.table("profiles")\
                .update({
                    "role": new_role.value,
                    "updated_at": datetime.utcnow().isoformat()
                })\
                .eq("id", user_id)\
                .execute()
            
            # Log admin action
            await self._log_admin_action(
                admin_id=admin_id,
                action="update_user_role",
                target_user_id=user_id,
                target_user_email=user_email,
                details={
                    "previous_role": current_role,
                    "new_role": new_role.value,
                    "reason": reason
                }
            )
            
            return {
                "message": "User role updated successfully",
                "user_id": user_id,
                "previous_role": current_role,
                "new_role": new_role.value
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Error updating user role", user_id=user_id, error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to update user role"
                }
            )
    
    async def bulk_update_users(
        self,
        bulk_request: BulkUserUpdateRequest,
        admin_id: str
    ) -> BulkUserUpdateResponse:
        """
        Perform bulk operations on multiple users
        
        Args:
            bulk_request: Bulk update request with user IDs and action
            admin_id: UUID of the admin performing the action
            
        Returns:
            BulkUserUpdateResponse with operation results
        """
        try:
            logger.info(
                "Performing bulk user update",
                action=bulk_request.action,
                user_count=len(bulk_request.user_ids),
                admin_id=admin_id
            )
            
            results = []
            updated_count = 0
            failed_count = 0
            
            for user_id in bulk_request.user_ids:
                try:
                    if bulk_request.action == "update_role":
                        new_role = UserRole(bulk_request.data["new_role"])
                        result = await self.update_user_role(
                            user_id=str(user_id),
                            new_role=new_role,
                            reason=bulk_request.data.get("reason", "Bulk role update"),
                            admin_id=admin_id
                        )
                        results.append({
                            "user_id": str(user_id),
                            "success": True,
                            "message": result["message"]
                        })
                        updated_count += 1
                    
                    elif bulk_request.action == "update_status":
                        new_status = UserStatus(bulk_request.data["new_status"])
                        result = await self.update_user_status(
                            user_id=str(user_id),
                            new_status=new_status,
                            reason=bulk_request.data.get("reason", "Bulk status update"),
                            admin_id=admin_id
                        )
                        results.append({
                            "user_id": str(user_id),
                            "success": True,
                            "message": result["message"]
                        })
                        updated_count += 1
                    
                    else:
                        results.append({
                            "user_id": str(user_id),
                            "success": False,
                            "error": "Invalid action"
                        })
                        failed_count += 1
                
                except Exception as e:
                    results.append({
                        "user_id": str(user_id),
                        "success": False,
                        "error": str(e)
                    })
                    failed_count += 1
            
            # Log bulk action
            await self._log_admin_action(
                admin_id=admin_id,
                action="bulk_update_users",
                target_user_id="bulk",
                details={
                    "action": bulk_request.action,
                    "data": bulk_request.data,
                    "updated_count": updated_count,
                    "failed_count": failed_count
                }
            )
            
            return BulkUserUpdateResponse(
                message=f"Bulk operation completed. Updated: {updated_count}, Failed: {failed_count}",
                updated_count=updated_count,
                failed_count=failed_count,
                results=results
            )
            
        except Exception as e:
            logger.error("Error in bulk user update", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to perform bulk operation"
                }
            )
    
    async def export_users(
        self,
        export_request: UserExportRequest,
        admin_id: str
    ) -> str:
        """
        Export user data in specified format
        
        Args:
            export_request: Export request with filters and format
            admin_id: UUID of the admin performing the action
            
        Returns:
            File path or data for download
        """
        try:
            logger.info(
                "Exporting user data",
                format=export_request.format,
                admin_id=admin_id
            )
            
            # Get users with filters
            user_list = await self.get_users(
                page=1,
                limit=10000,  # Large limit for export
                role=export_request.role,
                status=export_request.status,
                date_from=export_request.date_from,
                date_to=export_request.date_to
            )
            
            # Generate export data
            if export_request.format == "csv":
                csv_data = self._generate_csv_export(user_list.users)
                
                # Log export action
                await self._log_admin_action(
                    admin_id=admin_id,
                    action="export_users",
                    target_user_id="bulk",
                    details={
                        "format": export_request.format,
                        "filters": {
                            "role": export_request.role,
                            "status": export_request.status,
                            "date_from": export_request.date_from,
                            "date_to": export_request.date_to
                        },
                        "export_count": len(user_list.users)
                    }
                )
                
                return csv_data
            
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "code": "INVALID_FORMAT",
                        "message": "Unsupported export format"
                    }
                )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Error exporting user data", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to export user data"
                }
            )
    
    async def _get_user_stats(self) -> UserStats:
        """Get user statistics for dashboard"""
        try:
            # Get total users by status
            status_result = self.supabase.table("profiles")\
                .select("account_status")\
                .execute()
            
            status_counts = {"active": 0, "blocked": 0, "pending": 0}
            for user in status_result.data or []:
                status = user.get("account_status", "active")
                if status in status_counts:
                    status_counts[status] += 1
            
            # Get users by role
            role_result = self.supabase.table("profiles")\
                .select("role")\
                .execute()
            
            role_counts = {}
            for user in role_result.data or []:
                role = user.get("role", "CITIZEN")
                role_counts[role] = role_counts.get(role, 0) + 1
            
            # Get registration statistics
            now = datetime.utcnow()
            today = now.replace(hour=0, minute=0, second=0, microsecond=0)
            week_ago = today - timedelta(days=7)
            month_ago = today - timedelta(days=30)
            
            # Today's registrations
            today_result = self.supabase.table("profiles")\
                .select("id")\
                .gte("created_at", today.isoformat())\
                .execute()
            registrations_today = len(today_result.data) if today_result.data else 0
            
            # This week's registrations
            week_result = self.supabase.table("profiles")\
                .select("id")\
                .gte("created_at", week_ago.isoformat())\
                .execute()
            registrations_this_week = len(week_result.data) if week_result.data else 0
            
            # This month's registrations
            month_result = self.supabase.table("profiles")\
                .select("id")\
                .gte("created_at", month_ago.isoformat())\
                .execute()
            registrations_this_month = len(month_result.data) if month_result.data else 0
            
            total_users = len(status_result.data) if status_result.data else 0
            
            return UserStats(
                total_users=total_users,
                active_users=status_counts["active"],
                blocked_users=status_counts["blocked"],
                pending_users=status_counts["pending"],
                users_by_role=role_counts,
                registrations_today=registrations_today,
                registrations_this_week=registrations_this_week,
                registrations_this_month=registrations_this_month
            )
            
        except Exception as e:
            logger.error("Error getting user stats", error=str(e))
            # Return default stats on error
            return UserStats(
                total_users=0,
                active_users=0,
                blocked_users=0,
                pending_users=0,
                users_by_role={},
                registrations_today=0,
                registrations_this_week=0,
                registrations_this_month=0
            )
    
    async def _get_user_devices_count(self, user_id: str) -> int:
        """Get count of IoT devices for a user"""
        try:
            result = self.supabase.table("iot_devices")\
                .select("id")\
                .eq("farmer_id", user_id)\
                .execute()
            return len(result.data) if result.data else 0
        except:
            return 0
    
    async def _get_user_listings_count(self, user_id: str) -> int:
        """Get count of farm listings for a user"""
        try:
            result = self.supabase.table("farm_listings")\
                .select("id")\
                .eq("farmer_id", user_id)\
                .execute()
            return len(result.data) if result.data else 0
        except:
            return 0
    
    async def _get_user_reservations_count(self, user_id: str) -> int:
        """Get count of meal reservations for a user"""
        try:
            result = self.supabase.table("meal_reservations")\
                .select("id")\
                .eq("citizen_id", user_id)\
                .execute()
            return len(result.data) if result.data else 0
        except:
            return 0
    
    async def _get_user_orders_count(self, user_id: str) -> int:
        """Get count of orders for a user"""
        try:
            result = self.supabase.table("farm_orders")\
                .select("id")\
                .eq("buyer_id", user_id)\
                .execute()
            return len(result.data) if result.data else 0
        except:
            return 0
    
    def _is_valid_status_transition(
        self, 
        current_status: str, 
        new_status: UserStatus
    ) -> bool:
        """Validate if status transition is allowed"""
        # All transitions are allowed for now
        # You can add business logic here if needed
        return True
    
    async def _log_admin_action(
        self,
        admin_id: str,
        action: str,
        target_user_id: str,
        target_user_email: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log admin action for audit purposes"""
        try:
            # Get admin email
            admin_result = self.supabase.table("profiles")\
                .select("email")\
                .eq("id", admin_id)\
                .execute()
            
            admin_email = admin_result.data[0]["email"] if admin_result.data else "unknown"
            
            log_entry = {
                "id": str(uuid.uuid4()),
                "admin_id": admin_id,
                "admin_email": admin_email,
                "action": action,
                "target_user_id": target_user_id,
                "target_user_email": target_user_email,
                "details": details or {},
                "ip_address": "127.0.0.1",  # Will be updated from request
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.supabase.table("admin_audit_logs")\
                .insert(log_entry)\
                .execute()
            
            logger.info("Admin action logged", action=action, admin_id=admin_id)
            
        except Exception as e:
            logger.error("Failed to log admin action", error=str(e))
            # Don't raise exception for logging failures
    
    def _generate_csv_export(self, users: List[AdminUserView]) -> str:
        """Generate CSV export data"""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            "ID",
            "Email",
            "Full Name",
            "Phone",
            "Role",
            "Status",
            "Created At",
            "Last Login",
            "Devices Count",
            "Listings Count",
            "Reservations Count",
            "Orders Count"
        ])
        
        # Write user data
        for user in users:
            writer.writerow([
                str(user.id),
                user.email,
                user.full_name,
                user.phone or "",
                user.role,
                user.account_status,
                user.created_at,
                user.last_login or "",
                user.devices_count,
                user.listings_count,
                user.reservations_count,
                user.orders_count
            ])
        
        return output.getvalue()
