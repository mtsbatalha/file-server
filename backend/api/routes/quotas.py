"""
Quotas Routes
Placeholder for quota management
"""

from fastapi import APIRouter, Depends
from backend.core.security import get_current_user
from backend.api.models.user import User

router = APIRouter()


@router.get("/summary")
async def get_usage_summary(
    current_user: User = Depends(get_current_user)
):
    """Get global usage summary"""
    # TODO: Implement
    return {"total_users": 0, "total_quota_gb": 0, "total_used_gb": 0}
