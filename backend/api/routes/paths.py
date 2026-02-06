"""
Shared Paths Routes
Placeholder for paths management
"""

from fastapi import APIRouter, Depends
from backend.core.security import get_current_active_admin
from backend.api.models.user import User

router = APIRouter()


@router.get("/")
async def list_paths(
    current_user: User = Depends(get_current_active_admin)
):
    """List shared paths"""
    # TODO: Implement
    return []


@router.post("/")
async def create_path(
    current_user: User = Depends(get_current_active_admin)
):
    """Create shared path"""
    # TODO: Implement
    return {"message": "Not implemented"}
