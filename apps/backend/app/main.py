from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn

from app.api.api_v1 import api_router
from app.core.config import settings
from app.core.logging import setup_logging

# Set up logging
setup_logging()

app = FastAPI(
    title="Radio Recorder API",
    description="A headless radio recording system with web dashboard",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json" if settings.ENVIRONMENT != "production" else None,
    docs_url="/api/v1/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/api/v1/redoc" if settings.ENVIRONMENT != "production" else None,
)

# Set up CORS
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Add trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "0.0.0.0", "radio-recorder.local"]
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    """Root endpoint for health checking"""
    return {
        "message": "Radio Recorder API",
        "version": "1.0.0",
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )