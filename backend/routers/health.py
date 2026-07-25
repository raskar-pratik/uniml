"""
UniML — Health Router

Exposes health-check and platform info endpoints.
These are un-prefixed (not under /api/v1) for simplicity.
"""

from __future__ import annotations

import sys
import time

from fastapi import APIRouter

from backend.config import get_settings
from models.enums import MLFramework
from models.schemas import HealthResponse, PlatformInfo

router = APIRouter(tags=["Health"])

_start_time = time.time()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Lightweight health probe."""
    settings = get_settings()
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        uptime_seconds=round(time.time() - _start_time, 2),
    )


@router.get("/info", response_model=PlatformInfo)
async def platform_info() -> PlatformInfo:
    """Return platform metadata and capabilities."""
    settings = get_settings()
    return PlatformInfo(
        name=settings.app_name,
        version=settings.app_version,
        python_version=sys.version.split()[0],
        supported_frameworks=[fw.value for fw in MLFramework if fw != MLFramework.UNKNOWN],
        supported_extensions=settings.allowed_extensions,
        max_upload_size_mb=settings.max_upload_size_mb,
    )
