"""
NFS Installer
Stub - to be implemented
"""

from typing import Dict, Optional, Tuple
from backend.installers.base import ProtocolInstaller


class NFSInstaller(ProtocolInstaller):
    """NFS protocol installer (stub)"""
    
    def detect_existing(self) -> Tuple[bool, Optional[str]]:
        return False, None
    
    def install_packages(self) -> bool:
        self.logger.warning("NFS installer not yet implemented")
        return False
    
    def configure(self, config: Dict) -> bool:
        return False
    
    def start_service(self) -> bool:
        return False
    
    def stop_service(self) -> bool:
        return False
    
    def restart_service(self) -> bool:
        return False
    
    def get_status(self) -> Dict:
        return {"is_running": False}
    
    def uninstall(self) -> bool:
        return False
