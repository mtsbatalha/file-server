"""
Fixes for systemctl PATH issues in uvicorn/FastAPI environment
This module patches subprocess to properly resolve system commands
"""

import subprocess
import shutil
import os
import logging
from typing import List

logger = logging.getLogger(__name__)

_original_run = subprocess.run

# Common Linux system paths
SYSTEM_PATHS = ['/usr/bin', '/bin', '/usr/sbin', '/sbin', '/usr/local/bin']


def _find_command(cmd: str) -> str:
    """Find command in system paths"""
    # First try shutil.which
    resolved = shutil.which(cmd)
    if resolved:
        return resolved
    
    # Fallback: search common system paths
    for path in SYSTEM_PATHS:
        full_path = os.path.join(path, cmd)
        if os.path.exists(full_path) and os.access(full_path, os.X_OK):
            logger.info(f"Found {cmd} at {full_path}")
            return full_path
    
    # If not found, return original command
    logger.warning(f"Command {cmd} not found in PATH or system directories")
    return cmd


def _patched_run(args, *pargs, **kwargs):
    """Patched subprocess.run that resolves command paths"""
    if isinstance(args, list) and len(args) > 0:
        original_cmd = args[0]
        resolved_cmd = _find_command(original_cmd)
        if resolved_cmd != original_cmd:
            args = [resolved_cmd] + args[1:]
            logger.debug(f"Resolved {original_cmd} to {resolved_cmd}")
    
    return _original_run(args, *pargs, **kwargs)


# Apply the patch
subprocess.run = _patched_run
logger.info("Subprocess patch applied for command path resolution")
