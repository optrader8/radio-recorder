from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.db.types import JSON_TYPE, UUID_TYPE, generate_uuid


class AIAnalysis(Base):
    __tablename__ = "ai_analysis"

    id = Column(UUID_TYPE, primary_key=True, default=generate_uuid)
    recording_id = Column(UUID_TYPE, ForeignKey("recordings.id", ondelete="CASCADE"), nullable=False)

    analysis_type = Column(String(50), nullable=False)  # transcription, summary, keywords, speakers
    result = Column(JSON_TYPE, nullable=False)
    confidence_score = Column(Float)
    processing_time_seconds = Column(Integer)

    # Relationships
    recording = relationship("Recording", back_populates="ai_analyses")
