from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.db.types import INET_TYPE, JSON_TYPE, UUID_TYPE, generate_uuid


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(UUID_TYPE, primary_key=True, default=generate_uuid)
    user_id = Column(UUID_TYPE, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    action = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(UUID_TYPE)
    details = Column(JSON_TYPE)
    ip_address = Column(INET_TYPE)
    user_agent = Column(Text)

    # Relationships
    user = relationship("User", back_populates="audit_logs")
