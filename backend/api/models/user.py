"""
Database Models
SQLAlchemy ORM models for the database
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Integer, Float, DateTime, JSON, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
import enum

from backend.core.database import Base


def generate_uuid():
    """Generate UUID as string"""
    return str(uuid.uuid4())


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), nullable=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Quota (in GB)
    quota_gb = Column(Integer, default=100, nullable=False)
    used_space_gb = Column(Float, default=0.0, nullable=False)
    
    # Relationships
    protocol_accesses = relationship("UserProtocolAccess", back_populates="user", cascade="all, delete-orphan")
    access_logs = relationship("AccessLog", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"


class ProtocolStatus(str, enum.Enum):
    """Protocol service status"""
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    INSTALLING = "installing"
    UNINSTALLED = "uninstalled"


class Protocol(Base):
    """Protocol configuration model"""
    __tablename__ = "protocols"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(50), unique=True, nullable=False, index=True)  # FTP, SFTP, NFS, etc.
    display_name = Column(String(100), nullable=False)
    is_enabled = Column(Boolean, default=False, nullable=False)
    is_installed = Column(Boolean, default=False, nullable=False)
    port = Column(Integer, nullable=True)
    ssl_enabled = Column(Boolean, default=False, nullable=False)
    config_json = Column(JSON, nullable=True)  # Protocol-specific configuration
    status = Column(SQLEnum(ProtocolStatus), default=ProtocolStatus.UNINSTALLED, nullable=False)
    installed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user_accesses = relationship("UserProtocolAccess", back_populates="protocol", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Protocol(name='{self.name}', status='{self.status}')>"


class SharedPath(Base):
    """Shared path configuration"""
    __tablename__ = "shared_paths"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    path = Column(String(500), nullable=False)  # Absolute filesystem path
    description = Column(Text, nullable=True)
    protocols = Column(JSON, nullable=False)  # List of protocol names that can access this path
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user_accesses = relationship("UserProtocolAccess", back_populates="shared_path", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<SharedPath(name='{self.name}', path='{self.path}')>"


class PermissionLevel(str, enum.Enum):
    """Access permission levels"""
    READ = "read"
    WRITE = "write"
    FULL = "full"


class UserProtocolAccess(Base):
    """User access permissions for protocols and shared paths"""
    __tablename__ = "user_protocol_access"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    protocol_id = Column(String(36), ForeignKey("protocols.id"), nullable=False)
    shared_path_id = Column(String(36), ForeignKey("shared_paths.id"), nullable=False)
    permission = Column(SQLEnum(PermissionLevel), default=PermissionLevel.READ, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="protocol_accesses")
    protocol = relationship("Protocol", back_populates="user_accesses")
    shared_path = relationship("SharedPath", back_populates="user_accesses")
    
    def __repr__(self):
        return f"<UserProtocolAccess(user_id='{self.user_id}', protocol_id='{self.protocol_id}', permission='{self.permission}')>"


class ActionType(str, enum.Enum):
    """Types of logged actions"""
    LOGIN = "login"
    LOGOUT = "logout"
    UPLOAD = "upload"
    DOWNLOAD = "download"
    DELETE = "delete"
    RENAME = "rename"
    MKDIR = "mkdir"
    RMDIR = "rmdir"
    LIST = "list"
    CHMOD = "chmod"


class ActionStatus(str, enum.Enum):
    """Status of logged actions"""
    SUCCESS = "success"
    FAILED = "failed"
    DENIED = "denied"


class AccessLog(Base):
    """Access and operation logs"""
    __tablename__ = "access_logs"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)  # Nullable for failed login attempts
    username = Column(String(100), nullable=True)  # Denormalized for performance
    protocol = Column(String(50), nullable=False)
    action = Column(SQLEnum(ActionType), nullable=False)
    file_path = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 max length
    user_agent = Column(String(500), nullable=True)
    status = Column(SQLEnum(ActionStatus), default=ActionStatus.SUCCESS, nullable=False)
    error_message = Column(Text, nullable=True)
    file_size_bytes = Column(Integer, nullable=True)  # For uploads/downloads
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="access_logs")
    
    def __repr__(self):
        return f"<AccessLog(user='{self.username}', protocol='{self.protocol}', action='{self.action}', timestamp='{self.timestamp}')>"


class SystemSetting(Base):
    """System-wide settings"""
    __tablename__ = "system_settings"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(JSON, nullable=True)
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<SystemSetting(key='{self.key}')>"
