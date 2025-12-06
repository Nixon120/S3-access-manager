from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.security import get_current_user, get_current_active_admin
from app.models.user import User
from app.models.audit_log import AuditLog
from app.schemas import AuditLogResponse, SystemStats, UserStats

router = APIRouter(prefix="/audit", tags=["Audit Logs"])


@router.get("/logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    user_id: Optional[int] = None,
    bucket_name: Optional[str] = None,
    action: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(100, le=500),
    skip: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """
    Get audit logs with optional filters (admin only)
    """
    query = db.query(AuditLog)
    
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    
    if bucket_name:
        query = query.filter(AuditLog.bucket_name == bucket_name)
    
    if action:
        if action == "upload":
            # Include both upload and upload_initiated for "upload" filter
            query = query.filter(AuditLog.action.in_(["upload", "upload_initiated"]))
        else:
            query = query.filter(AuditLog.action == action)
    
    if status:
        query = query.filter(AuditLog.status == status)
    
    logs = query.order_by(AuditLog.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    # Convert to response objects manually to avoid metadata conflict
    # (SQLAlchemy models have a .metadata attribute that conflicts with our metadata field)
    response_logs = []
    for log in logs:
        response_logs.append(AuditLogResponse(
            id=log.id,
            user_id=log.user_id,
            action=log.action,
            bucket_name=log.bucket_name,
            object_key=log.object_key,
            status=log.status,
            ip_address=log.ip_address,
            meta=log.meta,
            error_message=log.error_message,
            created_at=log.created_at
        ))
    
    return response_logs


@router.get("/my-activity", response_model=List[AuditLogResponse])
async def get_my_activity(
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's activity logs
    """
    logs = db.query(AuditLog)\
        .filter(AuditLog.user_id == current_user.id)\
        .order_by(AuditLog.created_at.desc())\
        .limit(limit)\
        .all()
    
    # Convert to response objects manually
    response_logs = []
    for log in logs:
        response_logs.append(AuditLogResponse(
            id=log.id,
            user_id=log.user_id,
            action=log.action,
            bucket_name=log.bucket_name,
            object_key=log.object_key,
            status=log.status,
            ip_address=log.ip_address,
            meta=log.meta,
            error_message=log.error_message,
            created_at=log.created_at
        ))
    
    return response_logs


@router.get("/stats", response_model=SystemStats)
async def get_system_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """
    Get system-wide statistics (admin only)
    """
    from app.models.permission import Permission
    
    # Count users
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    
    # Count unique buckets
    total_buckets = db.query(Permission.bucket_name).distinct().count()
    
    # Count permissions
    total_permissions = db.query(Permission).count()
    
    # Get recent activity (last 20)
    recent_activity_logs = db.query(AuditLog)\
        .order_by(AuditLog.created_at.desc())\
        .limit(20)\
        .all()
    
    # Convert to response objects manually to avoid metadata conflict
    recent_activity = []
    for log in recent_activity_logs:
        recent_activity.append(AuditLogResponse(
            id=log.id,
            user_id=log.user_id,
            action=log.action,
            bucket_name=log.bucket_name,
            object_key=log.object_key,
            status=log.status,
            ip_address=log.ip_address,
            meta=log.meta,
            error_message=log.error_message,
            created_at=log.created_at
        ))
    
    return SystemStats(
        total_users=total_users,
        active_users=active_users,
        total_buckets=total_buckets,
        total_permissions=total_permissions,
        recent_activity=recent_activity
    )


@router.get("/user-stats/{user_id}", response_model=UserStats)
async def get_user_stats(
    user_id: int,
    days: int = Query(30, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """
    Get statistics for a specific user (admin only)
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Count uploads
    total_uploads = db.query(AuditLog).filter(
        AuditLog.user_id == user_id,
        AuditLog.action.in_(["upload", "upload_initiated"]),
        AuditLog.status == "success",
        AuditLog.created_at >= cutoff_date
    ).count()
    
    # Count downloads
    total_downloads = db.query(AuditLog).filter(
        AuditLog.user_id == user_id,
        AuditLog.action.in_(["download", "download_initiated"]),
        AuditLog.status == "success",
        AuditLog.created_at >= cutoff_date
    ).count()
    
    # Get last activity
    last_log = db.query(AuditLog).filter(
        AuditLog.user_id == user_id
    ).order_by(AuditLog.created_at.desc()).first()
    
    return UserStats(
        total_uploads=total_uploads,
        total_downloads=total_downloads,
        total_storage_bytes=0,  # Would need to track this separately
        last_activity=last_log.created_at if last_log else None
    )
