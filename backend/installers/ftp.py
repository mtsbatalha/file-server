"""
FTP/FTPS Installer
Installs and configures vsftpd (Linux) or IIS FTP (Windows)
"""

from typing import Dict, Optional, Tuple
import os

from backend.installers.base import ProtocolInstaller


class FTPInstaller(ProtocolInstaller):
    """FTP/FTPS protocol installer"""
    
    def __init__(self):
        super().__init__()
        self.service_name = "vsftpd" if self.os_type == "linux" else "ftpsvc"
        self.config_path = "/etc/vsftpd.conf" if self.os_type == "linux" else None
    
    def detect_existing(self) -> Tuple[bool, Optional[str]]:
        """Detect if FTP server is already installed"""
        if self.os_type == "linux":
            # Check if vsftpd is installed
            success, stdout, _ = self.run_command(
                ["which", "vsftpd"],
                check=False
            )
            if success and stdout.strip():
                # Get version
                success, version_out, _ = self.run_command(
                    ["vsftpd", "-v"],
                    check=False
                )
                return True, version_out.strip() if success else "unknown"
        elif self.os_type == "windows":
            # Check if IIS FTP is installed
            success, _, _ = self.run_command(
                ["powershell", "-Command", "Get-WindowsFeature", "-Name", "Web-Ftp-Server"],
                check=False
            )
            return success, "IIS FTP" if success else None
        
        return False, None
    
    def install_packages(self) -> bool:
        """Install FTP server packages"""
        if self.os_type == "linux":
            # Detect package manager
            if self.run_command(["which", "apt-get"], check=False)[0]:
                # Debian/Ubuntu
                self.logger.info("Installing vsftpd via apt...")
                success, _, _ = self.run_command(["apt-get", "update"], check=False)
                success, _, _ = self.run_command(
                    ["apt-get", "install", "-y", "vsftpd"],
                    check=False
                )
                return success
            elif self.run_command(["which", "yum"], check=False)[0]:
                # RHEL/CentOS
                self.logger.info("Installing vsftpd via yum...")
                success, _, _ = self.run_command(
                    ["yum", "install", "-y", "vsftpd"],
                    check=False
                )
                return success
            elif self.run_command(["which", "dnf"], check=False)[0]:
                # Fedora/Rocky
                self.logger.info("Installing vsftpd via dnf...")
                success, _, _ = self.run_command(
                    ["dnf", "install", "-y", "vsftpd"],
                    check=False
                )
                return success
        elif self.os_type == "windows":
            # Install IIS FTP via PowerShell
            self.logger.info("Installing IIS FTP...")
            success, _, _ = self.run_command([
                "powershell", "-Command",
                "Install-WindowsFeature", "-Name", "Web-Ftp-Server",
                "-IncludeManagementTools"
            ], check=False)
            return success
        
        return False
    
    def configure(self, config: Dict) -> bool:
        """Configure FTP server"""
        if self.os_type == "linux":
            return self._configure_vsftpd(config)
        elif self.os_type == "windows":
            return self._configure_iis_ftp(config)
        return False
    
    def _configure_vsftpd(self, config: Dict) -> bool:
        """Configure vsftpd for Linux"""
        # Default configuration
        vsftpd_config = """
# vsftpd configuration for File Server
listen=YES
listen_ipv6=NO
anonymous_enable=NO
local_enable=YES
write_enable=YES
local_umask=022
dirmessage_enable=YES
use_localtime=YES
xferlog_enable=YES
connect_from_port_20=YES
chroot_local_user=YES
allow_writeable_chroot=YES
secure_chroot_dir=/var/run/vsftpd/empty
pam_service_name=vsftpd
pasv_enable=YES
pasv_min_port=40000
pasv_max_port=50000
userlist_enable=YES
userlist_file=/etc/vsftpd.userlist
userlist_deny=NO

# SSL/TLS Configuration
ssl_enable={ssl_enable}
allow_anon_ssl=NO
force_local_data_ssl={force_ssl}
force_local_logins_ssl={force_ssl}
ssl_tlsv1={ssl_enable}
ssl_sslv2=NO
ssl_sslv3=NO
require_ssl_reuse=NO
ssl_ciphers=HIGH

# Logging
xferlog_std_format=NO
log_ftp_protocol=YES
""".format(
            ssl_enable="YES" if config.get("ssl_enabled", False) else "NO",
            force_ssl="YES" if config.get("force_ssl", False) else "NO"
        )
        
        # Write configuration
        if not self.write_config_file(self.config_path, vsftpd_config):
            return False
        
        # Create userlist file if doesn't exist
        userlist_path = "/etc/vsftpd.userlist"
        if not os.path.exists(userlist_path):
            self.write_config_file(userlist_path, "")
        
        # Create chroot directory
        self.create_directory("/var/run/vsftpd/empty")
        
        # If SSL enabled, generate self-signed cert if not provided
        if config.get("ssl_enabled", False):
            cert_path = config.get("ssl_cert", "/etc/ssl/certs/vsftpd.pem")
            if not os.path.exists(cert_path):
                self.logger.info("Generating self-signed SSL certificate...")
                self.run_command([
                    "openssl", "req", "-x509", "-nodes",
                    "-days", "365",
                    "-newkey", "rsa:2048",
                    "-keyout", cert_path,
                    "-out", cert_path,
                    "-subj", "/CN=FTP Server"
                ], check=False)
        
        return True
    
    def _configure_iis_ftp(self, config: Dict) -> bool:
        """Configure IIS FTP for Windows"""
        # Basic IIS FTP configuration via PowerShell
        # This is simplified; full implementation would be more complex
        ps_script = f"""
        Import-Module WebAdministration
        New-WebFtpSite -Name "FileServerFTP" -Port {config.get('port', 21)} -PhysicalPath "C:\\FTPRoot"
        """
        
        success, _, _ = self.run_command([
            "powershell", "-Command", ps_script
        ], check=False)
        
        return success
    
    def start_service(self) -> bool:
        """Start FTP service"""
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
                f"Start-Service {self.service_name}"
            ], check=False)
            return success
        return False
    
    def stop_service(self) -> bool:
        """Stop FTP service"""
        if self.os_type == "linux":
            success, _, _ = self.run_command(
                ["systemctl", "stop", self.service_name],
                check=False
            )
            return success
        elif self.os_type == "windows":
            success, _, _ = self.run_command([
                "powershell", "-Command",
                f"Stop-Service {self.service_name}"
            ], check=False)
            return success
        return False
    
    def restart_service(self) -> bool:
        """Restart FTP service"""
        if self.os_type == "linux":
            success, _, _ = self.run_command(
                ["systemctl", "restart", self.service_name],
                check=False
            )
            return success
        elif self.os_type == "windows":
            success, _, _ = self.run_command([
                "powershell", "-Command",
                f"Restart-Service {self.service_name}"
            ], check=False)
            return success
        return False
    
    def get_status(self) -> Dict:
        """Get FTP service status"""
        if self.os_type == "linux":
            is_running = self.is_service_running(self.service_name)
            
            # Try to get PID
            pid = None
            if is_running:
                success, stdout, _ = self.run_command(
                    ["systemctl", "show", "-p", "MainPID", self.service_name],
                    check=False
                )
                if success:
                    pid_str = stdout.strip().split("=")[-1]
                    try:
                        pid = int(pid_str)
                    except:
                        pass
            
            return {
                "is_running": is_running,
                "pid": pid,
                "uptime_seconds": None  # Would need additional command
            }
        
        elif self.os_type == "windows":
            success, stdout, _ = self.run_command([
                "powershell", "-Command",
                f"(Get-Service {self.service_name}).Status"
            ], check=False)
            
            is_running = "Running" in stdout if success else False
            
            return {
                "is_running": is_running,
                "pid": None,
                "uptime_seconds": None
            }
        
        return {"is_running": False}
    
    def uninstall(self) -> bool:
        """Uninstall FTP server"""
        # Stop service first
        self.stop_service()
        
        if self.os_type == "linux":
            # Remove vsftpd
            if self.run_command(["which", "apt-get"], check=False)[0]:
                success, _, _ = self.run_command(
                    ["apt-get", "remove", "-y", "vsftpd"],
                    check=False
                )
            elif self.run_command(["which", "yum"], check=False)[0]:
                success, _, _ = self.run_command(
                    ["yum", "remove", "-y", "vsftpd"],
                    check=False
                )
            elif self.run_command(["which", "dnf"], check=False)[0]:
                success, _, _ = self.run_command(
                    ["dnf", "remove", "-y", "vsftpd"],
                    check=False
                )
            else:
                return False
            return success
        
        elif self.os_type == "windows":
            # Remove IIS FTP
            success, _, _ = self.run_command([
                "powershell", "-Command",
                "Uninstall-WindowsFeature -Name Web-Ftp-Server"
            ], check=False)
            return success
        
        return False
