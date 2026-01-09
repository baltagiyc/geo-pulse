"""Health check endpoint."""

from datetime import datetime

from fastapi import APIRouter

from src.api.schemas.response import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check() -> HealthResponse:
    """
    Health check endpoint.

    Returns the API status and current timestamp.
    Used to verify that the API is running and accessible.
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat() + "Z",
    )
