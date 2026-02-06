"""
Logs Routes
Placeholder for access logs
"""

from fastapi import APIRouter, Depends
from backend.core.security import get_current_active_admin
from backend.api.models.user import User

router = APIRouter()


@router.get("/access")
async def get_access_logs(
    current_user: User = Depends(get_current_active_admin)
):
    """Get access logs"""
    # TODO: Implement
    return []
