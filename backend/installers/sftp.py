"""
SFTP Installer
Configures OpenSSH server for SFTP with chroot
"""

from typing import Dict, Optional, Tuple
import os

from backend.installers.base import ProtocolInstaller


class SFTPInstaller(ProtocolInstaller):
    """SFTP protocol installer (via OpenSSH)"""
    
    def __init__(self):
        super().__init__()
        self.service_name = "sshd" if self.os_type == "linux" else "sshd"
        self.config_path = "/etc/ssh/sshd_config" if self.os_type == "linux" else None
    
    def detect_existing(self) -> Tuple[bool, Optional[str]]:
        """Detect if OpenSSH server is already installed"""
        if self.os_type == "linux":
            success, stdout, _ = self.run_command(
                ["which", "sshd"],
                check=False
            )
            if success and stdout.strip():
                # Get version
                success, version_out, _ = self.run_command(
                    ["ssh", "-V"],
                    check=False
                )
                return True, version_out.strip() if success else "unknown"
        elif self.os_type == "windows":
            success, stdout, _ = self.run_command([
                "powershell", "-Command",
                "Get-WindowsCapability -Online | Where-Object Name -like 'OpenSSH.Server*'"
            ], check=False)
            return "Installed" in stdout if success else False, "OpenSSH Server"
        
        return False, None
    
    def install_packages(self) -> bool:
        """Install OpenSSH server"""
        if self.os_type == "linux":
            if self.run_command(["which", "apt-get"], check=False)[0]:
                self.logger.info("Installing openssh-server via apt...")
                self.run_command(["apt-get", "update"], check=False)
                success, _, _ = self.run_command(
                    ["apt-get", "install", "-y", "openssh-server"],
                    check=False
                )
                return success
            elif self.run_command(["which", "yum"], check=False)[0]:
                self.logger.info("Installing openssh-server via yum...")
                success, _, _ = self.run_command(
                    ["yum", "install", "-y", "openssh-server"],
                    check=False
                )
                return success
            elif self.run_command(["which", "dnf"], check=False)[0]:
                self.logger.info("Installing openssh-server via dnf...")
                success, _, _ = self.run_command(
                    ["dnf", "install", "-y", "openssh-server"],
                    check=False
                )
                return success
        elif self.os_type == "windows":
            self.logger.info("Installing OpenSSH Server on Windows...")
            success, _, _ = self.run_command([
                "powershell", "-Command",
                "Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0"
            ], check=False)
            return success
        
        return False
    
    def configure(self, config: Dict) -> bool:
        """Configure OpenSSH for SFTP"""
        if self.os_type == "linux":
            return self._configure_linux_sftp(config)
        elif self.os_type == "windows":
            return self._configure_windows_sftp(config)
        return False
    
    def _configure_linux_sftp(self, config: Dict) -> bool:
        """Configure SFTP on Linux with chroot"""
        
        # Backup original config
        if os.path.exists(self.config_path):
            self.run_command(
                ["cp", self.config_path, f"{self.config_path}.backup"],
                check=False
            )
        
        # Read existing config
        try:
            with open(self.config_path, 'r') as f:
                existing_config = f.read()
        except:
            existing_config = ""
        
        # Add SFTP configuration
        sftp_config = """

# File Server SFTP Configuration
Subsystem sftp internal-sftp

# SFTP-only users group configuration
Match Group sftpusers
    ChrootDirectory /opt/file-server/sftp/%u
    ForceCommand internal-sftp
    AllowTcpForwarding no
    X11Forwarding no
    PasswordAuthentication yes
"""
        
        # Check if already configured
        if "File Server SFTP Configuration" not in existing_config:
            new_config = existing_config + sftp_config
            if not self.write_config_file(self.config_path, new_config):
                return False
        
        # Create sftpusers group if doesn't exist
        self.run_command(["groupadd", "sftpusers"], check=False)
        
        # Create chroot directory structure
        self.create_directory("/opt/file-server/sftp")
        
        return True
    
    def _configure_windows_sftp(self, config: Dict) -> bool:
        """Configure SFTP on Windows"""
        # Start and configure OpenSSH service
        ps_script = """
        Set-Service -Name sshd -StartupType 'Automatic'
        Start-Service sshd
        New-NetFirewallRule -Name sshd -DisplayName 'OpenSSH Server (sshd)' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22
        """
        
        success, _, _ = self.run_command([
            "powershell", "-Command", ps_script
        ], check=False)
        
        return success
    
    def start_service(self) -> bool:
        """Start SSH/SFTP service"""
        if self.os_type == "linux":
            success, _, _ = self.run_command(
                ["systemctl", "start", self.service_name],
                check=False
            )
            if success:
                self.enable_service(self.service_name)
            return success
        elif self.os_type == "windows":
            success, _, _ = self.run_command([
                "powershell", "-Command",
                "Start-Service sshd"
            ], check=False)
            return success
        return False
    
    def stop_service(self) -> bool:
        """Stop SSH/SFTP service"""
        if self.os_type == "linux":
            success, _, _ = self.run_command(
                ["systemctl", "stop", self.service_name],
                check=False
            )
            return success
        elif self.os_type == "windows":
            success, _, _ = self.run_command([
                "powershell", "-Command",
                "Stop-Service sshd"
            ], check=False)
            return success
        return False
    
    def restart_service(self) -> bool:
        """Restart SSH/SFTP service"""
        if self.os_type == "linux":
            success, _, _ = self.run_command(
                ["systemctl", "restart", self.service_name],
                check=False
            )
            return success
        elif self.os_type == "windows":
            success, _, _ = self.run_command([
                "powershell", "-Command",
                "Restart-Service sshd"
            ], check=False)
            return success
        return False
    
    def get_status(self) -> Dict:
        """Get SSH/SFTP service status"""
        if self.os_type == "linux":
            is_running = self.is_service_running(self.service_name)
            
            pid = None
            if is_running:
                success, stdout, _ = self.run_command(
                    ["systemctl", "show", "-p", "MainPID", self.service_name],
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
                "(Get-Service sshd).Status"
            ], check=False)
            
            is_running = "Running" in stdout if success else False
            
            return {
                "is_running": is_running,
                "pid": None,
                "uptime_seconds": None
            }
        
        return {"is_running": False}
    
    def uninstall(self) -> bool:
        """Uninstall OpenSSH server"""
        self.stop_service()
        
        if self.os_type == "linux":
            if self.run_command(["which", "apt-get"], check=False)[0]:
                success, _, _ = self.run_command(
                    ["apt-get", "remove", "-y", "openssh-server"],
                    check=False
                )
            elif self.run_command(["which", "yum"], check=False)[0]:
                success, _, _ = self.run_command(
                    ["yum", "remove", "-y", "openssh-server"],
                    check=False
                )
            elif self.run_command(["which", "dnf"], check=False)[0]:
                success, _, _ = self.run_command(
                    ["dnf", "remove", "-y", "openssh-server"],
                    check=False
                )
            else:
                return False
            return success
        elif self.os_type == "windows":
            success, _, _ = self.run_command([
                "powershell", "-Command",
                "Remove-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0"
            ], check=False)
            return success
        
        return False
