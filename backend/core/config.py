"""
Configuration Management
Handles environment variables and application settings
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    app_name: str = "File Server Management System"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api"
    cors_origins: list[str] = ["*"]  # Allow all origins (configure via CORS_ORIGINS env var for production)
    
    # Database
    database_url: str = "sqlite:///./fileserver.db"
    database_echo: bool = False
    
    # Security
    secret_key: str = Field(default="change-this-in-production-use-openssl-rand-hex-32")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080  # 7 days (same as refresh token)
    refresh_token_expire_days: int = 7
    
    # Password hashing
    pwd_schemes: list[str] = ["bcrypt"]
    pwd_deprecated: str = "auto"
    
    # File Storage
    storage_base_path: Path = Path("/opt/file-server/storage")
    max_upload_size_mb: int = 5000  # 5GB default
    
    # SSL/TLS
    ssl_enabled: bool = False
    ssl_cert_path: Optional[Path] = None
    ssl_key_path: Optional[Path] = None
    letsencrypt_enabled: bool = False
    letsencrypt_email: Optional[str] = None
    letsencrypt_domain: Optional[str] = None
    
    # Quotas
    default_user_quota_gb: int = 100
    quota_check_interval_minutes: int = 60
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[Path] = Path("./logs/fileserver.log")
    log_rotation: str = "10 MB"
    log_retention: str = "90 days"
    
    # Redis (for Celery)
    redis_url: str = "redis://localhost:6379/0"
    
    # Admin User (created on first install)
    admin_username: str = "admin"
    admin_password: str = "admin123"  # CHANGE THIS!
    admin_email: str = "admin@example.com"
    
    # Firewall
    auto_configure_firewall: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Dependency to inject settings"""
    return settings
