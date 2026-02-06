"""
Users Routes
CRUD operations for user management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.core.database import get_db
from backend.core.security import get_current_active_admin, get_current_user
from backend.api.models.user import User
from backend.api.schemas.schemas import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserUsageResponse,
    MessageResponse
)
from backend.api.services import user_service

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    """List all users (admin only)"""
    users = user_service.get_users(db, skip=skip, limit=limit)
    return users


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    """Create a new user (admin only)"""
    try:
        user = user_service.create_user(db, user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user details (users can see their own, admins can see all)"""
    # Users can only see themselves unless they're admin
    if not current_user.is_admin and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    user = user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user (users can update themselves, admins can update all)"""
    # Users can only update themselves unless they're admin
    if not current_user.is_admin and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Non-admins cannot promote themselves to admin
    if not current_user.is_admin and user_data.is_admin is True:
        raise HTTPException(status_code=403, detail="Cannot change admin status")
    
    user = user_service.update_user(db, user_id, user_data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: str,
    current_user: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    """Delete user (admin only)"""
    # Prevent deleting yourself
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    success = user_service.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User deleted successfully"}


@router.get("/{user_id}/usage", response_model=UserUsageResponse)
async def get_user_usage(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user storage usage"""
    # Users can only see their own usage unless they're admin
    if not current_user.is_admin and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    user = user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    usage_percent = (user.used_space_gb / user.quota_gb * 100) if user.quota_gb > 0 else 0
    remaining_gb = max(0, user.quota_gb - user.used_space_gb)
    
    return {
        "user_id": user.id,
        "username": user.username,
        "quota_gb": user.quota_gb,
        "used_space_gb": user.used_space_gb,
        "usage_percent": round(usage_percent, 2),
        "remaining_gb": round(remaining_gb, 2)
    }
