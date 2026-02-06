"""
User Service
Business logic for user management
"""

from sqlalchemy.orm import Session
from typing import List, Optional

from backend.api.models.user import User
from backend.api.schemas.schemas import UserCreate, UserUpdate
from backend.core.security import hash_password
from backend.core.config import get_settings
from backend.core.database import SessionLocal

settings = get_settings()


def create_user(db: Session, user_data: UserCreate) -> User:
    """Create a new user"""
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise ValueError(f"Username '{user_data.username}' already exists")
    
    # Hash password
    password_hash = hash_password(user_data.password)
    
    # Create user
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=password_hash,
        quota_gb=user_data.quota_gb,
        is_admin=user_data.is_admin
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


def get_user(db: Session, user_id: str) -> Optional[User]:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username"""
    return db.query(User).filter(User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Get all users with pagination"""
    return db.query(User).offset(skip).limit(limit).all()


def update_user(db: Session, user_id: str, user_data: UserUpdate) -> Optional[User]:
    """Update user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    
    # Update fields
    if user_data.email is not None:
        user.email = user_data.email
    if user_data.password is not None:
        user.password_hash = hash_password(user_data.password)
    if user_data.quota_gb is not None:
        user.quota_gb = user_data.quota_gb
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    if user_data.is_admin is not None:
        user.is_admin = user_data.is_admin
    
    db.commit()
    db.refresh(user)
    
    return user


def delete_user(db: Session, user_id: str) -> bool:
    """Delete user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False
    
    db.delete(user)
    db.commit()
    
    return True


def create_default_admin():
    """Create default admin user if not exists"""
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == settings.admin_username).first()
        if not admin:
            admin_data = UserCreate(
                username=settings.admin_username,
                password=settings.admin_password,
                email=settings.admin_email,
                quota_gb=1000,
                is_admin=True
            )
            create_user(db, admin_data)
            print(f"Created default admin user: {settings.admin_username}")
        else:
            print("Default admin user already exists")
    finally:
        db.close()
