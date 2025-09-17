from typing import List, Optional, Union
from pydantic import AnyHttpUrl, EmailStr, field_validator
from pydantic_settings import BaseSettings
import secrets


class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # CORS
    CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # File Storage
    STORAGE_PATH: str = "/app/recordings"
    MAX_STORAGE_GB: int = 100

    # External Services
    WHISPER_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None

    # Security
    API_KEY_EXPIRE_DAYS: int = 365

    # Celery
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    @field_validator("CELERY_BROKER_URL", mode="before")
    @classmethod
    def set_celery_broker_url(cls, v: Optional[str], values) -> str:
        if v:
            return v
        redis_url = values.data.get("REDIS_URL", "redis://localhost:6379/0")
        return redis_url

    @field_validator("CELERY_RESULT_BACKEND", mode="before")
    @classmethod
    def set_celery_result_backend(cls, v: Optional[str], values) -> str:
        if v:
            return v
        redis_url = values.data.get("REDIS_URL", "redis://localhost:6379/0")
        return redis_url

    # Superuser
    FIRST_SUPERUSER_EMAIL: Optional[EmailStr] = None
    FIRST_SUPERUSER_PASSWORD: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()