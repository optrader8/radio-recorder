from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.db.types import UUID_TYPE, generate_uuid


class User(Base):
    __tablename__ = "users"

    id = Column(UUID_TYPE, primary_key=True, default=generate_uuid)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="user", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    schedules = relationship("Schedule", back_populates="user", cascade="all, delete-orphan")
    recordings = relationship("Recording", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")
