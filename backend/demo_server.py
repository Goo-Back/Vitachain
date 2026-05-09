"""
VitaChain Demo Server
Simplified version to showcase implemented features without complex dependencies
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid
import json

# Create FastAPI app
app = FastAPI(
    title="VitaChain Demo API",
    description="Demo of VitaChain Implementation - Epics 1 & 2",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Demo data storage (in production, this would be in Supabase)
demo_users = []
demo_sessions = {}
demo_audit_logs = []

# Pydantic Models
class UserRole(str):
    FARMER = "FARMER"
    RESTAURANT = "RESTAURANT"
    CITIZEN = "CITIZEN"
    ADMIN = "ADMIN"

class UserRegistrationRequest(BaseModel):
    email: EmailStr
    role: str
    full_name: str

class UserRegistrationResponse(BaseModel):
    message: str
    user_id: str
    email_sent: bool

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserLoginResponse(BaseModel):
    message: str
    user: Dict[str, Any]
    redirect_to: str

class ProfileViewResponse(BaseModel):
    id: str
    email: str
    full_name: str
    phone: Optional[str]
    role: str
    created_at: str
    updated_at: str
    role_data: Optional[Dict[str, Any]]

class AdminUserView(BaseModel):
    id: str
    email: str
    full_name: str
    phone: Optional[str]
    role: str
    account_status: str
    created_at: str
    updated_at: str
    last_login: Optional[str]
    devices_count: int
    listings_count: int
    reservations_count: int
    orders_count: int

class UserStats(BaseModel):
    total_users: int
    active_users: int
    blocked_users: int
    pending_users: int
    users_by_role: Dict[str, int]
    registrations_today: int
    registrations_this_week: int
    registrations_this_month: int

class UserListResponse(BaseModel):
    users: List[AdminUserView]
    pagination: Dict[str, Any]
    stats: UserStats

# Helper functions
def create_demo_user(email: str, role: str, full_name: str) -> Dict[str, Any]:
    """Create a demo user"""
    user_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    
    return {
        "id": user_id,
        "email": email,
        "full_name": full_name,
        "phone": None,
        "role": role,
        "account_status": "active",
        "created_at": now,
        "updated_at": now,
        "last_login": None,
        "devices_count": 0,
        "listings_count": 0,
        "reservations_count": 0,
        "orders_count": 0,
        "role_data": {}
    }

def add_audit_log(admin_id: str, action: str, details: Dict[str, Any]):
    """Add audit log entry"""
    demo_audit_logs.append({
        "id": str(uuid.uuid4()),
        "admin_id": admin_id,
        "action": action,
        "details": details,
        "timestamp": datetime.now().isoformat()
    })

# API Endpoints

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "VitaChain Demo API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "implemented_features": {
            "epic_1": ["Platform Foundation", "Security", "Caching", "Monitoring"],
            "epic_2": ["User Registration", "Authentication", "Profile Management", "Admin Dashboard"]
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "api": "running",
            "database": "simulated",
            "cache": "simulated",
            "auth": "running"
        }
    }

@app.post("/api/auth/register", response_model=UserRegistrationResponse)
async def register_user(request: UserRegistrationRequest):
    """Register a new user"""
    # Check if user already exists
    for user in demo_users:
        if user["email"] == request.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "EMAIL_EXISTS", "message": "Email already registered"}
            )
    
    # Create new user
    user = create_demo_user(request.email, request.role, request.full_name)
    demo_users.append(user)
    
    return UserRegistrationResponse(
        message="User registered successfully",
        user_id=user["id"],
        email_sent=True
    )

@app.post("/api/auth/login", response_model=UserLoginResponse)
async def login_user(request: UserLoginRequest):
    """Login user"""
    # Find user
    user = None
    for u in demo_users:
        if u["email"] == request.email:
            user = u
            break
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_CREDENTIALS", "message": "Invalid email or password"}
        )
    
    # Update last login
    user["last_login"] = datetime.now().isoformat()
    
    # Create session
    session_id = str(uuid.uuid4())
    demo_sessions[session_id] = {
        "user_id": user["id"],
        "email": user["email"],
        "role": user["role"],
        "created_at": datetime.now().isoformat()
    }
    
    return UserLoginResponse(
        message="Login successful",
        user=user,
        redirect_to=f"/dashboard/{user['role'].lower()}"
    )

@app.get("/api/profiles/me", response_model=ProfileViewResponse)
async def get_my_profile():
    """Get current user profile (demo)"""
    # Return first demo user for demo purposes
    if demo_users:
        user = demo_users[0]
        return ProfileViewResponse(**user)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "PROFILE_NOT_FOUND", "message": "Profile not found"}
        )

@app.get("/api/admin/users", response_model=UserListResponse)
async def get_admin_users():
    """Get all users (admin endpoint)"""
    # Calculate stats
    total_users = len(demo_users)
    active_users = len([u for u in demo_users if u["account_status"] == "active"])
    blocked_users = len([u for u in demo_users if u["account_status"] == "blocked"])
    pending_users = len([u for u in demo_users if u["account_status"] == "pending"])
    
    users_by_role = {}
    for user in demo_users:
        role = user["role"]
        users_by_role[role] = users_by_role.get(role, 0) + 1
    
    stats = UserStats(
        total_users=total_users,
        active_users=active_users,
        blocked_users=blocked_users,
        pending_users=pending_users,
        users_by_role=users_by_role,
        registrations_today=total_users,  # Demo: all are today
        registrations_this_week=total_users,
        registrations_this_month=total_users
    )
    
    return UserListResponse(
        users=[AdminUserView(**user) for user in demo_users],
        pagination={"page": 1, "limit": 20, "total": total_users},
        stats=stats
    )

@app.get("/api/admin/stats")
async def get_admin_stats():
    """Get admin dashboard statistics"""
    return {
        "user_statistics": {
            "total_users": len(demo_users),
            "active_users": len([u for u in demo_users if u["account_status"] == "active"]),
            "new_registrations_today": len(demo_users),
            "registration_growth": "+15% this week"
        },
        "system_health": {
            "api_response_time": "45ms",
            "database_response_time": "12ms",
            "cache_hit_rate": "94%",
            "uptime": "99.9%"
        },
        "security_metrics": {
            "failed_login_attempts": 3,
            "suspicious_activities": 0,
            "blocked_ips": 0,
            "active_sessions": len(demo_sessions)
        },
        "feature_usage": {
            "registrations": len(demo_users),
            "profile_updates": 12,
            "admin_actions": len(demo_audit_logs),
            "api_calls": 1247
        }
    }

@app.get("/api/admin/audit-logs")
async def get_audit_logs():
    """Get admin audit logs"""
    return {
        "logs": demo_audit_logs[-10:],  # Last 10 logs
        "total_count": len(demo_audit_logs),
        "filters_applied": {}
    }

# Demo data initialization
def initialize_demo_data():
    """Initialize demo data"""
    # Create demo users
    demo_users.extend([
        create_demo_user("farmer@vitachain.ma", "FARMER", "Mohammed Farmer"),
        create_demo_user("restaurant@vitachain.ma", "RESTAURANT", "Restaurant Owner"),
        create_demo_user("citizen@vitachain.ma", "CITIZEN", "Happy Customer"),
        create_demo_user("admin@vitachain.ma", "ADMIN", "System Admin")
    ])
    
    # Add some demo audit logs
    add_audit_log(
        admin_id=demo_users[3]["id"],
        action="USER_CREATED",
        details={"user_email": "farmer@vitachain.ma", "role": "FARMER"}
    )
    
    print("🚀 VitaChain Demo Server Started!")
    print("📊 Demo users created:", len(demo_users))
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔧 Health Check: http://localhost:8000/health")

if __name__ == "__main__":
    # Initialize demo data
    initialize_demo_data()
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
