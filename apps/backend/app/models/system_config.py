from sqlalchemy import Column, String, Text

from app.db.base import Base
from app.db.types import JSON_TYPE


class SystemConfig(Base):
    __tablename__ = "system_config"

    key = Column(String(100), primary_key=True)
    value = Column(JSON_TYPE, nullable=False)
    description = Column(Text)
