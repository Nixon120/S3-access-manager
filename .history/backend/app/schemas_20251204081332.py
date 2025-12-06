from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    is_admin: bool = False


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    last_login: Optional[datetime] = None

# Permission Schemas (moved set before UserWithPermissions to avoid forward ref issues)
class PermissionBase(BaseModel):
    bucket_name: str
    prefix: str = ""
    can_read: bool = True
    can_write: bool = False
    can_delete: bool = False
    can_list: bool = True
    description: Optional[str] = None


class PermissionCreate(PermissionBase):
    user_id: int


class PermissionUpdate(BaseModel):
    bucket_name: Optional[str] = None
    prefix: Optional[str] = None
    can_read: Optional[bool] = None
    can_write: Optional[bool] = None
    can_delete: Optional[bool] = None
    can_list: Optional[bool] = None
    description: Optional[str] = None


class PermissionResponse(PermissionBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    created_at: datetime


class UserWithPermissions(UserResponse):
    permissions: List['PermissionResponse'] = []



# Audit Log Schemas
class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    action: str
    bucket_name: str
    object_key: str
    status: str
    ip_address: Optional[str] = None
    meta: Optional[dict] = Field(None, alias="metadata")
    error_message: Optional[str] = None
    created_at: datetime


# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# S3 Schemas
class PresignedUrlRequest(BaseModel):
    bucket_name: str
    object_key: str
    operation: str = Field(..., pattern="^(upload|download)$")


class PresignedUrlResponse(BaseModel):
    url: str
    expires_in: int
    fields: Optional[dict] = None  # For multipart uploads


class S3Object(BaseModel):
    key: str
    size: int
    last_modified: datetime
    etag: Optional[str] = None


class S3ListResponse(BaseModel):
    objects: List[S3Object]
    prefix: str
    bucket_name: str
    has_more: bool = False


# Stats Schemas
class UserStats(BaseModel):
    total_uploads: int
    total_downloads: int
    total_storage_bytes: int
    last_activity: Optional[datetime] = None


class SystemStats(BaseModel):
    total_users: int
    active_users: int
    total_buckets: int
    total_permissions: int
    recent_activity: List[AuditLogResponse]
