"""
📁 File: src/interfaces/http/routes/health.py
Layer: Interfaces (HTTP)
Purpose: Health check endpoints for monitoring and readiness
Depends on: src/shared/config, src/shared/logger
Used by: Load balancers, monitoring systems, Kubernetes

Health check endpoints:
- /health - Basic liveness check
- /health/ready - Readiness check (all dependencies available)
- /health/live - Liveness check (application is running)
"""

from typing import Any

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from src.shared.config import get_settings
from src.shared.logger import get_logger

# Initialize
router = APIRouter()
settings = get_settings()
logger = get_logger(__name__)


class HealthResponse(BaseModel):
    """Health check response model."""
    
    status: str = Field(..., description="Health status (healthy/unhealthy)")
    version: str = Field(..., description="Application version")
    environment: str = Field(..., description="Deployment environment")


class ReadinessResponse(BaseModel):
    """Readiness check response model with dependency status."""
    
    status: str = Field(..., description="Overall readiness status")
    version: str = Field(..., description="Application version")
    checks: dict[str, Any] = Field(..., description="Individual dependency checks")


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Basic health check endpoint. Returns 200 if application is running.",
)
async def health_check() -> JSONResponse:
    """
    Basic health check endpoint.
    
    This endpoint always returns 200 OK if the application is running.
    Used for basic liveness checks.
    
    Returns:
        JSONResponse with health status
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "healthy",
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
        },
    )


@router.get(
    "/health/live",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Liveness Check",
    description="Kubernetes liveness probe. Returns 200 if application process is alive.",
)
async def liveness_check() -> JSONResponse:
    """
    Liveness check for Kubernetes.
    
    Returns 200 OK if the application process is running.
    Does not check external dependencies.
    
    Returns:
        JSONResponse with liveness status
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "alive",
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
        },
    )


@router.get(
    "/health/ready",
    response_model=ReadinessResponse,
    status_code=status.HTTP_200_OK,
    summary="Readiness Check",
    description="Kubernetes readiness probe. Returns 200 if all dependencies are available.",
)
async def readiness_check() -> JSONResponse:
    """
    Readiness check for Kubernetes.
    
    Checks if the application is ready to accept traffic by verifying:
    - Database connection
    - Redis connection
    - Qdrant connection
    - Any other critical dependencies
    
    Returns:
        JSONResponse with readiness status and dependency checks
        
    Note:
        Currently returns basic status. TODO: Add actual dependency checks.
    """
    checks: dict[str, Any] = {}
    overall_status = "ready"
    status_code = status.HTTP_200_OK
    
    # TODO: Check PostgreSQL connection
    # try:
    #     await database.execute("SELECT 1")
    #     checks["database"] = {"status": "healthy", "latency_ms": 0}
    # except Exception as e:
    #     checks["database"] = {"status": "unhealthy", "error": str(e)}
    #     overall_status = "not_ready"
    #     status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    
    checks["database"] = {"status": "not_checked", "message": "TODO: Implement check"}
    
    # TODO: Check Redis connection
    # try:
    #     await redis.ping()
    #     checks["redis"] = {"status": "healthy", "latency_ms": 0}
    # except Exception as e:
    #     checks["redis"] = {"status": "unhealthy", "error": str(e)}
    #     overall_status = "not_ready"
    #     status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    
    checks["redis"] = {"status": "not_checked", "message": "TODO: Implement check"}
    
    # TODO: Check Qdrant connection
    # try:
    #     await qdrant.health_check()
    #     checks["qdrant"] = {"status": "healthy", "latency_ms": 0}
    # except Exception as e:
    #     checks["qdrant"] = {"status": "unhealthy", "error": str(e)}
    #     overall_status = "not_ready"
    #     status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    
    checks["qdrant"] = {"status": "not_checked", "message": "TODO: Implement check"}
    
    # Log readiness check
    logger.info(
        "readiness_check_completed",
        overall_status=overall_status,
        checks=checks,
    )
    
    return JSONResponse(
        status_code=status_code,
        content={
            "status": overall_status,
            "version": settings.APP_VERSION,
            "checks": checks,
        },
    )
