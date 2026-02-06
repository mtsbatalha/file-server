"""
SMB/CIFS Installer
Installs and configures Samba (Linux) or built-in SMB (Windows)
"""

from typing import Dict, Optional, Tuple
import os

from backend.installers.base import ProtocolInstaller


class SMBInstaller(ProtocolInstaller):
    """SMB/CIFS protocol installer"""
    
    def __init__(self):
        super().__init__()
        self.service_name = "smbd" if self.os_type == "linux" else "LanmanServer"
        self.config_path = "/etc/samba/smb.conf" if self.os_type == "linux" else None
    
    def detect_existing(self) -> Tuple[bool, Optional[str]]:
        """Detect if Samba/SMB is installed"""
        if self.os_type == "linux":
            success, stdout, _ = self.run_command(
                ["which", "smbd"],
                check=False
            )
            if success and stdout.strip():
                success, version_out, _ = self.run_command(
                    ["smbd", "--version"],
                    check=False
                )
                return True, version_out.strip() if success else "unknown"
        elif self.os_type == "windows":
            # SMB is built-in on Windows
            success, stdout, _ = self.run_command([
                "powershell", "-Command",
                "(Get-Service LanmanServer).Status"
            ], check=False)
            return True, "Built-in SMB Server"
        
        return False, None
    
    def install_packages(self) -> bool:
        """Install Samba packages"""
        if self.os_type == "linux":
            if self.run_command(["which", "apt-get"], check=False)[0]:
                self.logger.info("Installing samba via apt...")
                self.run_command(["apt-get", "update"], check=False)
                success, _, _ = self.run_command(
                    ["apt-get", "install", "-y", "samba", "samba-common-bin"],
                    check=False
                )
                return success
            elif self.run_command(["which", "yum"], check=False)[0]:
                self.logger.info("Installing samba via yum...")
                success, _, _ = self.run_command(
                    ["yum", "install", "-y", "samba", "samba-client"],
                    check=False
                )
                return success
            elif self.run_command(["which", "dnf"], check=False)[0]:
                self.logger.info("Installing samba via dnf...")
                success, _, _ = self.run_command(
                    ["dnf", "install", "-y", "samba", "samba-client"],
                    check=False
                )
                return success
        elif self.os_type == "windows":
            # SMB is built-in, just ensure it's enabled
            return True
        
        return False
    
    def configure(self, config: Dict) -> bool:
        """Configure SMB/Samba"""
        if self.os_type == "linux":
            return self._configure_samba(config)
        elif self.os_type == "windows":
            return self._configure_windows_smb(config)
        return False
    
    def _configure_samba(self, config: Dict) -> bool:
        """Configure Samba on Linux"""
        
        # Backup original config
        if os.path.exists(self.config_path):
            self.run_command(
                ["cp", self.config_path, f"{self.config_path}.backup"],
                check=False
            )
        
        # Create Samba configuration
        smb_config = """
[global]
   workgroup = WORKGROUP
   server string = File Server
   netbios name = fileserver
   security = user
   map to guest = bad user
   dns proxy = no
   
   # Logging
   log file = /var/log/samba/log.%m
   max log size = 1000
   log level = 1
   
   # Performance tuning
   socket options = TCP_NODELAY IPTOS_LOWDELAY SO_RCVBUF=131072 SO_SNDBUF=131072
   read raw = yes
   write raw = yes
   max xmit = 65535
   dead time = 15
   getwd cache = yes

# Shared directories will be added here
"""
        
        if not self.write_config_file(self.config_path, smb_config):
            return False
        
        # Test configuration
        success, _, stderr = self.run_command(["testparm", "-s"], check=False)
        if not success:
            self.logger.error(f"Samba configuration test failed: {stderr}")
            return False
        
        return True
    
    def _configure_windows_smb(self, config: Dict) -> bool:
        """Configure SMB on Windows"""
        # Ensure SMB is enabled
        ps_script = """
        Set-Service -Name LanmanServer -StartupType Automatic
        Start-Service LanmanServer
        """
        
        success, _, _ = self.run_command([
            "powershell", "-Command", ps_script
        ], check=False)
        
        return success
    
    def start_service(self) -> bool:
        """Start SMB service"""
        if self.os_type == "linux":
            # Start both smbd and nmbd
            success1, _, _ = self.run_command(
                ["systemctl", "start", "smbd"],
                check=False
            )
            success2, _, _ = self.run_command(
                ["systemctl", "start", "nmbd"],
                check=False
            )
            
            if success1 and success2:
                self.enable_service("smbd")
                self.enable_service("nmbd")
            
            return success1 and success2
        elif self.os_type == "windows":
            success, _, _ = self.run_command([
                "powershell", "-Command",
                "Start-Service LanmanServer"
            ], check=False)
            return success
        return False
    
    def stop_service(self) -> bool:
        """Stop SMB service"""
        if self.os_type == "linux":
            success1, _, _ = self.run_command(
                ["systemctl", "stop", "smbd"],
                check=False
            )
            success2, _, _ = self.run_command(
                ["systemctl", "stop", "nmbd"],
                check=False
            )
            return success1 and success2
        elif self.os_type == "windows":
            success, _, _ = self.run_command([
                "powershell", "-Command",
                "Stop-Service LanmanServer"
            ], check=False)
            return success
        return False
    
    def restart_service(self) -> bool:
        """Restart SMB service"""
        if self.os_type == "linux":
            success1, _, _ = self.run_command(
                ["systemctl", "restart", "smbd"],
                check=False
            )
            success2, _, _ = self.run_command(
                ["systemctl", "restart", "nmbd"],
                check=False
            )
            return success1 and success2
        elif self.os_type == "windows":
            success, _, _ = self.run_command([
                "powershell", "-Command",
                "Restart-Service LanmanServer"
            ], check=False)
            return success
        return False
    
    def get_status(self) -> Dict:
        """Get SMB service status"""
        if self.os_type == "linux":
            is_running = self.is_service_running("smbd")
            
            pid = None
            if is_running:
                success, stdout, _ = self.run_command(
                    ["systemctl", "show", "-p", "MainPID", "smbd"],
                    check=False
                )
                if success:
                    try:
                        pid = int(stdout.strip().split("=")[-1])
                    except:
                        pass
            
            return {
                "is_running": is_running,
                "pid": pid,
                "uptime_seconds": None
            }
        elif self.os_type == "windows":
            success, stdout, _ = self.run_command([
                "powershell", "-Command",
                "(Get-Service LanmanServer).Status"
            ], check=False)
            
            is_running = "Running" in stdout if success else False
            
            return {
                "is_running": is_running,
                "pid": None,
                "uptime_seconds": None
            }
        
        return {"is_running": False}
    
    def uninstall(self) -> bool:
        """Uninstall Samba"""
        self.stop_service()
        
        if self.os_type == "linux":
            if self.run_command(["which", "apt-get"], check=False)[0]:
                success, _, _ = self.run_command(
                    ["apt-get", "remove", "-y", "samba", "samba-common-bin"],
                    check=False
                )
            elif self.run_command(["which", "yum"], check=False)[0]:
                success, _, _ = self.run_command(
                    ["yum", "remove", "-y", "samba"],
                    check=False
                )
            elif self.run_command(["which", "dnf"], check=False)[0]:
                success, _, _ = self.run_command(
                    ["dnf", "remove", "-y", "samba"],
                    check=False
                )
            else:
                return False
            return success
        elif self.os_type == "windows":
            # Can't uninstall built-in SMB on Windows
            self.logger.info("SMB is built-in on Windows and cannot be uninstalled")
            return False
        
        return False
