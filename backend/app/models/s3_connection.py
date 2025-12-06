from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base
from app.core.config import settings
from cryptography.fernet import Fernet
import base64
import logging

logger = logging.getLogger(__name__)

class AuthMethod(str, enum.Enum):
    ACCESS_KEY = "access_key"
    IAM_ROLE = "iam_role"
    IAM_ROLES_ANYWHERE = "iam_roles_anywhere"

class S3Connection(Base):
    __tablename__ = "s3_connections"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    account_id = Column(String, nullable=False)
    region = Column(String, default="us-east-1", nullable=False)
    auth_method = Column(SQLEnum(AuthMethod), default=AuthMethod.ACCESS_KEY, nullable=False)
    
    # Encrypted fields
    _access_key_id = Column("access_key_id", String, nullable=True)
    _secret_access_key = Column("secret_access_key", String, nullable=True)
    
    # IAM Role fields
    role_arn = Column(String, nullable=True)
    external_id = Column(String, nullable=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    permissions = relationship("Permission", back_populates="s3_connection")

    def _get_fernet(self):
        # Create a key from the SECRET_KEY (must be 32 url-safe base64-encoded bytes)
        # We'll use the first 32 chars of SECRET_KEY padded/adjusted if needed
        # For simplicity in this implementation, we derive a key
        key = settings.SECRET_KEY
        if len(key) < 32:
            key = key.ljust(32, '0')
        key = key[:32].encode('utf-8')
        return Fernet(base64.urlsafe_b64encode(key))

    @property
    def access_key_id(self):
        if not self._access_key_id:
            return None
        try:
            f = self._get_fernet()
            return f.decrypt(self._access_key_id.encode('utf-8')).decode('utf-8')
        except Exception as e:
            logger.error(f"Error decrypting access key: {e}")
            return None

    @access_key_id.setter
    def access_key_id(self, value):
        if value:
            f = self._get_fernet()
            self._access_key_id = f.encrypt(value.encode('utf-8')).decode('utf-8')
        else:
            self._access_key_id = None

    @property
    def secret_access_key(self):
        if not self._secret_access_key:
            return None
        try:
            f = self._get_fernet()
            return f.decrypt(self._secret_access_key.encode('utf-8')).decode('utf-8')
        except Exception as e:
            logger.error(f"Error decrypting secret key: {e}")
            return None

    @secret_access_key.setter
    def secret_access_key(self, value):
        if value:
            f = self._get_fernet()
            self._secret_access_key = f.encrypt(value.encode('utf-8')).decode('utf-8')
        else:
            self._secret_access_key = None
