from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import JSONB

from app.db.base import Base


class SystemConfig(Base):
    __tablename__ = "system_config"

    key = Column(String(100), primary_key=True)
    value = Column(JSONB, nullable=False)
    description = Column(Text)