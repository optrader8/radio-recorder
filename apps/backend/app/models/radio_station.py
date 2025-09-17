from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base


class RadioStation(Base):
    __tablename__ = "radio_stations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    stream_url = Column(String(500), nullable=False)
    description = Column(Text)
    genre = Column(String(100))
    country = Column(String(100))
    language = Column(String(50))

    # Relationships
    schedules = relationship("Schedule", back_populates="station")
    recordings = relationship("Recording", back_populates="station")