from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base


class AIAnalysis(Base):
    __tablename__ = "ai_analysis"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recording_id = Column(UUID(as_uuid=True), ForeignKey("recordings.id", ondelete="CASCADE"), nullable=False)

    analysis_type = Column(String(50), nullable=False)  # transcription, summary, keywords, speakers
    result = Column(JSONB, nullable=False)
    confidence_score = Column(Float)
    processing_time_seconds = Column(Integer)

    # Relationships
    recording = relationship("Recording", back_populates="ai_analyses")