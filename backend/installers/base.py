"""
Base Protocol Installer
Abstract base class for all protocol installers
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, List, Tuple
from enum import Enum
import platform
import subprocess
import logging

logger = logging.getLogger(__name__)


class InstallerStatus(str, Enum):
    """Installer operation status"""
    SUCCESS = "success"
    FAILED = "failed"
    ALREADY_INSTALLED = "already_installed"
    NOT_SUPPORTED = "not_supported"


class ProtocolInstaller(ABC):
    """
    Abstract base class for protocol installers
    All protocol-specific installers must inherit from this class
    """
    
    def __init__(self):
        self.os_type = platform.system().lower()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def detect_existing(self) -> Tuple[bool, Optional[str]]:
        """
        Detect if protocol is already installed
        
        Returns:
            (is_installed, version_or_path)
        """
        pass
    
    @abstractmethod
    def install_packages(self) -> bool:
        """
        Install required system packages
        
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def configure(self, config: Dict) -> bool:
        """
        Configure the protocol service
        
        Args:
            config: Configuration dictionary
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def start_service(self) -> bool:
        """
        Start the protocol service
        
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def stop_service(self) -> bool:
        """
        Stop the protocol service
      
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def restart_service(self) -> bool:
        """
        Restart the protocol service
        
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_status(self) -> Dict:
        """
        Get current service status
        
        Returns:
            Status dictionary with keys: is_running, pid, uptime, etc.
        """
        pass
    
    @abstractmethod
    def uninstall(self) -> bool:
        """
        Uninstall the protocol
        
        Returns:
            True if successful, False otherwise
        """
        pass
    
    # Helper methods (can be overridden)
    
    def run_command(self, command: List[str], check: bool = True) -> Tuple[bool, str, str]:
        """
        Run a system command
        
        Args:
            command: Command as list of strings
            check: Whether to raise exception on failure
            
        Returns:
            (success, stdout, stderr)
        """
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=check
            )
            return True, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Command failed: {' '.join(command)}")
            self.logger.error(f"Error: {e.stderr}")
            return False, e.stdout, e.stderr
    
    def is_service_running(self, service_name: str) -> bool:
        """
        Check if a systemd service is running (Linux only)
        
        Args:
            service_name: Name of the service
            
        Returns:
            True if running, False otherwise
        """
        if self.os_type != "linux":
            return False
        
        success, stdout, _ = self.run_command(
            ["systemctl", "is-active", service_name],
            check=False
        )
        return "active" in stdout.lower()
    
    def enable_service(self, service_name: str) -> bool:
        """
        Enable service to start on boot (Linux systemd)
        
        Args:
            service_name: Name of the service
            
        Returns:
            True if successful
        """
        if self.os_type != "linux":
            return False
        
        success, _, _ = self.run_command(
            ["systemctl", "enable", service_name],
            check=False
        )
        return success
    
    def check_port_available(self, port: int) -> bool:
        """
        Check if a port is available
        
        Args:
            port: Port number to check
            
        Returns:
            True if available, False if in use
        """
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(("0.0.0.0", port))
            sock.close()
            return True
        except OSError:
            return False
    
    def create_directory(self, path: str, owner: Optional[str] = None) -> bool:
        """
        Create directory with optional owner
        
        Args:
            path: Directory path
            owner: Optional owner (user:group format for Linux)
            
        Returns:
            True if successful
        """
        from pathlib import Path
        
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            
            if owner and self.os_type == "linux":
                self.run_command(["chown", owner, path])
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to create directory {path}: {e}")
            return False
    
    def write_config_file(self, path: str, content: str, owner: Optional[str] = None) -> bool:
        """
        Write configuration file
        
        Args:
            path: File path
            content: File content
            owner: Optional owner (Linux)
            
        Returns:
            True if successful
        """
        try:
            with open(path, 'w') as f:
                f.write(content)
            
            if owner and self.os_type == "linux":
                self.run_command(["chown", owner, path])
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to write config file {path}: {e}")
            return False
