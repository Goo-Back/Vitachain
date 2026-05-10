"""Working authentication routes - simplified version"""

from fastapi import APIRouter, HTTPException, status, Depends, Request
from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum
import uuid
import json

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/auth", tags=["authentication"])

# Enums
class UserRole(str, Enum):
    FARMER = "FARMER"
    RESTAURANT = "RESTAURANT"
    CITIZEN = "CITIZEN"
    ADMIN = "ADMIN"

# Request/Response Models
class UserRegistrationRequest(BaseModel):
    email: EmailStr
    password: str
    role: UserRole
    full_name: str

class UserRegistrationResponse(BaseModel):
    message: str
    user_id: Optional[str] = None
    email_sent: bool = False

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    role: UserRole
    full_name: str

class LoginResponse(BaseModel):
    user: UserResponse
    message: str

# Simple in-memory user store for testing
test_users = {}

def get_client_ip(request: Request) -> str:
    """Get client IP from request."""
    return request.client.host if request.client else "unknown"

@router.post("/register", response_model=UserRegistrationResponse)
async def register_user_working(
    request: UserRegistrationRequest,
    http_request: Request
):
    """
    Working user registration
    """
    try:
        logger.info(f"Registration attempt: {request.email}")
        
        # Check if user already exists
        if request.email in test_users:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "USER_EXISTS", "message": "User already exists"}
            )
        
        # Create user
        user_id = str(uuid.uuid4())
        test_users[request.email] = {
            "id": user_id,
            "email": request.email,
            "password": request.password,  # In production, hash this
            "role": request.role,
            "full_name": request.full_name,
            "created_at": "2026-05-09T21:00:00Z"
        }
        
        logger.info(f"User created successfully: {request.email} ({user_id})")
        
        return UserRegistrationResponse(
            message="Registration successful! You can now log in.",
            user_id=user_id,
            email_sent=False  # Skip email for now
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "INTERNAL_ERROR", "message": str(e)}
        )

@router.post("/login", response_model=LoginResponse)
async def login_user_working(
    request: UserLoginRequest,
    http_request: Request
):
    """
    Working user login
    """
    try:
        logger.info(f"Login attempt: {request.email}")
        
        # Check if user exists
        if request.email not in test_users:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "INVALID_CREDENTIALS", "message": "Invalid email or password"}
            )
        
        user = test_users[request.email]
        
        # Check password
        if user["password"] != request.password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "INVALID_CREDENTIALS", "message": "Invalid email or password"}
            )
        
        logger.info(f"User logged in successfully: {request.email}")
        
        return LoginResponse(
            user=UserResponse(
                id=user["id"],
                email=user["email"],
                role=user["role"],
                full_name=user["full_name"]
            ),
            message="Login successful"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "INTERNAL_ERROR", "message": str(e)}
        )

@router.get("/me")
async def get_current_user_working():
    """
    Get current user (working version)
    """
    return {
        "message": "Working auth endpoint",
        "users_count": len(test_users),
        "users": list(test_users.keys())
    }

@router.get("/users")
async def list_test_users():
    """
    List all test users (for debugging)
    """
    return {
        "users": [
            {
                "id": user["id"],
                "email": user["email"],
                "role": user["role"],
                "full_name": user["full_name"]
            }
            for user in test_users.values()
        ],
        "count": len(test_users)
    }

@router.post("/clear-users")
async def clear_test_users():
    """
    Clear all test users (for debugging)
    """
    global test_users
    test_users.clear()
    return {"message": "All test users cleared", "count": 0}
