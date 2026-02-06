"""
Fixes for systemctl PATH issues in uvicorn/FastAPI environment
This module patches subprocess to properly resolve system commands
"""

import subprocess
import shutil
from typing import List

_original_run = subprocess.run


def _patched_run(args, *pargs, **kwargs):
    """Patched subprocess.run that resolves command paths"""
    if isinstance(args, list) and len(args) > 0:
        # Try to resolve the command using shutil.which
        resolved = shutil.which(args[0])
        if resolved:
            args = [resolved] + args[1:]
    
    return _original_run(args, *pargs, **kwargs)


# Apply the patch
subprocess.run = _patched_run
