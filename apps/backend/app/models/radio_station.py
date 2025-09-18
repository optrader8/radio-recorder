from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.db.types import UUID_TYPE, generate_uuid


class RadioStation(Base):
    __tablename__ = "radio_stations"

    id = Column(UUID_TYPE, primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    stream_url = Column(String(500), nullable=False)
    description = Column(Text)
    genre = Column(String(100))
    country = Column(String(100))
    language = Column(String(50))

    # Relationships
    schedules = relationship("Schedule", back_populates="station")
    recordings = relationship("Recording", back_populates="station")
