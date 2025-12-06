from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any
from app.core.database import get_db
from app.core.security import get_current_active_admin
from app.models.user import User
from app.models.s3_connection import S3Connection
from app.schemas import (
    S3ConnectionCreate,
    S3ConnectionUpdate,
    S3ConnectionResponse,
    S3ConnectionList
)
from app.services.s3_service import s3_service

router = APIRouter(
    prefix="/s3-connections",
    tags=["s3-connections"]
)

@router.get("/", response_model=List[S3ConnectionList])
async def list_s3_connections(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """
    List all S3 connections
    """
    connections = db.query(S3Connection).all()
    return connections

@router.post("/", response_model=S3ConnectionResponse)
async def create_s3_connection(
    connection_in: S3ConnectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """
    Create a new S3 connection
    """
    # Check if name exists
    if db.query(S3Connection).filter(S3Connection.name == connection_in.name).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Connection with this name already exists"
        )
    
    connection = S3Connection(
        name=connection_in.name,
        account_id=connection_in.account_id,
        region=connection_in.region,
        auth_method=connection_in.auth_method,
        role_arn=connection_in.role_arn,
        external_id=connection_in.external_id,
        is_active=connection_in.is_active
    )
    
    # Set encrypted fields
    if connection_in.access_key_id:
        connection.access_key_id = connection_in.access_key_id
    if connection_in.secret_access_key:
        connection.secret_access_key = connection_in.secret_access_key
        
    db.add(connection)
    db.commit()
    db.refresh(connection)
    return connection

@router.get("/{connection_id}", response_model=S3ConnectionResponse)
async def get_s3_connection(
    connection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """
    Get a specific S3 connection
    """
    connection = db.query(S3Connection).filter(S3Connection.id == connection_id).first()
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="S3 connection not found"
        )
    return connection

@router.put("/{connection_id}", response_model=S3ConnectionResponse)
async def update_s3_connection(
    connection_id: int,
    connection_in: S3ConnectionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """
    Update an S3 connection
    """
    connection = db.query(S3Connection).filter(S3Connection.id == connection_id).first()
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="S3 connection not found"
        )
        
    # Check name uniqueness if changing name
    if connection_in.name and connection_in.name != connection.name:
        if db.query(S3Connection).filter(S3Connection.name == connection_in.name).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Connection with this name already exists"
            )
            
    # Update fields
    update_data = connection_in.model_dump(exclude_unset=True)
    
    # Handle encrypted fields separately
    if 'access_key_id' in update_data:
        connection.access_key_id = update_data.pop('access_key_id')
    if 'secret_access_key' in update_data:
        connection.secret_access_key = update_data.pop('secret_access_key')
        
    for field, value in update_data.items():
        setattr(connection, field, value)
        
    db.commit()
    db.refresh(connection)
    return connection

@router.delete("/{connection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_s3_connection(
    connection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """
    Delete an S3 connection
    """
    connection = db.query(S3Connection).filter(S3Connection.id == connection_id).first()
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="S3 connection not found"
        )
        
    # Check if used in permissions
    if connection.permissions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete connection that is used by permissions"
        )
        
    db.delete(connection)
    db.commit()
    return None

@router.post("/test", status_code=status.HTTP_200_OK)
async def test_s3_connection(
    connection_in: S3ConnectionCreate,
    current_user: User = Depends(get_current_active_admin)
):
    """
    Test an S3 connection configuration without saving it
    """
    # Create a temporary connection object (not saved to DB)
    temp_connection = S3Connection(
        name=connection_in.name,
        account_id=connection_in.account_id,
        region=connection_in.region,
        auth_method=connection_in.auth_method,
        role_arn=connection_in.role_arn,
        external_id=connection_in.external_id
    )
    
    if connection_in.access_key_id:
        temp_connection.access_key_id = connection_in.access_key_id
    if connection_in.secret_access_key:
        temp_connection.secret_access_key = connection_in.secret_access_key
        
    result = s3_service.test_connection(temp_connection)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Connection failed: {result['message']}"
        )
        
    return result
