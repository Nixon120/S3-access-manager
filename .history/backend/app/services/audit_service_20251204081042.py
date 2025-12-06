from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog
from app.models.user import User
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class AuditService:
    @staticmethod
    def log_action(
        db: Session,
        user: User,
        action: str,
        bucket_name: str,
        object_key: str,
        status: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        metadata: Optional[Dict] = None,
        error_message: Optional[str] = None
    ) -> AuditLog:
        """
        Log a user action to the audit trail
        
        Args:
            db: Database session
            user: User who performed the action
            action: Action type (upload, download, delete, list)
            bucket_name: S3 bucket name
            object_key: S3 object key
            status: Action status (success, failure)
            ip_address: User's IP address
            user_agent: User's browser/client info
            metadata: Additional context
            error_message: Error message if status is failure
        
        Returns:
            Created AuditLog entry
        """
        audit_log = AuditLog(
            user_id=user.id,
            action=action,
            bucket_name=bucket_name,
            object_key=object_key,
            status=status,
            ip_address=ip_address,
            user_agent=user_agent,
            meta=metadata,
            error_message=error_message
        )
        
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        
        # Also log to application logger for CloudWatch
        log_message = (
            f"AUDIT: user={user.email} action={action} "
            f"bucket={bucket_name} key={object_key} status={status}"
        )
        
        if status == "success":
            logger.info(log_message, extra={
                'user_id': user.id,
                'action': action,
                'bucket': bucket_name,
                'object_key': object_key
            })
        else:
            logger.error(log_message, extra={
                'user_id': user.id,
                'action': action,
                'bucket': bucket_name,
                'object_key': object_key,
                'error': error_message
            })
        
        return audit_log
    
    @staticmethod
    def get_user_logs(
        db: Session,
        user_id: int,
        limit: int = 100
    ):
        """Get audit logs for a specific user"""
        return db.query(AuditLog)\
            .filter(AuditLog.user_id == user_id)\
            .order_by(AuditLog.created_at.desc())\
            .limit(limit)\
            .all()
    
    @staticmethod
    def get_recent_logs(
        db: Session,
        limit: int = 100
    ):
        """Get recent audit logs across all users"""
        return db.query(AuditLog)\
            .order_by(AuditLog.created_at.desc())\
            .limit(limit)\
            .all()
    
    @staticmethod
    def get_logs_by_bucket(
        db: Session,
        bucket_name: str,
        limit: int = 100
    ):
        """Get audit logs for a specific bucket"""
        return db.query(AuditLog)\
            .filter(AuditLog.bucket_name == bucket_name)\
            .order_by(AuditLog.created_at.desc())\
            .limit(limit)\
            .all()


# Singleton instance
audit_service = AuditService()
