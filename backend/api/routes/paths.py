"""
Shared Paths Routes
CRUD operations for managing shared directories
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import os

from backend.core.database import get_db
from backend.core.security import get_current_active_admin
from backend.api.models.user import User, SharedPath
from backend.api.schemas.schemas import (
    SharedPathCreate,
    SharedPathUpdate,
    SharedPathResponse,
    MessageResponse
)

router = APIRouter()


@router.get("/", response_model=List[SharedPathResponse])
async def list_paths(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """List all shared paths"""
    paths = db.query(SharedPath).order_by(SharedPath.name).all()
    return paths


@router.post("/", response_model=SharedPathResponse, status_code=status.HTTP_201_CREATED)
async def create_path(
    path_data: SharedPathCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """Create a new shared path"""
    # Check if path name already exists
    existing = db.query(SharedPath).filter(SharedPath.name == path_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Path with name '{path_data.name}' already exists"
        )
    
    # Validate filesystem path exists
    if not os.path.isabs(path_data.path):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Path must be an absolute path"
        )
    
    # Create directory if it doesn't exist
    if not os.path.exists(path_data.path):
        try:
            os.makedirs(path_data.path, exist_ok=True)
        except PermissionError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot create directory: Permission denied"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot create directory: {str(e)}"
            )
    
    # Create shared path
    db_path = SharedPath(
        name=path_data.name,
        path=path_data.path,
        description=path_data.description,
        protocols=path_data.protocols
    )
    
    db.add(db_path)
    db.commit()
    db.refresh(db_path)
    
    return db_path


@router.get("/{path_id}", response_model=SharedPathResponse)
async def get_path(
    path_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """Get a specific shared path"""
    path = db.query(SharedPath).filter(SharedPath.id == path_id).first()
    if not path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shared path not found"
        )
    return path


@router.put("/{path_id}", response_model=SharedPathResponse)
async def update_path(
    path_id: str,
    path_data: SharedPathUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """Update a shared path"""
    path = db.query(SharedPath).filter(SharedPath.id == path_id).first()
    if not path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shared path not found"
        )
    
    # Update fields if provided
    if path_data.name is not None:
        # Check for duplicates
        existing = db.query(SharedPath).filter(
            SharedPath.name == path_data.name,
            SharedPath.id != path_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Path with name '{path_data.name}' already exists"
            )
        path.name = path_data.name
    
    if path_data.path is not None:
        if not os.path.isabs(path_data.path):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Path must be an absolute path"
            )
        path.path = path_data.path
    
    if path_data.description is not None:
        path.description = path_data.description
    
    if path_data.protocols is not None:
        path.protocols = path_data.protocols
    
    db.commit()
    db.refresh(path)
    
    return path


@router.delete("/{path_id}", response_model=MessageResponse)
async def delete_path(
    path_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """Delete a shared path"""
    path = db.query(SharedPath).filter(SharedPath.id == path_id).first()
    if not path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shared path not found"
        )
    
    db.delete(path)
    db.commit()
    
    return {"message": f"Shared path '{path.name}' deleted successfully"}
