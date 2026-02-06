"""
Protocols Routes
Protocol installation, configuration, and management
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict

from backend.core.database import get_db
from backend.core.security import get_current_active_admin
from backend.api.models.user import User, Protocol, ProtocolStatus
from backend.api.schemas.schemas import (
    ProtocolResponse,
    ProtocolUpdate,
    ProtocolStatusResponse,
    MessageResponse
)
from backend.api.services import protocol_service

router = APIRouter()


# Import protocol installers dynamically
def get_protocol_installer(protocol_name: str):
    """Get the installer class for a protocol"""
    installer_map = {
        "ftp": "backend.installers.ftp.FTPInstaller",
        "sftp": "backend.installers.sftp.SFTPInstaller",
        "nfs": "backend.installers.nfs.NFSInstaller",
        "smb": "backend.installers.smb.SMBInstaller",
        "webdav": "backend.installers.webdav.WebDAVInstaller",
        "s3": "backend.installers.s3.S3Installer",
        "nextcloud": "backend.installers.nextcloud.NextCloudInstaller"
    }
    
    module_path = installer_map.get(protocol_name)
    if not module_path:
        raise ValueError(f"Unknown protocol: {protocol_name}")
    
    # Import dynamically
    module_name, class_name = module_path.rsplit(".", 1)
    module = __import__(module_name, fromlist=[class_name])
    installer_class = getattr(module, class_name)
    
    return installer_class()


@router.get("/", response_model=List[ProtocolResponse])
async def list_protocols(
    db: Session = Depends(get_db)
):
    """List all available protocols"""
    protocols = protocol_service.get_all_protocols(db)
    return protocols


@router.get("/{protocol_name}", response_model=ProtocolResponse)
async def get_protocol(
    protocol_name: str,
    db: Session = Depends(get_db)
):
    """Get protocol details by name"""
    protocol = protocol_service.get_protocol_by_name(db, protocol_name)
    if not protocol:
        raise HTTPException(status_code=404, detail="Protocol not found")
    
    return protocol


@router.post("/{protocol_name}/install", response_model=MessageResponse)
async def install_protocol(
    protocol_name: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    """Install a protocol (admin only, runs in background)"""
    protocol = protocol_service.get_protocol_by_name(db, protocol_name)
    if not protocol:
        raise HTTPException(status_code=404, detail="Protocol not found")
    
    if protocol.is_installed:
        return {"message": f"{protocol.display_name} is already installed"}
    
    # Mark as installing
    protocol_service.update_protocol_status(
        db, protocol.id, ProtocolStatus.INSTALLING
    )
    
    # Run installation in background
    def install_task():
        try:
            installer = get_protocol_installer(protocol_name)
            
            # Check if already installed
            is_installed, version = installer.detect_existing()
            if is_installed:
                protocol_service.update_protocol_status(
                    db, protocol.id, ProtocolStatus.STOPPED,
                    is_installed=True
                )
                return
            
            # Install packages
            if not installer.install_packages():
                protocol_service.update_protocol_status(
                    db, protocol.id, ProtocolStatus.ERROR
                )
                return
            
            # Configure
            config = protocol.config_json or {}
            if not installer.configure(config):
                protocol_service.update_protocol_status(
                    db, protocol.id, ProtocolStatus.ERROR
                )
                return
            
            # Start service automatically after installation
            if installer.start_service():
                protocol_service.update_protocol_status(
                    db, protocol.id, ProtocolStatus.RUNNING,
                    is_installed=True,
                    is_enabled=True
                )
            else:
                # Installed but failed to start
                protocol_service.update_protocol_status(
                    db, protocol.id, ProtocolStatus.STOPPED,
                    is_installed=True,
                    is_enabled=False
                )
            
        except Exception as e:
            print(f"Installation failed for {protocol_name}: {e}")
            protocol_service.update_protocol_status(
                db, protocol.id, ProtocolStatus.ERROR
            )
    
    background_tasks.add_task(install_task)
    
    return {"message": f"Installation of {protocol.display_name} started in background"}


@router.post("/{protocol_name}/start", response_model=MessageResponse)
async def start_protocol(
    protocol_name: str,
    current_user: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    """Start a protocol service (admin only)"""
    protocol = protocol_service.get_protocol_by_name(db, protocol_name)
    if not protocol:
        raise HTTPException(status_code=404, detail="Protocol not found")
    
    if not protocol.is_installed:
        raise HTTPException(status_code=400, detail="Protocol not installed")
    
    try:
        installer = get_protocol_installer(protocol_name)
        if installer.start_service():
            protocol_service.update_protocol_status(
                db, protocol.id, ProtocolStatus.RUNNING,
                is_enabled=True
            )
            return {"message": f"{protocol.display_name} started successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to start service")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{protocol_name}/stop", response_model=MessageResponse)
async def stop_protocol(
    protocol_name: str,
    current_user: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    """Stop a protocol service (admin only)"""
    protocol = protocol_service.get_protocol_by_name(db, protocol_name)
    if not protocol:
        raise HTTPException(status_code=404, detail="Protocol not found")
    
    if not protocol.is_installed:
        raise HTTPException(status_code=400, detail="Protocol not installed")
    
    try:
        installer = get_protocol_installer(protocol_name)
        if installer.stop_service():
            protocol_service.update_protocol_status(
                db, protocol.id, ProtocolStatus.STOPPED,
                is_enabled=False
            )
            return {"message": f"{protocol.display_name} stopped successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to stop service")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{protocol_name}/status", response_model=ProtocolStatusResponse)
async def get_protocol_status(
    protocol_name: str,
    db: Session = Depends(get_db)
):
    """Get protocol service status"""
    protocol = protocol_service.get_protocol_by_name(db, protocol_name)
    if not protocol:
        raise HTTPException(status_code=404, detail="Protocol not found")
    
    if not protocol.is_installed:
        return {
            "protocol_name": protocol_name,
            "status": ProtocolStatus.UNINSTALLED,
            "is_running": False,
            "port": protocol.port
        }
    
    try:
        installer = get_protocol_installer(protocol_name)
        status_info = installer.get_status()
        
        return{
            "protocol_name": protocol_name,
            "status": protocol.status,
            **status_info,
            "port": protocol.port
        }
    except Exception as e:
        return {
            "protocol_name": protocol_name,
            "status": ProtocolStatus.ERROR,
            "is_running": False,
            "error_message": str(e),
            "port": protocol.port
        }


@router.put("/{protocol_name}/config", response_model=ProtocolResponse)
async def update_protocol_config(
    protocol_name: str,
    config_update: ProtocolUpdate,
    current_user: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    """Update protocol configuration (admin only)"""
    protocol = protocol_service.get_protocol_by_name(db, protocol_name)
    if not protocol:
        raise HTTPException(status_code=404, detail="Protocol not found")
    
    config = config_update.config_json or protocol.config_json
    port = config_update.port if config_update.port is not None else protocol.port
    ssl_enabled = config_update.ssl_enabled if config_update.ssl_enabled is not None else protocol.ssl_enabled
    
    updated_protocol = protocol_service.update_protocol_config(
        db, protocol.id, config, port, ssl_enabled
    )
    
    # If protocol is installed and running, reconfigure it
    if protocol.is_installed and protocol.status == ProtocolStatus.RUNNING:
        try:
            installer = get_protocol_installer(protocol_name)
            if not installer.configure(config):
                raise HTTPException(status_code=500, detail="Failed to apply new configuration")
            
            # Restart to apply changes
            installer.restart_service()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to reconfigure: {str(e)}")
    
    return updated_protocol


@router.post("/{protocol_name}/restart", response_model=MessageResponse)
async def restart_protocol(
    protocol_name: str,
    current_user: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    """Restart a protocol service (admin only)"""
    protocol = protocol_service.get_protocol_by_name(db, protocol_name)
    if not protocol:
        raise HTTPException(status_code=404, detail="Protocol not found")
    
    if not protocol.is_installed:
        raise HTTPException(status_code=400, detail="Protocol not installed")
    
    try:
        installer = get_protocol_installer(protocol_name)
        if installer.restart_service():
            protocol_service.update_protocol_status(
                db, protocol.id, ProtocolStatus.RUNNING,
                is_enabled=True
            )
            return {"message": f"{protocol.display_name} restarted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to restart service")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{protocol_name}/uninstall", response_model=MessageResponse)
async def uninstall_protocol(
    protocol_name: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    """Uninstall a protocol (admin only, runs in background)"""
    protocol = protocol_service.get_protocol_by_name(db, protocol_name)
    if not protocol:
        raise HTTPException(status_code=404, detail="Protocol not found")
    
    if not protocol.is_installed:
        return {"message": f"{protocol.display_name} is not installed"}
    
    # Mark as uninstalling
    protocol_service.update_protocol_status(
        db, protocol.id, ProtocolStatus.INSTALLING  # Reusing status for uninstalling
    )
    
    # Run uninstallation in background
    def uninstall_task():
        try:
            installer = get_protocol_installer(protocol_name)
            
            # Stop service first
            installer.stop_service()
            
            # Uninstall
            if installer.uninstall():
                protocol_service.update_protocol_status(
                    db, protocol.id, ProtocolStatus.UNINSTALLED,
                    is_installed=False,
                    is_enabled=False
                )
            else:
                protocol_service.update_protocol_status(
                    db, protocol.id, ProtocolStatus.ERROR
                )
        except Exception as e:
            print(f"Uninstallation failed for {protocol_name}: {e}")
            protocol_service.update_protocol_status(
                db, protocol.id, ProtocolStatus.ERROR
            )
    
    background_tasks.add_task(uninstall_task)
    
    return {"message": f"Uninstallation of {protocol.display_name} started in background"}
