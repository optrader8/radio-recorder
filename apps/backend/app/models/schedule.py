from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.db.types import UUID_TYPE, generate_uuid


class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(UUID_TYPE, primary_key=True, default=generate_uuid)
    user_id = Column(UUID_TYPE, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    station_id = Column(UUID_TYPE, ForeignKey("radio_stations.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    cron_expression = Column(String(100), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    format = Column(String(10), default="mp3", nullable=False)
    bitrate = Column(Integer, default=128, nullable=False)
    sample_rate = Column(Integer, default=44100, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    next_run_at = Column(DateTime(timezone=True))

    # Relationships
    user = relationship("User", back_populates="schedules")
    station = relationship("RadioStation", back_populates="schedules")
    recordings = relationship("Recording", back_populates="schedule")
