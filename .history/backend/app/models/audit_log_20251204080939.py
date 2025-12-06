from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False, index=True)  # upload, download, delete, list
    bucket_name = Column(String, nullable=False, index=True)
    object_key = Column(String, nullable=False)
    status = Column(String, nullable=False)  # success, failure
    ip_address = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    meta = Column('metadata', JSON, nullable=True)  # Additional context stored in DB column 'metadata'
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    @property
    def metadata(self):
        return self.meta

    @metadata.setter
    def metadata(self, value):
        self.meta = value
