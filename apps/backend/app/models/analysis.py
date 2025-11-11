"""
Database models for webhooks, analysis results, and event logs
"""
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Float, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

from app.db.base import Base


class WebhookModel(Base):
    """Webhook subscription model"""
    __tablename__ = "webhooks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    url = Column(String(500), nullable=False)
    event_types = Column(JSON, nullable=False)  # List of event types
    description = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    success_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    last_triggered_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<WebhookModel(id={self.id}, url={self.url})>"


class RecordingAnalysisModel(Base):
    """Recording analysis results model"""
    __tablename__ = "recording_analysis"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    recording_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    file_path = Column(String(500), nullable=False)

    # Transcription
    transcription_text = Column(Text, nullable=True)
    transcription_language = Column(String(10), default="unknown")
    transcription_confidence = Column(Float, default=0.0)

    # Voice analysis
    duration_seconds = Column(Float, nullable=True)
    num_speakers = Column(Integer, default=0)
    clarity_score = Column(Float, default=0.0)  # 0-100
    noise_level_db = Column(Float, default=0.0)
    snr_db = Column(Float, default=0.0)
    overall_quality = Column(Float, default=0.0)  # 0-100

    # Emotions and segments stored as JSON
    detected_emotions = Column(JSON, nullable=True)  # {emotion: confidence}
    speaker_segments = Column(JSON, nullable=True)  # [{speaker_id, start, end, duration}]
    detected_ads = Column(JSON, nullable=True)  # [{start, end, probability, confidence}]

    # Processing info
    processing_time_seconds = Column(Float, default=0.0)
    analysis_engine = Column(String(50), default="combined")  # transcription engine used

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<RecordingAnalysisModel(recording_id={self.recording_id})>"


class EventLogModel(Base):
    """Event log for audit and analytics"""
    __tablename__ = "event_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    event_type = Column(String(100), nullable=False, index=True)  # e.g., "recording.started"
    resource_type = Column(String(50), nullable=True)  # e.g., "recording"
    resource_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    data = Column(JSON, nullable=True)  # Event-specific data
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<EventLogModel(event_type={self.event_type}, user_id={self.user_id})>"


class PlaybackHistoryModel(Base):
    """Playback history for analytics"""
    __tablename__ = "playback_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    station_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    station_name = Column(String(200), nullable=False)
    duration_seconds = Column(Float, nullable=True)
    bitrate = Column(Integer, nullable=True)
    skip_ads = Column(Boolean, default=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<PlaybackHistoryModel(station={self.station_name})>"


class AdFeedbackModel(Base):
    """User feedback on ad detection accuracy"""
    __tablename__ = "ad_feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    recording_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    feedback_type = Column(String(50), nullable=False)  # "correct_ad", "false_positive", "missed_ad"
    confidence_before = Column(Float, nullable=True)  # ML model confidence
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<AdFeedbackModel(feedback={self.feedback_type})>"
