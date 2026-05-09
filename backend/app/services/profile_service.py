"""
Profile Service for VitaChain
Handles profile management business logic and database operations
"""

from datetime import datetime
from typing import Optional, Dict, Any
import structlog
from fastapi import HTTPException, status
from app.core.config import settings
from app.core.validation import PhoneValidator, ProfileValidator, InputSanitizer

logger = structlog.get_logger("profile_service")


class ProfileService:
    """Service for managing user profiles"""
    
    def __init__(self, supabase_client):
        self.supabase = supabase_client
        self.phone_validator = PhoneValidator()
        self.profile_validator = ProfileValidator()
        self.input_sanitizer = InputSanitizer()
    
    async def get_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Get user profile with role-specific data
        
        Args:
            user_id: User ID from JWT token
            
        Returns:
            User profile data with role-specific information
            
        Raises:
            HTTPException: If profile not found
        """
        try:
            logger.info("Fetching profile", user_id=user_id)
            
            # Get base profile data
            result = self.supabase.table('user_profiles').select('*').eq('user_id', user_id).single()
            
            if hasattr(result, 'error') and result.error:
                logger.error("Database error fetching profile", user_id=user_id, error=result.error)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "code": "DATABASE_ERROR",
                        "message": "Failed to fetch profile data"
                    }
                )
            
            if not result.data:
                logger.warning("Profile not found", user_id=user_id)
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "code": "PROFILE_NOT_FOUND",
                        "message": "User profile not found"
                    }
                )
            
            profile = result.data
            
            # Get user email from auth.users
            user_result = self.supabase.auth.admin.get_user(user_id)
            if user_result and hasattr(user_result, 'user'):
                profile['email'] = user_result.user.email
            
            # Combine first_name and last_name into full_name for consistency
            if profile.get('first_name') or profile.get('last_name'):
                profile['full_name'] = f"{profile.get('first_name', '')} {profile.get('last_name', '')}".strip()
            else:
                profile['full_name'] = profile.get('full_name', '')
            
            # Add role-specific data
            role = profile.get('role')
            if role:
                role_data = await self._get_role_specific_data(user_id, role)
                profile['role_data'] = role_data
            
            logger.info("Profile retrieved successfully", user_id=user_id, role=role)
            return profile
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Error fetching profile", user_id=user_id, error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to fetch profile"
                }
            )
    
    async def update_profile(self, user_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update user profile with validation
        
        Args:
            user_id: User ID from JWT token
            profile_data: Profile data to update
            
        Returns:
            Updated profile data
            
        Raises:
            HTTPException: If validation fails or update fails
        """
        try:
            logger.info("Updating profile", user_id=user_id)
            
            # Sanitize input data
            sanitized_data = self.input_sanitizer.sanitize_profile_data(profile_data)
            
            # Validate full name if provided
            if 'full_name' in sanitized_data:
                is_valid, error_msg = self.profile_validator.validate_full_name(sanitized_data['full_name'])
                if not is_valid:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail={
                            "code": "VALIDATION_ERROR",
                            "message": error_msg,
                            "details": {
                                "field": "full_name",
                                "constraint": "Must be 2-100 characters, letters only"
                            }
                        }
                    )
            
            # Validate phone number if provided
            if 'phone' in sanitized_data and sanitized_data['phone']:
                is_valid, error_msg = self.phone_validator.validate_moroccan_phone(sanitized_data['phone'])
                if not is_valid:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail={
                            "code": "VALIDATION_ERROR",
                            "message": error_msg,
                            "details": {
                                "field": "phone",
                                "constraint": "Must be valid Moroccan phone number"
                            }
                        }
                    )
                
                # Format phone number
                sanitized_data['phone'] = self.phone_validator.format_phone_number(sanitized_data['phone'])
            
            # Get current profile to check role
            current_profile = await self.get_profile(user_id)
            current_role = current_profile.get('role')
            
            # Validate role-specific data if provided
            if 'role_data' in sanitized_data and sanitized_data['role_data']:
                is_valid, error_msg = self.profile_validator.validate_role_data(
                    current_role, 
                    sanitized_data['role_data']
                )
                if not is_valid:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail={
                            "code": "VALIDATION_ERROR",
                            "message": error_msg,
                            "details": {
                                "field": "role_data",
                                "constraint": "Invalid role-specific data"
                            }
                        }
                    )
            
            # Remove protected fields that users shouldn't modify
            protected_fields = ['id', 'role', 'created_at', 'email']
            for field in protected_fields:
                sanitized_data.pop(field, None)
            
            # Add update timestamp
            sanitized_data['updated_at'] = datetime.utcnow().isoformat()
            
            # Split full_name into first_name and last_name for database
            if 'full_name' in sanitized_data:
                full_name = sanitized_data.pop('full_name')
                name_parts = full_name.strip().split(' ', 1)
                sanitized_data['first_name'] = name_parts[0]
                sanitized_data['last_name'] = name_parts[1] if len(name_parts) > 1 else ''
            
            # Update profile
            result = self.supabase.table('user_profiles').update(sanitized_data).eq('user_id', user_id).execute()
            
            if hasattr(result, 'error') and result.error:
                logger.error("Database error updating profile", user_id=user_id, error=result.error)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "code": "DATABASE_ERROR",
                        "message": "Failed to update profile data"
                    }
                )
            
            if not result.data:
                logger.error("Profile update failed", user_id=user_id)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "code": "INTERNAL_ERROR",
                        "message": "Failed to update profile"
                    }
                )
            
            # Update role-specific data if provided
            if 'role_data' in sanitized_data and sanitized_data['role_data']:
                await self._update_role_specific_data(user_id, current_role, sanitized_data['role_data'])
            
            # Get updated profile
            updated_profile = await self.get_profile(user_id)
            
            logger.info("Profile updated successfully", user_id=user_id)
            
            return {
                "message": "Profile updated successfully",
                "profile": updated_profile
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Error updating profile", user_id=user_id, error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to update profile"
                }
            )
    
    async def _get_role_specific_data(self, user_id: str, role: str) -> Optional[Dict[str, Any]]:
        """
        Get role-specific data for user
        
        Args:
            user_id: User ID
            role: User role
            
        Returns:
            Role-specific data or None
        """
        try:
            # For now, store role data in a JSON column in user_profiles table
            # In future, could be moved to separate tables
            result = self.supabase.table('user_profiles').select('role_data').eq('user_id', user_id).single()
            
            if result.data and result.data.get('role_data'):
                return result.data['role_data']
            
            # Return default structure based on role
            if role == 'FARMER':
                return {
                    "farm_location": None,
                    "farm_size_hectares": None,
                    "main_crops": []
                }
            elif role == 'RESTAURANT':
                return {
                    "restaurant_name": None,
                    "address": None,
                    "cuisine_type": None
                }
            elif role == 'CITIZEN':
                return {
                    "preferred_pickup_locations": []
                }
            
            return None
            
        except Exception as e:
            logger.warning("Error getting role-specific data", user_id=user_id, role=role, error=str(e))
            return None
    
    async def _update_role_specific_data(self, user_id: str, role: str, role_data: Dict[str, Any]) -> bool:
        """
        Update role-specific data for user
        
        Args:
            user_id: User ID
            role: User role
            role_data: Role-specific data to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Update role_data column in user_profiles table
            result = self.supabase.table('user_profiles').update({
                'role_data': role_data,
                'updated_at': datetime.utcnow().isoformat()
            }).eq('user_id', user_id).execute()
            
            return bool(result.data)
            
        except Exception as e:
            logger.error("Error updating role-specific data", user_id=user_id, role=role, error=str(e))
            return False
    
    async def validate_profile_access(self, user_id: str, target_user_id: str) -> bool:
        """
        Validate that user can access target profile
        
        Args:
            user_id: Current user ID from JWT
            target_user_id: Target profile user ID
            
        Returns:
            True if access allowed, False otherwise
        """
        # Users can only access their own profile (unless admin)
        return user_id == target_user_id
    
    async def get_profile_summary(self, user_id: str) -> Dict[str, Any]:
        """
        Get profile summary for dashboard display
        
        Args:
            user_id: User ID
            
        Returns:
            Profile summary data
        """
        try:
            profile = await self.get_profile(user_id)
            
            # Return summary data
            return {
                "id": profile.get('id'),
                "full_name": profile.get('full_name'),
                "role": profile.get('role'),
                "phone": profile.get('phone'),
                "completed_profile": self._is_profile_complete(profile),
                "last_updated": profile.get('updated_at')
            }
            
        except Exception as e:
            logger.error("Error getting profile summary", user_id=user_id, error=str(e))
            return {}
    
    def _is_profile_complete(self, profile: Dict[str, Any]) -> bool:
        """
        Check if user profile is complete
        
        Args:
            profile: Profile data
            
        Returns:
            True if profile is complete, False otherwise
        """
        # Check required fields
        if not profile.get('full_name'):
            return False
        
        # Check phone (optional but recommended)
        if not profile.get('phone'):
            return False
        
        # Check role-specific data
        role = profile.get('role')
        role_data = profile.get('role_data', {})
        
        if role == 'FARMER':
            return bool(role_data.get('farm_location'))
        elif role == 'RESTAURANT':
            return bool(role_data.get('restaurant_name') and role_data.get('address'))
        elif role == 'CITIZEN':
            return True  # Citizen profile is complete with basic info
        
        return True
