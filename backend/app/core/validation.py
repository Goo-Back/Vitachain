"""
Validation utilities for VitaChain API
Handles phone number validation and other input validation
"""

import re
from typing import Optional


class PhoneValidator:
    """Validates phone numbers with Moroccan format support"""
    
    # Moroccan phone patterns
    patterns = [
        r'^\+2126\d{8}$',    # +2126XXXXXXXX
        r'^\+2127\d{8}$',    # +2127XXXXXXXX
        r'^06\d{8}$',        # 06XXXXXXXX
        r'^07\d{8}$'         # 07XXXXXXXX
    ]
    
    @classmethod
    def validate_moroccan_phone(cls, phone: str) -> tuple[bool, Optional[str]]:
        """
        Validate Moroccan phone number format
        
        Args:
            phone: Phone number to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if phone is None:
            return True, None  # Phone is optional
        
        if not phone.strip():
            return False, "Phone number cannot be empty"
        
        # Remove spaces and special characters
        clean_phone = re.sub(r'[^\d+]', '', phone)
        
        # Check against Moroccan patterns
        for pattern in cls.patterns:
            if re.match(pattern, clean_phone):
                return True, None
        
        return False, "Invalid Moroccan phone number format. Expected formats: +2126XXXXXXXX, +2127XXXXXXXX, 06XXXXXXXX, or 07XXXXXXXX"
    
    @classmethod
    def format_phone_number(cls, phone: str) -> Optional[str]:
        """
        Format phone number to standard format
        
        Args:
            phone: Phone number to format
            
        Returns:
            Formatted phone number or None if invalid
        """
        if not phone:
            return None
        
        # Remove spaces and special characters
        clean_phone = re.sub(r'[^\d+]', '', phone)
        
        # Format to international format
        if clean_phone.startswith('06') and len(clean_phone) == 10:
            return f'+212{clean_phone[1:]}'
        elif clean_phone.startswith('07') and len(clean_phone) == 10:
            return f'+212{clean_phone[1:]}'
        elif clean_phone.startswith('+2126') and len(clean_phone) == 13:
            return clean_phone
        elif clean_phone.startswith('+2127') and len(clean_phone) == 13:
            return clean_phone
        
        # Return original phone if no formatting applied
        return phone if phone else None


class ProfileValidator:
    """Validates profile data and fields"""
    
    @staticmethod
    def validate_full_name(full_name: str) -> tuple[bool, Optional[str]]:
        """
        Validate full name field
        
        Args:
            full_name: Full name to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not full_name or not full_name.strip():
            return False, "Full name is required"
        
        if len(full_name.strip()) < 2:
            return False, "Full name must be at least 2 characters long"
        
        if len(full_name.strip()) > 100:
            return False, "Full name cannot exceed 100 characters"
        
        # Check for valid characters (letters, spaces, hyphens, apostrophes)
        if not re.match(r'^[a-zA-Z\u0600-\u06FF\s\-\'\.]+$', full_name.strip()):
            return False, "Full name contains invalid characters"
        
        return True, None
    
    @staticmethod
    def validate_role_data(role: str, role_data: dict) -> tuple[bool, Optional[str]]:
        """
        Validate role-specific data
        
        Args:
            role: User role (FARMER, RESTAURANT, CITIZEN)
            role_data: Role-specific data to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not role_data:
            return True, None  # Role data is optional
        
        if role == "FARMER":
            return ProfileValidator._validate_farmer_data(role_data)
        elif role == "RESTAURANT":
            return ProfileValidator._validate_restaurant_data(role_data)
        elif role == "CITIZEN":
            return ProfileValidator._validate_citizen_data(role_data)
        else:
            return False, f"Invalid role: {role}"
    
    @staticmethod
    def _validate_farmer_data(data: dict) -> tuple[bool, Optional[str]]:
        """Validate farmer-specific data"""
        if 'farm_size_hectares' in data:
            try:
                size = float(data['farm_size_hectares'])
                if size < 0:
                    return False, "Farm size cannot be negative"
                if size > 10000:  # Reasonable upper limit
                    return False, "Farm size seems too large"
            except (ValueError, TypeError):
                return False, "Invalid farm size value"
        
        if 'main_crops' in data:
            crops = data['main_crops']
            if not isinstance(crops, list):
                return False, "Main crops must be a list"
            if len(crops) > 20:  # Reasonable limit
                return False, "Too many crops specified"
        
        return True, None
    
    @staticmethod
    def _validate_restaurant_data(data: dict) -> tuple[bool, Optional[str]]:
        """Validate restaurant-specific data"""
        if 'restaurant_name' in data:
            name = data['restaurant_name']
            if not isinstance(name, str) or len(name.strip()) < 2:
                return False, "Restaurant name must be at least 2 characters"
            if len(name.strip()) > 100:
                return False, "Restaurant name cannot exceed 100 characters"
        
        if 'cuisine_type' in data:
            cuisine = data['cuisine_type']
            if not isinstance(cuisine, str) or len(cuisine.strip()) < 2:
                return False, "Cuisine type must be at least 2 characters"
            if len(cuisine.strip()) > 50:
                return False, "Cuisine type cannot exceed 50 characters"
        
        return True, None
    
    @staticmethod
    def _validate_citizen_data(data: dict) -> tuple[bool, Optional[str]]:
        """Validate citizen-specific data"""
        if 'preferred_pickup_locations' in data:
            locations = data['preferred_pickup_locations']
            if not isinstance(locations, list):
                return False, "Preferred pickup locations must be a list"
            if len(locations) > 10:  # Reasonable limit
                return False, "Too many pickup locations specified"
        
        return True, None


class InputSanitizer:
    """Sanitizes user input to prevent injection attacks"""
    
    @staticmethod
    def sanitize_string(value: str) -> str:
        """
        Sanitize string input
        
        Args:
            value: String to sanitize
            
        Returns:
            Sanitized string
        """
        if not isinstance(value, str):
            return str(value)
        
        # Remove potentially dangerous characters
        sanitized = value.replace("<", "&lt;").replace(">", "&gt;")
        sanitized = sanitized.replace('"', "&quot;").replace("'", "&#x27;")
        
        return sanitized.strip()
    
    @staticmethod
    def sanitize_profile_data(data: dict) -> dict:
        """
        Sanitize profile data
        
        Args:
            data: Profile data to sanitize
            
        Returns:
            Sanitized profile data
        """
        sanitized = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = InputSanitizer.sanitize_string(value)
            elif isinstance(value, dict):
                sanitized[key] = InputSanitizer.sanitize_profile_data(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    InputSanitizer.sanitize_string(item) if isinstance(item, str) else item
                    for item in value
                ]
            else:
                sanitized[key] = value
        
        return sanitized
