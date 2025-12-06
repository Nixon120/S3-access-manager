from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_active_admin, get_current_user
from app.models.user import User
from app.models.permission import Permission
from app.schemas import (
    PermissionCreate,
    PermissionUpdate,
    PermissionResponse
)
from app.services.permission_service import permission_service

router = APIRouter(prefix="/permissions", tags=["Permissions"])


@router.get("/", response_model=List[PermissionResponse])
async def list_permissions(
    user_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """
    List all permissions or filter by user_id (admin only)
    """
    query = db.query(Permission)
    
    if user_id:
        query = query.filter(Permission.user_id == user_id)
    
    permissions = query.all()
    return permissions


@router.get("/my-permissions", response_model=List[dict])
async def get_my_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's accessible buckets and permissions
    """
    return permission_service.get_accessible_buckets(db, current_user)


@router.post("/", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
async def create_permission(
    permission_data: PermissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """
    Create a new permission (admin only)
    """
    # Verify user exists
    user = db.query(User).filter(User.id == permission_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    permission = permission_service.create_permission(
        db=db,
        user_id=permission_data.user_id,
        bucket_name=permission_data.bucket_name,
        prefix=permission_data.prefix,
        can_read=permission_data.can_read,
        can_write=permission_data.can_write,
        can_delete=permission_data.can_delete,
        can_list=permission_data.can_list,
        description=permission_data.description,
        s3_connection_id=permission_data.s3_connection_id
    )
    
    return permission


@router.put("/{permission_id}", response_model=PermissionResponse)
async def update_permission(
    permission_id: int,
    permission_data: PermissionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """
    Update a permission (admin only)
    """
    update_dict = permission_data.model_dump(exclude_unset=True)
    permission = permission_service.update_permission(
        db=db,
        permission_id=permission_id,
        **update_dict
    )
    
    return permission


@router.delete("/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """
    Delete a permission (admin only)
    """
    permission_service.delete_permission(db=db, permission_id=permission_id)
    return None
