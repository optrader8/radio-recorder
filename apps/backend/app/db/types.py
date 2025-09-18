from sqlalchemy import JSON, String
from sqlalchemy.types import TypeEngine
from uuid import UUID, uuid4

from app.core.config import settings

IS_SQLITE = settings.DATABASE_URL.startswith("sqlite")

if not IS_SQLITE:
    from sqlalchemy.dialects.postgresql import INET as _INET  # type: ignore
    from sqlalchemy.dialects.postgresql import JSONB as _JSONB  # type: ignore
    from sqlalchemy.dialects.postgresql import UUID as _UUID  # type: ignore

    UUID_TYPE: TypeEngine = _UUID(as_uuid=True)
    JSON_TYPE: TypeEngine = _JSONB
    INET_TYPE: TypeEngine = _INET
else:
    # SQLite fallback types for testing purposes
    UUID_TYPE = String(36)
    JSON_TYPE = JSON
    INET_TYPE = String(45)


def generate_uuid() -> str | UUID:
    value = uuid4()
    if IS_SQLITE:
        return str(value)
    return value


def parse_uuid(value: str | UUID) -> str | UUID:
    if IS_SQLITE:
        return str(value)
    if isinstance(value, UUID):
        return value
    return UUID(str(value))


__all__ = [
    "UUID_TYPE",
    "JSON_TYPE",
    "INET_TYPE",
    "IS_SQLITE",
    "generate_uuid",
    "parse_uuid",
]
