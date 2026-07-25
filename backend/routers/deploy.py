"""
UniML — Deploy Router

Endpoints for generating the deployment package (FastAPI server,
Docker config, ZIP archive) and downloading it.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from loguru import logger

from backend.security import require_api_key
from models.schemas import GenerationRequest, GenerationResult

router = APIRouter(prefix="/api/v1", tags=["Deployment"])


@router.post(
    "/generate",
    response_model=GenerationResult,
    dependencies=[Depends(require_api_key)],
)
async def generate_package(req: GenerationRequest) -> GenerationResult:
    """
    Generate a full deployment package:
    1. FastAPI inference server code
    2. Docker configuration
    3. ZIP archive of everything
    """
    from backend.services.pipeline import generate_deployment_package

    result = generate_deployment_package(req)
    logger.info(
        "Generated deployment package: {} ({} files)",
        req.project_name,
        len(result.files_generated),
    )
    return result


@router.get("/download/{model_id}")
async def download_package(model_id: str):
    """Download the generated ZIP package for a given model ID."""
    from backend.config import get_settings

    settings = get_settings()

    # Look for any ZIP file in the model's generated directory
    gen_dir = settings.generated_dir / model_id
    if not gen_dir.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Deployment package for {model_id} not found. Generate it first."
        )

    zip_files = list(gen_dir.glob("*.zip"))
    if not zip_files:
        raise HTTPException(
            status_code=404,
            detail="ZIP file not found in generated directory",
        )

    zip_path = zip_files[0]
    logger.info("Serving download: {}", zip_path)

    return FileResponse(
        path=str(zip_path),
        media_type="application/zip",
        filename=zip_path.name,
    )
