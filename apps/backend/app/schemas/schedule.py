from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ScheduleCreate(BaseModel):
    station_id: UUID
    name: str
    cron_expression: str
    duration_minutes: int
    format: Optional[str] = "mp3"
    bitrate: Optional[int] = 128
    sample_rate: Optional[int] = 44100
    is_active: bool = True


class ScheduleRead(BaseModel):
    id: UUID
    station_id: UUID
    user_id: UUID
    name: str
    cron_expression: str
    duration_minutes: int
    format: str
    bitrate: int
    sample_rate: int
    is_active: bool
    created_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
