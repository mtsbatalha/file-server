"""
S3 (MinIO) Installer
Installs and configures MinIO object storage server
"""

from typing import Dict, Optional, Tuple
import os
import secrets
import string

from backend.installers.base import ProtocolInstaller


class S3Installer(ProtocolInstaller):
    """S3-compatible storage installer (MinIO)"""
    
    def __init__(self):
        super().__init__()
        self.service_name = "minio"
        self.install_dir = "/opt/minio" if self.os_type == "linux" else "C:\\minio"
        self.data_dir = "/opt/minio/data" if self.os_type == "linux" else "C:\\minio\\data"
        self.config_dir = "/etc/minio" if self.os_type == "linux" else "C:\\minio\\config"
    
    def detect_existing(self) -> Tuple[bool, Optional[str]]:
        """Detect if MinIO is already installed"""
        if self.os_type == "linux":
            success, stdout, _ = self.run_command(
                ["which", "minio"],
                check=False
            )
            if success and stdout.strip():
                success, version_out, _ = self.run_command(
                    ["minio", "--version"],
                    check=False
                )
                return True, version_out.strip() if success else "unknown"
        elif self.os_type == "windows":
            import pathlib
            minio_exe = pathlib.Path("C:\\minio\\minio.exe")
            if minio_exe.exists():
                return True, "MinIO (Windows)"
        
        return False, None
    
    def install_packages(self) -> bool:
        """Install MinIO server"""
        if self.os_type == "linux":
            return self._install_minio_linux()
        elif self.os_type == "windows":
            return self._install_minio_windows()
        return False
    
    def _install_minio_linux(self) -> bool:
        """Install MinIO on Linux"""
        self.logger.info("Downloading MinIO for Linux...")
        
        # Create installation directory
        self.create_directory(self.install_dir)
        
        # Download MinIO binary
        success, _, _ = self.run_command([
            "wget",
            "https://dl.min.io/server/minio/release/linux-amd64/minio",
            "-O", f"{self.install_dir}/minio"
        ], check=False)
        
        if not success:
            # Try with curl
            success, _, _ = self.run_command([
                "curl",
                "-o", f"{self.install_dir}/minio",
                "https://dl.min.io/server/minio/release/linux-amd64/minio"
            ], check=False)
        
        if not success:
            self.logger.error("Failed to download MinIO")
            return False
        
        # Make executable
        self.run_command(["chmod", "+x", f"{self.install_dir}/minio"], check=False)
        
        # Create symlink
        self.run_command(["ln", "-sf", f"{self.install_dir}/minio", "/usr/local/bin/minio"], check=False)
        
        # Create minio user
        self.run_command(["useradd", "-r", "-s", "/sbin/nologin", "minio-user"], check=False)
        
        return True
    
    def _install_minio_windows(self) -> bool:
        """Install MinIO on Windows"""
        self.logger.info("Downloading MinIO for Windows...")
        
        # Create installation directory
        os.makedirs(self.install_dir, exist_ok=True)
        
        # Download MinIO binary
        ps_script = f"""
        Invoke-WebRequest -Uri "https://dl.min.io/server/minio/release/windows-amd64/minio.exe" -OutFile "{self.install_dir}\\minio.exe"
        """
        
        success, _, _ = self.run_command([
            "powershell", "-Command", ps_script
        ], check=False)
        
        return success
    
    def configure(self, config: Dict) -> bool:
        """Configure MinIO"""
        # Generate credentials if not provided
        access_key = config.get("access_key") or self._generate_key(20)
        secret_key = config.get("secret_key") or self._generate_key(40)
        
        # Create data directory
        self.create_directory(self.data_dir, "minio-user:minio-user" if self.os_type == "linux" else None)
        
        # Create config directory
        self.create_directory(self.config_dir)
        
        if self.os_type == "linux":
            return self._configure_minio_linux(access_key, secret_key, config)
        elif self.os_type == "windows":
            return self._configure_minio_windows(access_key, secret_key, config)
        
        return False
    
    def _generate_key(self, length: int) -> str:
        """Generate random key"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def _configure_minio_linux(self, access_key: str, secret_key: str, config: Dict) -> bool:
        """Configure MinIO on Linux"""
        
        # Create environment file
        env_content = f"""
MINIO_ROOT_USER={access_key}
MINIO_ROOT_PASSWORD={secret_key}
MINIO_VOLUMES={self.data_dir}
MINIO_OPTS="--console-address :9001"
"""
        
        if not self.write_config_file(f"{self.config_dir}/minio.env", env_content):
            return False
        
        # Create systemd service
        service_content = f"""
[Unit]
Description=MinIO
Documentation=https://docs.min.io
Wants=network-online.target
After=network-online.target
AssertFileIsExecutable={self.install_dir}/minio

[Service]
WorkingDirectory=/usr/local/

User=minio-user
Group=minio-user
ProtectProc=invisible

