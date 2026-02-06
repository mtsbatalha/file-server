"""
Pydantic Schemas for API request/response validation
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ============================================================================
# Enums
# ============================================================================

class PermissionLevel(str, Enum):
    READ = "read"
    WRITE = "write"
    FULL = "full"


class ProtocolStatus(str, Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    INSTALLING = "installing"
    UNINSTALLED = "uninstalled"


class ActionType(str, Enum):
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


class ActionStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    DENIED = "denied"


# ============================================================================
# User Schemas
# ============================================================================

class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., min_length=3, max_length=100)
    email: Optional[EmailStr] = None


class UserCreate(UserBase):
    """Schema for creating a user"""
    password: str = Field(..., min_length=8)
    quota_gb: int = Field(default=100, ge=1, le=10000)
    is_admin: bool = False


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    quota_gb: Optional[int] = Field(None, ge=1, le=10000)
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response"""
    id: str
    is_active: bool
    is_admin: bool
    quota_gb: int
    used_space_gb: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserUsageResponse(BaseModel):
    """Schema for user storage usage"""
    user_id: str
    username: str
    quota_gb: int
    used_space_gb: float
    usage_percent: float
    remaining_gb: float


# ============================================================================
# Authentication Schemas
# ============================================================================

class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token payload"""
    username: Optional[str] = None


class LoginRequest(BaseModel):
    """Schema for login request"""
    username: str
    password: str


class RefreshRequest(BaseModel):
    """Schema for token refresh"""
    refresh_token: str


# ============================================================================
# Protocol Schemas
# ============================================================================

class ProtocolBase(BaseModel):
    """Base protocol schema"""
    name: str
    display_name: str
    port: Optional[int] = None
    ssl_enabled: bool = False
    config_json: Optional[dict] = None


class ProtocolCreate(ProtocolBase):
    """Schema for creating/installing a protocol"""
    pass


class ProtocolUpdate(BaseModel):
    """Schema for updating protocol configuration"""
    port: Optional[int] = None
    ssl_enabled: Optional[bool] = None
    config_json: Optional[dict] = None
    is_enabled: Optional[bool] = None


from pydantic import BaseModel, ConfigDict, computed_field

class ProtocolResponse(ProtocolBase):
    """Schema for protocol response"""
    id: str
    is_enabled: bool
    is_installed: bool
    status: ProtocolStatus
    installed_at: Optional[datetime] = None
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
    
    @computed_field
    @property
    def description(self) -> str:
        """Alias for display_name for frontend compatibility"""
        return self.display_name
    
    @computed_field
    @property
    def default_port(self) -> Optional[int]:
        """Alias for port for frontend compatibility"""
        return self.port


class ProtocolStatusResponse(BaseModel):
    """Detailed protocol status"""
    protocol_name: str
    status: ProtocolStatus
    is_running: bool
    pid: Optional[int] = None
    uptime_seconds: Optional[int] = None
    port: Optional[int] = None
    error_message: Optional[str] = None


# ============================================================================
# Shared Path Schemas
# ============================================================================

class SharedPathBase(BaseModel):
    """Base shared path schema"""
    name: str = Field(..., min_length=1, max_length=100)
    path: str = Field(..., min_length=1)
    description: Optional[str] = None
    protocols: List[str] = []


class SharedPathCreate(SharedPathBase):
    """Schema for creating a shared path"""
    pass


class SharedPathUpdate(BaseModel):
    """Schema for updating a shared path"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    path: Optional[str] = None
    description: Optional[str] = None
    protocols: Optional[List[str]] = None


class SharedPathResponse(SharedPathBase):
    """Schema for shared path response"""
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# User Protocol Access Schemas
# ============================================================================

class UserProtocolAccessBase(BaseModel):
    """Base user protocol access schema"""
    user_id: str
    protocol_id: str
    shared_path_id: str
    permission: PermissionLevel


class UserProtocolAccessCreate(UserProtocolAccessBase):
    """Schema for creating user protocol access"""
    pass


class UserProtocolAccessUpdate(BaseModel):
    """Schema for updating user protocol access"""
    permission: PermissionLevel


class UserProtocolAccessResponse(UserProtocolAccessBase):
    """Schema for user protocol access response"""
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Access Log Schemas
# ============================================================================

class AccessLogBase(BaseModel):
    """Base access log schema"""
    protocol: str
    action: ActionType
    file_path: Optional[str] = None
    ip_address: Optional[str] = None
    status: ActionStatus = ActionStatus.SUCCESS


class AccessLogCreate(AccessLogBase):
    """Schema for creating access log"""
    user_id: Optional[str] = None
    username: Optional[str] = None
    user_agent: Optional[str] = None
    error_message: Optional[str] = None
    file_size_bytes: Optional[int] = None


class AccessLogResponse(AccessLogBase):
    """Schema for access log response"""
    id: str
    user_id: Optional[str]
    username: Optional[str]
    user_agent: Optional[str]
    error_message: Optional[str]
    file_size_bytes: Optional[int]
    timestamp: datetime
    
    class Config:
        from_attributes = True


class AccessLogFilter(BaseModel):
    """Schema for filtering access logs"""
    user_id: Optional[str] = None
    protocol: Optional[str] = None
    action: Optional[ActionType] = None
    status: Optional[ActionStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


# ============================================================================
# Quota Schemas
# ============================================================================

class QuotaUpdate(BaseModel):
    """Schema for updating user quota"""
    quota_gb: int = Field(..., ge=1, le=10000)


class QuotaResponse(BaseModel):
    """Schema for quota information"""
    user_id: str
    username: str
    quota_gb: int
    used_space_gb: float
    usage_percent: float
    is_over_quota: bool


class UsageSummaryResponse(BaseModel):
    """Schema for global usage summary"""
    total_users: int
    total_quota_gb: int
    total_used_gb: float
    average_usage_percent: float
    users_over_quota: int


# ============================================================================
# Generic Response Schemas
# ============================================================================

class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    detail: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None


class PaginatedResponse(BaseModel):
    """Paginated response wrapper"""
    items: List[BaseModel]
    total: int
    limit: int
    offset: int
    has_more: bool
