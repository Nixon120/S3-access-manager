from sqlalchemy.orm import Session
from app.models.user import User
from app.models.permission import Permission
from typing import Optional, List
from fastapi import HTTPException, status


class PermissionService:
    @staticmethod
    def check_permission(
        db: Session,
        user: User,
        bucket_name: str,
        object_key: str,
        action: str
    ) -> Permission:
        """
        Check if user has permission for a specific action on an S3 object
        
        Args:
            db: Database session
            user: User to check permissions for
            bucket_name: S3 bucket name
            object_key: S3 object key
            action: Action to check (read, write, delete, list)
        
        Returns:
            Permission object if user has permission, raises HTTPException otherwise
        """
        # Admin users have all permissions - return None (will use default connection)
        if user.is_admin:
            return None
        
        # Get all permissions for this user and bucket
        permissions = db.query(Permission).filter(
            Permission.user_id == user.id,
            Permission.bucket_name == bucket_name
        ).all()
        
        if not permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No access to bucket: {bucket_name}"
            )
        
        # Check if any permission matches the object key prefix
        matching_permission = None
        for perm in permissions:
            # Check if object_key starts with the permission prefix
            if object_key.startswith(perm.prefix):
                # Check specific action permission
                if action == "read" and perm.can_read:
                    matching_permission = perm
                    break
                elif action == "write" and perm.can_write:
                    matching_permission = perm
                    break
                elif action == "delete" and perm.can_delete:
                    matching_permission = perm
                    break
                elif action == "list" and perm.can_list:
                    matching_permission = perm
                    break
        
        if not matching_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No {action} permission for: {bucket_name}/{object_key}"
            )
        
        return matching_permission
    
    @staticmethod
    def get_user_permissions(
        db: Session,
        user: User
    ) -> List[Permission]:
        """Get all permissions for a user"""
        return db.query(Permission).filter(
            Permission.user_id == user.id
        ).all()
    
    @staticmethod
    def get_accessible_buckets(
        db: Session,
        user: User
    ) -> List[dict]:
        """
        Get all buckets and prefixes a user can access
        
        Returns:
            List of dicts with bucket_name, prefix, and permissions
        """
        if user.is_admin:
            # Admin can see all buckets - would need to query AWS
            return []
        
        permissions = db.query(Permission).filter(
            Permission.user_id == user.id
        ).all()
        
        accessible = []
        for perm in permissions:
            accessible.append({
                'bucket_name': perm.bucket_name,
                'prefix': perm.prefix,
                'can_read': perm.can_read,
                'can_write': perm.can_write,
                'can_delete': perm.can_delete,
                'can_list': perm.can_list,
                'description': perm.description
            })
        
        return accessible
    
    @staticmethod
    def create_permission(
        db: Session,
        user_id: int,
        bucket_name: str,
        prefix: str = "",
        can_read: bool = True,
        can_write: bool = False,
        can_delete: bool = False,
        can_list: bool = True,
        description: Optional[str] = None,
        s3_connection_id: Optional[int] = None
    ) -> Permission:
        """Create a new permission for a user"""
        permission = Permission(
            user_id=user_id,
            bucket_name=bucket_name,
            prefix=prefix,
            can_read=can_read,
            can_write=can_write,
            can_delete=can_delete,
            can_list=can_list,
            description=description,
            s3_connection_id=s3_connection_id
        )
        
        db.add(permission)
        db.commit()
        db.refresh(permission)
        
        return permission
    
    @staticmethod
    def update_permission(
        db: Session,
        permission_id: int,
        **kwargs
    ) -> Permission:
        """Update an existing permission"""
        permission = db.query(Permission).filter(
            Permission.id == permission_id
        ).first()
        
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )
        
        # Update fields - allow None for s3_connection_id to reset to default
        for key, value in kwargs.items():
            if hasattr(permission, key):
                # Handle s3_connection_id specially - allow None to reset to default
                if key == 's3_connection_id':
                    setattr(permission, key, value)
                elif value is not None:
                    setattr(permission, key, value)
        
        db.commit()
        db.refresh(permission)
        
        return permission
    
    @staticmethod
    def delete_permission(
        db: Session,
        permission_id: int
    ) -> bool:
        """Delete a permission"""
        permission = db.query(Permission).filter(
            Permission.id == permission_id
        ).first()
        
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )
        
        db.delete(permission)
        db.commit()
        
        return True


# Singleton instance
permission_service = PermissionService()