EnvironmentFile={self.config_dir}/minio.env
ExecStartPre=/bin/bash -c "if [ -z \\"${{MINIO_VOLUMES}}\\" ]; then echo \\"Variable MINIO_VOLUMES not set in {self.config_dir}/minio.env\\"; exit 1; fi"
ExecStart={self.install_dir}/minio server $MINIO_OPTS $MINIO_VOLUMES

Restart=always
LimitNOFILE=65536
TasksMax=infinity
TimeoutStopSec=infinity
SendSIGKILL=no

[Install]
WantedBy=multi-user.target
"""
        
        if not self.write_config_file("/etc/systemd/system/minio.service", service_content):
            return False
        
        # Reload systemd
        self.run_command(["systemctl", "daemon-reload"], check=False)
        
        # Set ownership
        self.run_command(["chown", "-R", "minio-user:minio-user", self.data_dir], check=False)
        self.run_command(["chown", "-R", "minio-user:minio-user", self.config_dir], check=False)
        
        # Save credentials to file for user reference
        creds_file = f"{self.config_dir}/credentials.txt"
        self.write_config_file(creds_file, f"Access Key: {access_key}\nSecret Key: {secret_key}\n")
        
        self.logger.info(f"MinIO credentials saved to: {creds_file}")
        
        return True
    
    def _configure_minio_windows(self, access_key: str, secret_key: str, config: Dict) -> bool:
        """Configure MinIO on Windows"""
        
        # Create environment variables
        ps_script = f"""
        [Environment]::SetEnvironmentVariable("MINIO_ROOT_USER", "{access_key}", "Machine")
        [Environment]::SetEnvironmentVariable("MINIO_ROOT_PASSWORD", "{secret_key}", "Machine")
        """
        
        self.run_command(["powershell", "-Command", ps_script], check=False)
        
        # Create start script
        start_script = f"""
@echo off
set MINIO_ROOT_USER={access_key}
set MINIO_ROOT_PASSWORD={secret_key}
"{self.install_dir}\\minio.exe" server "{self.data_dir}" --console-address ":9001"
"""
        
        self.write_config_file(f"{self.install_dir}\\start-minio.bat", start_script)
        
        # Save credentials
        creds_file = f"{self.install_dir}\\credentials.txt"
        self.write_config_file(creds_file, f"Access Key: {access_key}\nSecret Key: {secret_key}\n")
        
        return True
    
    def start_service(self) -> bool:
        """Start MinIO service"""
        if self.os_type == "linux":
            success, _, _ = self.run_command(
                ["systemctl", "start", self.service_name],
                check=False
            )
            if success:
                self.enable_service(self.service_name)
            return success
        elif self.os_type == "windows":
            # On Windows, MinIO needs to be started manually or via Task Scheduler
            self.logger.info(f"Run {self.install_dir}\\start-minio.bat to start MinIO")
            return True
        return False
    
    def stop_service(self) -> bool:
        """Stop MinIO service"""
        if self.os_type == "linux":
            success, _, _ = self.run_command(
                ["systemctl", "stop", self.service_name],
                check=False
            )
            return success
        elif self.os_type == "windows":
            # Kill minio.exe process
            success, _, _ = self.run_command([
                "powershell", "-Command",
                "Stop-Process -Name minio -Force"
            ], check=False)
            return success
        return False
    
    def restart_service(self) -> bool:
        """Restart MinIO service"""
        if self.os_type == "linux":
            success, _, _ = self.run_command(
                ["systemctl", "restart", self.service_name],
                check=False
            )
            return success
        else:
            self.stop_service()
            return self.start_service()
    
    def get_status(self) -> Dict:
        """Get MinIO service status"""
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
                "Get-Process -Name minio -ErrorAction SilentlyContinue"
            ], check=False)
            
            is_running = bool(stdout.strip()) if success else False
            
            return {
                "is_running": is_running,
                "pid": None,
                "uptime_seconds": None
            }
        
        return {"is_running": False}
    
    def uninstall(self) -> bool:
        """Uninstall MinIO"""
        self.stop_service()
        
        if self.os_type == "linux":
            # Remove service file
            self.run_command(["rm", "-f", "/etc/systemd/system/minio.service"], check=False)
            self.run_command(["systemctl", "daemon-reload"], check=False)
            
            # Remove binary
            self.run_command(["rm", "-f", "/usr/local/bin/minio"], check=False)
            self.run_command(["rm", "-rf", self.install_dir], check=False)
            
            # Remove user (optional, might want to preserve data)
            # self.run_command(["userdel", "minio-user"], check=False)
            
            return True
        elif self.os_type == "windows":
            # Remove installation directory
            success, _, _ = self.run_command([
                "powershell", "-Command",
                f"Remove-Item -Path '{self.install_dir}' -Recurse -Force"
            ], check=False)
            return success
        
        return False
