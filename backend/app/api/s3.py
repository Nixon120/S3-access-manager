from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas import (
    PresignedUrlRequest,
    PresignedUrlResponse,
    S3ListResponse,
    S3Object
)
from app.services.s3_service import s3_service
from app.services.permission_service import permission_service
from app.services.audit_service import audit_service

router = APIRouter(prefix="/s3", tags=["S3 Operations"])


class UploadCompleteRequest(BaseModel):
    bucket_name: str
    object_key: str
    status: str  # 'success' or 'failure'
    error_message: Optional[str] = None


@router.post("/upload-complete")
async def notify_upload_complete(
    request_data: UploadCompleteRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Receive notification of upload completion from frontend
    """
    try:
        # Log the actual upload result
        audit_service.log_action(
            db=db,
            user=current_user,
            action="upload",
            bucket_name=request_data.bucket_name,
            object_key=request_data.object_key,
            status=request_data.status,
            ip_address=request.client.host,
            error_message=request_data.error_message
        )
        
        return {
            "message": "Upload status recorded",
            "status": request_data.status
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record upload status: {str(e)}"
        )


import re

def sanitize_key(key: str) -> str:
    """
    Sanitize the filename part of an object key.
    Keeps the directory structure intact.
    """
    parts = key.split('/')
    filename = parts[-1]
    # Allow alphanumeric, dot, dash, underscore
    safe_filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    parts[-1] = safe_filename
    return '/'.join(parts)

@router.post("/presigned-url", response_model=PresignedUrlResponse)
async def get_presigned_url(
    request_data: PresignedUrlRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate a presigned URL for S3 upload or download
    """
    # Sanitize the object key if it's an upload
    object_key = request_data.object_key
    if request_data.operation == "upload":
        object_key = sanitize_key(object_key)

    # Determine action based on operation
    action = "write" if request_data.operation == "upload" else "read"
    
    # Check permissions and get the permission object
    try:
        permission = permission_service.check_permission(
            db=db,
            user=current_user,
            bucket_name=request_data.bucket_name,
            object_key=object_key,
            action=action
        )
    except HTTPException as e:
        # Log failed attempt
        audit_service.log_action(
            db=db,
            user=current_user,
            action=request_data.operation,
            bucket_name=request_data.bucket_name,
            object_key=object_key,
            status="failure",
            ip_address=request.client.host,
            error_message=e.detail
        )
        raise
    
    # Get S3 connection if permission specifies one
    s3_connection = None
    if permission and permission.s3_connection_id:
        from app.models.s3_connection import S3Connection
        s3_connection = db.query(S3Connection).filter(
            S3Connection.id == permission.s3_connection_id
        ).first()
    
    # Generate presigned URL
    try:
        if request_data.operation == "upload":
            # Use presigned POST for uploads
            response = s3_service.generate_presigned_post(
                bucket_name=request_data.bucket_name,
                object_key=object_key,
                connection=s3_connection
            )
            
            # Log successful generation (NOT the actual upload)
            audit_service.log_action(
                db=db,
                user=current_user,
                action="upload_initiated",
                bucket_name=request_data.bucket_name,
                object_key=object_key,
                status="success",
                ip_address=request.client.host
            )
            
            return PresignedUrlResponse(
                url=response['url'],
                expires_in=3600,
                fields=response['fields']
            )
        else:
            # Use presigned GET for downloads
            url = s3_service.generate_presigned_url(
                bucket_name=request_data.bucket_name,
                object_key=object_key,
                operation="get_object",
                connection=s3_connection
            )
            
            # Log successful generation
            audit_service.log_action(
                db=db,
                user=current_user,
                action="download_initiated",
                bucket_name=request_data.bucket_name,
                object_key=object_key,
                status="success",
                ip_address=request.client.host
            )
            
            return PresignedUrlResponse(
                url=url,
                expires_in=3600
            )
    
    except Exception as e:
        # Log error
        audit_service.log_action(
            db=db,
            user=current_user,
            action=request_data.operation,
            bucket_name=request_data.bucket_name,
            object_key=request_data.object_key,
            status="failure",
            ip_address=request.client.host,
            error_message=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate presigned URL: {str(e)}"
        )


@router.get("/list/{bucket_name}", response_model=S3ListResponse)
async def list_objects(
    bucket_name: str,
    prefix: str = "",
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List objects in an S3 bucket with optional prefix
    """
    # Check list permission and get the permission object
    try:
        permission = permission_service.check_permission(
            db=db,
            user=current_user,
            bucket_name=bucket_name,
            object_key=prefix,
            action="list"
        )
    except HTTPException as e:
        # Check for partial access if forbidden
        if e.status_code == status.HTTP_403_FORBIDDEN:
            from app.models.permission import Permission
            from datetime import datetime
            
            # Find permissions that are sub-paths of requested prefix
            user_permissions = db.query(Permission).filter(
                Permission.user_id == current_user.id,
                Permission.bucket_name == bucket_name,
                Permission.can_list == True
            ).all()
            
            allowed_prefixes = set()
            for perm in user_permissions:
                # If perm.prefix starts with requested prefix (and is longer)
                if perm.prefix.startswith(prefix) and len(perm.prefix) > len(prefix):
                    # Get the relative path part
                    relative = perm.prefix[len(prefix):]
                    # Get the first component
                    parts = relative.split('/')
                    if parts[0]:
                        allowed_prefixes.add(parts[0] + '/')
            
            if allowed_prefixes:
                synthetic_objects = []
                for p in sorted(allowed_prefixes):
                    synthetic_objects.append(S3Object(
                        key=prefix + p,
                        size=0,
                        last_modified=datetime.utcnow(),
                        etag="directory"
                    ))
                
                return S3ListResponse(
                    objects=synthetic_objects,
                    prefix=prefix,
                    bucket_name=bucket_name,
                    has_more=False
                )

        # Log failed attempt
        audit_service.log_action(
            db=db,
            user=current_user,
            action="list",
            bucket_name=bucket_name,
            object_key=prefix,
            status="failure",
            ip_address=request.client.host if request else None,
            error_message=e.detail
        )
        raise
    
    # Get S3 connection if permission specifies one
    s3_connection = None
    if permission and permission.s3_connection_id:
        from app.models.s3_connection import S3Connection
        s3_connection = db.query(S3Connection).filter(
            S3Connection.id == permission.s3_connection_id
        ).first()
    
    # List objects
    try:
        objects = s3_service.list_objects(
            bucket_name=bucket_name,
            prefix=prefix,
            connection=s3_connection
        )
        
        # Log successful list
        audit_service.log_action(
            db=db,
            user=current_user,
            action="list",
            bucket_name=bucket_name,
            object_key=prefix,
            status="success",
            ip_address=request.client.host if request else None,
            metadata={"object_count": len(objects)}
        )
        
        s3_objects = [
            S3Object(
                key=obj['key'],
                size=obj['size'],
                last_modified=obj['last_modified'],
                etag=obj['etag']
            )
            for obj in objects
        ]
        
        return S3ListResponse(
            objects=s3_objects,
            prefix=prefix,
            bucket_name=bucket_name,
            has_more=len(objects) >= 1000
        )
    
    except Exception as e:
        # Log error
        audit_service.log_action(
            db=db,
            user=current_user,
            action="list",
            bucket_name=bucket_name,
            object_key=prefix,
            status="failure",
            ip_address=request.client.host if request else None,
            error_message=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list objects: {str(e)}"
        )


@router.get("/buckets", response_model=List[str])
async def list_buckets(
    current_user: User = Depends(get_current_user)
):
    """
    List accessible S3 buckets
    For admin: all buckets
    For users: only buckets they have permissions for
    """
    try:
        if current_user.is_admin:
            # Admin can see all buckets
            return s3_service.list_buckets()
        else:
            # Regular users see only their accessible buckets
            # This would be retrieved from their permissions
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Use /api/v1/permissions/my-permissions to see your accessible buckets"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list buckets: {str(e)}"
        )


@router.delete("/object/{bucket_name}/{object_key:path}")
async def delete_object(
    bucket_name: str,
    object_key: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an S3 object (generates presigned DELETE URL)
    """
    # Check delete permission
    try:
        permission = permission_service.check_permission(
            db=db,
            user=current_user,
            bucket_name=bucket_name,
            object_key=object_key,
            action="delete"
        )
    except HTTPException as e:
        # Log failed attempt
        audit_service.log_action(
            db=db,
            user=current_user,
            action="delete",
            bucket_name=bucket_name,
            object_key=object_key,
            status="failure",
            ip_address=request.client.host,
            error_message=e.detail
        )
        raise
    
    # Get S3 connection if permission specifies one
    s3_connection = None
    if permission and permission.s3_connection_id:
        from app.models.s3_connection import S3Connection
        s3_connection = db.query(S3Connection).filter(
            S3Connection.id == permission.s3_connection_id
        ).first()
    
    try:
        # Delete object directly
        s3_service.delete_object(
            bucket_name=bucket_name,
            object_key=object_key,
            connection=s3_connection
        )
        
        # Log successful deletion
        audit_service.log_action(
            db=db,
            user=current_user,
            action="delete",
            bucket_name=bucket_name,
            object_key=object_key,
            status="success",
            ip_address=request.client.host
        )
        
        return {
            "message": "Object deleted successfully"
        }
    
    except Exception as e:
        # Log error
        audit_service.log_action(
            db=db,
            user=current_user,
            action="delete",
            bucket_name=bucket_name,
            object_key=object_key,
            status="failure",
            ip_address=request.client.host,
            error_message=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate delete URL: {str(e)}"
        )
