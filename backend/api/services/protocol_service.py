"""
Protocol Service  
Business logic for protocol management and initialization
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from backend.api.models.user import Protocol, ProtocolStatus
from backend.core.database import SessionLocal


# Default protocols to initialize
DEFAULT_PROTOCOLS = [
    {
        "name": "ftp",
        "display_name": "FTP/FTPS",
        "port": 21,
        "status": ProtocolStatus.UNINSTALLED
    },
    {
        "name": "sftp",
        "display_name": "SFTP",
        "port": 22,
        "status": ProtocolStatus.UNINSTALLED
    },
    {
        "name": "nfs",
        "display_name": "NFS",
        "port": 2049,
        "status": ProtocolStatus.UNINSTALLED
    },
    {
        "name": "smb",
        "display_name": "SMB/CIFS",
        "port": 445,
        "status": ProtocolStatus.UNINSTALLED
    },
    {
        "name": "webdav",
        "display_name": "WebDAV",
        "port": 8080,
        "status": ProtocolStatus.UNINSTALLED
    },
    {
        "name": "s3",
        "display_name": "S3 (MinIO)",
        "port": 9000,
        "status": ProtocolStatus.UNINSTALLED
    },
    {
        "name": "nextcloud",
        "display_name": "NextCloud",
        "port": 8081,
        "status": ProtocolStatus.UNINSTALLED
    }
]


def initialize_protocols():
    """Initialize default protocols in database"""
    db = SessionLocal()
    try:
        for proto_data in DEFAULT_PROTOCOLS:
            existing = db.query(Protocol).filter(Protocol.name == proto_data["name"]).first()
            if not existing:
                protocol = Protocol(**proto_data)
                db.add(protocol)
        db.commit()
        print("Default protocols initialized")
    finally:
        db.close()


def get_protocol(db: Session, protocol_id: str) -> Optional[Protocol]:
    """Get protocol by ID"""
    return db.query(Protocol).filter(Protocol.id == protocol_id).first()


def get_protocol_by_name(db: Session, name: str) -> Optional[Protocol]:
    """Get protocol by name"""
    return db.query(Protocol).filter(Protocol.name == name).first()


def get_all_protocols(db: Session) -> List[Protocol]:
    """Get all protocols"""
    return db.query(Protocol).all()


def update_protocol_status(
    db: Session,
    protocol_id: str,
    status: ProtocolStatus,
    is_installed: bool = None,
    is_enabled: bool = None,
    error_message: str = None
) -> Optional[Protocol]:
    """Update protocol status"""
    protocol = db.query(Protocol).filter(Protocol.id == protocol_id).first()
    if not protocol:
        return None
    
    protocol.status = status
    if is_installed is not None:
        protocol.is_installed = is_installed
    if is_enabled is not None:
        protocol.is_enabled = is_enabled
    
    # Update error message
    protocol.error_message = error_message
    
    if status == ProtocolStatus.RUNNING and is_installed:
        protocol.installed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(protocol)
    
    return protocol


def update_protocol_config(
    db: Session,
    protocol_id: str,
    config: dict,
    port: int = None,
    ssl_enabled: bool = None
) -> Optional[Protocol]:
    """Update protocol configuration"""
    protocol = db.query(Protocol).filter(Protocol.id == protocol_id).first()
    if not protocol:
        return None
    
    protocol.config_json = config
    if port is not None:
        protocol.port = port
    if ssl_enabled is not None:
        protocol.ssl_enabled = ssl_enabled
    
    db.commit()
    db.refresh(protocol)
    
    return protocol
