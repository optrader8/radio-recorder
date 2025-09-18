from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RecordingCreate(BaseModel):
    station_id: UUID
    schedule_id: Optional[UUID] = None
    title: Optional[str] = None
    format: Optional[str] = None
    bitrate: Optional[int] = None
    sample_rate: Optional[int] = None
    duration_seconds: Optional[int] = None


class RecordingRead(BaseModel):
    id: UUID
    station_id: UUID
    schedule_id: Optional[UUID] = None
    title: Optional[str] = None
    status: str
    format: Optional[str] = None
    bitrate: Optional[int] = None
    sample_rate: Optional[int] = None
    duration_seconds: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
