"""
Logs Routes
Access logs and service logs management
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime, timedelta
import subprocess

from backend.core.database import get_db
from backend.core.security import get_current_active_admin
from backend.api.models.user import User, AccessLog, ActionType, ActionStatus
from backend.api.schemas.schemas import AccessLogResponse

router = APIRouter()


@router.get("/access", response_model=List[AccessLogResponse])
async def get_access_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    user_id: Optional[str] = None,
    protocol: Optional[str] = None,
    action: Optional[str] = None,
    status: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """Get access logs with filtering"""
    query = db.query(AccessLog)
    
    # Apply filters
    if user_id:
        query = query.filter(AccessLog.user_id == user_id)
    if protocol:
        query = query.filter(AccessLog.protocol == protocol)
    if action:
        try:
            action_enum = ActionType(action)
            query = query.filter(AccessLog.action == action_enum)
        except ValueError:
            pass
    if status:
        try:
            status_enum = ActionStatus(status)
            query = query.filter(AccessLog.status == status_enum)
        except ValueError:
            pass
    if from_date:
        query = query.filter(AccessLog.timestamp >= from_date)
    if to_date:
        query = query.filter(AccessLog.timestamp <= to_date)
    
    # Order by most recent and paginate
    logs = query.order_by(desc(AccessLog.timestamp)).offset(skip).limit(limit).all()
    
    return logs


@router.get("/access/stats")
async def get_access_stats(
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """Get access log statistics"""
    from_date = datetime.utcnow() - timedelta(days=days)
    
    total_logs = db.query(AccessLog).filter(AccessLog.timestamp >= from_date).count()
    success_logs = db.query(AccessLog).filter(
        AccessLog.timestamp >= from_date,
        AccessLog.status == ActionStatus.SUCCESS
    ).count()
    failed_logs = db.query(AccessLog).filter(
        AccessLog.timestamp >= from_date,
        AccessLog.status == ActionStatus.FAILED
    ).count()
    denied_logs = db.query(AccessLog).filter(
        AccessLog.timestamp >= from_date,
        AccessLog.status == ActionStatus.DENIED
    ).count()
    
    # Group by action type
    action_stats = {}
    for action in ActionType:
        count = db.query(AccessLog).filter(
            AccessLog.timestamp >= from_date,
            AccessLog.action == action
        ).count()
        if count > 0:
            action_stats[action.value] = count
    
    # Group by protocol
    protocol_stats = {}
    protocols = db.query(AccessLog.protocol).filter(
        AccessLog.timestamp >= from_date
    ).distinct().all()
    for (proto,) in protocols:
        count = db.query(AccessLog).filter(
            AccessLog.timestamp >= from_date,
            AccessLog.protocol == proto
        ).count()
        protocol_stats[proto] = count
    
    return {
        "period_days": days,
        "total": total_logs,
        "success": success_logs,
        "failed": failed_logs,
        "denied": denied_logs,
        "by_action": action_stats,
        "by_protocol": protocol_stats
    }


@router.get("/services")
async def get_service_logs(
    service: str = Query(..., description="Service name: ftp, sftp, smb, s3, fileserver-api"),
    lines: int = Query(50, ge=10, le=500),
    current_user: User = Depends(get_current_active_admin)
):
    """Get system service logs via journalctl"""
    # Map service names to systemd unit names
    service_map = {
        "ftp": "vsftpd",
        "sftp": "sshd",
        "smb": "smbd",
        "s3": "minio",
        "api": "fileserver-api",
        "fileserver-api": "fileserver-api"
    }
    
    unit_name = service_map.get(service.lower())
    if not unit_name:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown service: {service}. Available: {list(service_map.keys())}"
        )
    
    try:
        result = subprocess.run(
            ["journalctl", "-u", unit_name, "-n", str(lines), "--no-pager", "-o", "short-iso"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        lines_list = result.stdout.strip().split("\n") if result.stdout else []
        
        return {
            "service": service,
            "unit": unit_name,
            "lines": lines_list,
            "error": result.stderr if result.returncode != 0 else None
        }
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Timeout reading service logs")
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="journalctl not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/services/status")
async def get_services_status(
    current_user: User = Depends(get_current_active_admin)
):
    """Get status of all file-sharing services"""
    services = ["vsftpd", "smbd", "minio", "sshd", "fileserver-api"]
    statuses = {}
    
    for service in services:
        try:
            result = subprocess.run(
                ["systemctl", "is-active", service],
                capture_output=True,
                text=True,
                timeout=5
            )
            statuses[service] = result.stdout.strip()
        except Exception:
            statuses[service] = "unknown"
    
    return statuses
