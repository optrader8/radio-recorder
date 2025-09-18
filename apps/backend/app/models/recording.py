from sqlalchemy import Column, String, Integer, BigInteger, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.db.types import JSON_TYPE, UUID_TYPE, generate_uuid


class Recording(Base):
    __tablename__ = "recordings"

    id = Column(UUID_TYPE, primary_key=True, default=generate_uuid)
    user_id = Column(UUID_TYPE, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    station_id = Column(UUID_TYPE, ForeignKey("radio_stations.id", ondelete="CASCADE"), nullable=False)
    schedule_id = Column(UUID_TYPE, ForeignKey("schedules.id", ondelete="SET NULL"), nullable=True)

    title = Column(String(255))
    file_path = Column(String(500))
    file_size = Column(BigInteger)
    duration_seconds = Column(Integer)
    format = Column(String(10))
    bitrate = Column(Integer)
    sample_rate = Column(Integer)

    status = Column(String(20), default="pending", nullable=False)  # pending, recording, completed, failed
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    error_message = Column(Text)
    metadata_json = Column("metadata", JSON_TYPE)

    # Relationships
    user = relationship("User", back_populates="recordings")
    station = relationship("RadioStation", back_populates="recordings")
    schedule = relationship("Schedule", back_populates="recordings")
    ai_analyses = relationship("AIAnalysis", back_populates="recording", cascade="all, delete-orphan")
