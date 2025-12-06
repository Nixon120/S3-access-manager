from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    bucket_name = Column(String, nullable=False, index=True)
    prefix = Column(String, default="", nullable=False)  # Empty string means root
    can_read = Column(Boolean, default=True)
    can_write = Column(Boolean, default=False)
    can_delete = Column(Boolean, default=False)
    can_list = Column(Boolean, default=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # New field for S3 Connection
    s3_connection_id = Column(Integer, ForeignKey("s3_connections.id"), nullable=True)

    # Relationships
    user = relationship("User", back_populates="permissions")
    s3_connection = relationship("S3Connection", back_populates="permissions", lazy="joined")

