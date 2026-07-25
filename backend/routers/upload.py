"""
UniML — Upload Router

Handles file upload, basic validation, and framework detection trigger.
"""

from __future__ import annotations

from fastapi import APIRouter, File, UploadFile, HTTPException
from loguru import logger

from backend.config import get_settings
from backend.utils.file_utils import (
    format_file_size,
    save_upload,
    validate_extension,
)
from models.schemas import UploadResponse

router = APIRouter(prefix="/api/v1", tags=["Upload"])


@router.post("/upload", response_model=UploadResponse)
async def upload_model(file: UploadFile = File(...)) -> UploadResponse:
    """
    Upload a machine-learning model file.

    Validates:
    - File is not empty
    - Extension is in the allow-list
    - File size does not exceed the configured maximum
    """
    settings = get_settings()

    # ── Validate filename ────────────────────────────────────────
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    if not validate_extension(file.filename):
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type. Allowed: {', '.join(settings.allowed_extensions)}"
        )

    # ── Read and validate size ───────────────────────────────────
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    if len(content) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds maximum size of {settings.max_upload_size_mb} MB"
        )

    # ── Save to disk ─────────────────────────────────────────────
    saved_path = await save_upload(content, file.filename)

    logger.info(
        "Model uploaded: {} ({}) → {}",
        file.filename,
        format_file_size(len(content)),
        saved_path,
    )

    return UploadResponse(
        filename=file.filename,
        file_size_bytes=len(content),
        file_size_human=format_file_size(len(content)),
        file_path=str(saved_path),
    )
