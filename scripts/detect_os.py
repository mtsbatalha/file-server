#!/usr/bin/env python3
"""
OS Detection Module
Detects operating system, distribution, and validates system requirements
"""

import platform
import os
import sys
import subprocess
from enum import Enum
from typing import Dict, Optional, Tuple
from pathlib import Path


class OSType(Enum):
    """Supported operating system types"""
    LINUX = "linux"
    WINDOWS = "windows"
    MACOS = "macos"
    BSD = "bsd"
    UNKNOWN = "unknown"


class LinuxDistro(Enum):
    """Supported Linux distributions"""
    UBUNTU = "ubuntu"
    DEBIAN = "debian"
    RHEL = "rhel"
    CENTOS = "centos"
    ROCKY = "rocky"
    FEDORA = "fedora"
    ARCH = "arch"
    UNKNOWN = "unknown"


class DetectionResult:
    """System detection result"""
    
    def __init__(self):
        self.os_type: OSType = OSType.UNKNOWN
        self.distro: Optional[LinuxDistro] = None
        self.version: str = ""
        self.is_root: bool = False
        self.architecture: str = ""
        self.existing_installation: bool = False
        self.install_path: Optional[Path] = None
        
    def __repr__(self):
        return (
            f"DetectionResult(os={self.os_type.value}, "
            f"distro={self.distro.value if self.distro else None}, "
            f"version={self.version}, "
            f"is_root={self.is_root}, "
            f"arch={self.architecture})"
        )


def detect_os_type() -> OSType:
    """Detect the operating system type"""
    system = platform.system().lower()
    
    if system == "linux":
        return OSType.LINUX
    elif system == "windows":
        return OSType.WINDOWS
    elif system == "darwin":
        return OSType.MACOS
    elif "bsd" in system:
        return OSType.BSD
    else:
        return OSType.UNKNOWN


def detect_linux_distro() -> Tuple[LinuxDistro, str]:
    """
    Detect Linux distribution and version
    Returns: (distro, version)
    """
    try:
        # Try using /etc/os-release (standard)
        if os.path.exists("/etc/os-release"):
            with open("/etc/os-release") as f:
                lines = f.readlines()
                
            info = {}
            for line in lines:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    info[key] = value.strip('"')
            
            distro_id = info.get("ID", "").lower()
            version = info.get("VERSION_ID", "")
            
            # Map distro ID to enum
            distro_map = {
                "ubuntu": LinuxDistro.UBUNTU,
                "debian": LinuxDistro.DEBIAN,
                "rhel": LinuxDistro.RHEL,
                "centos": LinuxDistro.CENTOS,
                "rocky": LinuxDistro.ROCKY,
                "fedora": LinuxDistro.FEDORA,
                "arch": LinuxDistro.ARCH,
            }
            
            return distro_map.get(distro_id, LinuxDistro.UNKNOWN), version
            
        # Fallback: try legacy files
        elif os.path.exists("/etc/redhat-release"):
            with open("/etc/redhat-release") as f:
                content = f.read().lower()
                if "centos" in content:
                    return LinuxDistro.CENTOS, ""
                elif "rhel" in content or "red hat" in content:
                    return LinuxDistro.RHEL, ""
                elif "rocky" in content:
                    return LinuxDistro.ROCKY, ""
                    
        elif os.path.exists("/etc/debian_version"):
            return LinuxDistro.DEBIAN, ""
            
    except Exception as e:
        print(f"Warning: Could not detect Linux distribution: {e}")
    
    return LinuxDistro.UNKNOWN, ""


def is_root_user() -> bool:
    """Check if running with root/admin privileges"""
    if platform.system() == "Windows":
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False
    else:
        return os.geteuid() == 0


def detect_architecture() -> str:
    """Detect system architecture"""
    return platform.machine()


def check_existing_installation() -> Tuple[bool, Optional[Path]]:
    """
    Check if file-server is already installed
    Returns: (exists, installation_path)
    """
    # Common installation paths
    if platform.system() == "Windows":
        search_paths = [
            Path("C:/Program Files/file-server"),
            Path("C:/file-server"),
            Path.home() / "file-server"
        ]
    else:
        search_paths = [
            Path("/opt/file-server"),
            Path("/usr/local/file-server"),
            Path.home() / "file-server"
        ]
    
    for path in search_paths:
        if path.exists() and (path / "backend" / "api" / "main.py").exists():
            return True, path
            
    return False, None


