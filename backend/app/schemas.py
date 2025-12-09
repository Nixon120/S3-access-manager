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
    must_change_password: bool
    created_at: datetime
    last_login: Optional[datetime] = None


class UserChangePassword(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)

# Permission Schemas (moved set before UserWithPermissions to avoid forward ref issues)
class PermissionBase(BaseModel):
    bucket_name: str
    prefix: str = ""
    can_read: bool = True
    can_write: bool = False
    can_delete: bool = False
    can_list: bool = True
    description: Optional[str] = None
    s3_connection_id: Optional[int] = None


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
    s3_connection_id: Optional[int] = None


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


# S3 Connection Schemas
class S3ConnectionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    account_id: str = Field(..., pattern=r"^\d{12}$", description="12-digit AWS Account ID")
    region: str = Field(default="us-east-1")
    auth_method: str = Field(default="access_key")
    
    # Optional fields based on auth method
    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None
    role_arn: Optional[str] = None
    external_id: Optional[str] = None
    is_active: bool = True


class S3ConnectionCreate(S3ConnectionBase):
    pass


class S3ConnectionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    account_id: Optional[str] = Field(None, pattern=r"^\d{12}$")
    region: Optional[str] = None
    auth_method: Optional[str] = None
    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None
    role_arn: Optional[str] = None
    external_id: Optional[str] = None
    is_active: Optional[bool] = None


class S3ConnectionResponse(S3ConnectionBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Override secret fields to not return them in response
    access_key_id: Optional[str] = Field(None, exclude=True) 
    secret_access_key: Optional[str] = Field(None, exclude=True)


class S3ConnectionList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    account_id: str
    region: str
    auth_method: str
    is_active: bool
    created_at: datetime