def check_python_version() -> bool:
    """Check if Python version meets minimum requirements (3.10+)"""
    version_info = sys.version_info
    return version_info.major == 3 and version_info.minor >= 10


def check_command_available(command: str) -> bool:
    """Check if a command is available in PATH"""
    try:
        if platform.system() == "Windows":
            subprocess.run(
                ["where", command],
                capture_output=True,
                check=True
            )
        else:
            subprocess.run(
                ["which", command],
                capture_output=True,
                check=True
            )
        return True
    except subprocess.CalledProcessError:
        return False


def get_package_manager() -> Optional[str]:
    """Detect available package manager for Linux"""
    if platform.system() != "Linux":
        return None
        
    managers = {
        "apt": ["apt-get", "apt"],
        "yum": ["yum"],
        "dnf": ["dnf"],
        "pacman": ["pacman"],
        "zypper": ["zypper"]
    }
    
    for manager, commands in managers.items():
        for cmd in commands:
            if check_command_available(cmd):
                return manager
                
    return None


def detect_system() -> DetectionResult:
    """
    Perform complete system detection
    Returns: DetectionResult object with all detection info
    """
    result = DetectionResult()
    
    # OS Type
    result.os_type = detect_os_type()
    
    # Linux distro
    if result.os_type == OSType.LINUX:
        result.distro, result.version = detect_linux_distro()
    elif result.os_type == OSType.WINDOWS:
        result.version = platform.version()
        
    # Privileges
    result.is_root = is_root_user()
    
    # Architecture
    result.architecture = detect_architecture()
    
    # Existing installation
    result.existing_installation, result.install_path = check_existing_installation()
    
    return result


def print_system_info(result: DetectionResult):
    """Print formatted system information"""
    print("\n" + "="*60)
    print("SYSTEM DETECTION RESULTS")
    print("="*60)
    print(f"Operating System: {result.os_type.value.upper()}")
    
    if result.distro:
        print(f"Distribution: {result.distro.value.upper()} {result.version}")
    elif result.version:
        print(f"Version: {result.version}")
        
    print(f"Architecture: {result.architecture}")
    print(f"Running as root/admin: {'YES' if result.is_root else 'NO'}")
    
    if result.existing_installation:
        print(f"\n⚠️  Existing installation found at: {result.install_path}")
    else:
        print("\n✅ No existing installation detected")
        
    # Check requirements
    print("\n" + "-"*60)
    print("REQUIREMENTS CHECK")
    print("-"*60)
    
    python_ok = check_python_version()
    print(f"Python 3.10+: {'✅ YES' if python_ok else '❌ NO'}")
    
    if result.os_type == OSType.LINUX:
        pkg_mgr = get_package_manager()
        print(f"Package Manager: {'✅ ' + pkg_mgr.upper() if pkg_mgr else '❌ NOT FOUND'}")
        
    # Check common tools
    tools = {
        "git": "Git",
        "curl": "Curl",
        "systemctl": "Systemd" if result.os_type == OSType.LINUX else None
    }
    
    for cmd, name in tools.items():
        if name:
            available = check_command_available(cmd)
            print(f"{name}: {'✅ YES' if available else '❌ NO'}")
    
    print("="*60 + "\n")


def validate_installation_requirements() -> Dict[str, bool]:
    """
    Validate all installation requirements
    Returns: Dict with requirement names and their status
    """
    result = detect_system()
    
    requirements = {
        "supported_os": result.os_type in [OSType.LINUX, OSType.WINDOWS],
        "root_privileges": result.is_root,
        "python_version": check_python_version(),
    }
    
    if result.os_type == OSType.LINUX:
        requirements["package_manager"] = get_package_manager() is not None
        
    return requirements


if __name__ == "__main__":
    # Run detection and print results
    result = detect_system()
    print_system_info(result)
    
    # Validate requirements
    requirements = validate_installation_requirements()
    
    if not all(requirements.values()):
        print("\n❌ SOME REQUIREMENTS ARE NOT MET:")
        for req, status in requirements.items():
            if not status:
                print(f"   - {req.replace('_', ' ').title()}")
        print("\nPlease resolve these issues before installation.")
        sys.exit(1)
    else:
        print("\n✅ ALL REQUIREMENTS MET! Ready for installation.")
        sys.exit(0)
