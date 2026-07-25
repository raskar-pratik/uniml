"""
UniML — Convert Router

Endpoints for framework detection, model validation, ONNX conversion,
and benchmarking. Each step can be called independently or via the
full pipeline. All ML operations run in a threadpool to prevent
blocking the main event loop.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool
from loguru import logger
from pydantic import BaseModel

from backend.config import get_settings
from backend.utils.file_utils import resolve_managed_path

router = APIRouter(prefix="/api/v1", tags=["Conversion"])


class DetectRequest(BaseModel):
    file_path: str


class ValidateRequest(BaseModel):
    file_path: str


class ConvertRequest(BaseModel):
    file_path: str
    model_id: str = ""


class BenchmarkRequest(BaseModel):
    file_path: str
    model_id: str = ""


def get_model_path(file_path: str) -> Path:
    """
    Validate a client-supplied model path and return a safe Path object.

    Enforces that the path resolves inside the server's managed directories
    before touching the filesystem, then checks that it exists and is a file.
    """
    try:
        path = resolve_managed_path(file_path)
    except PermissionError:
        # Do not echo the attempted path back to the client.
        raise HTTPException(
            status_code=403,
            detail="Access to the requested path is not allowed.",
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid file path.")

    if not path.exists():
        raise HTTPException(status_code=404, detail="Model file not found.")
    if not path.is_file():
        raise HTTPException(status_code=400, detail="Path is not a file.")
    return path


# ── Detection ────────────────────────────────────────────────────────

@router.post("/detect")
async def detect_framework(req: DetectRequest):
    """Detect the ML framework of an uploaded model."""
    from converter.detector import detect_framework as _detect

    path = get_model_path(req.file_path)

    result = await run_in_threadpool(_detect, path)
    logger.info("Detected framework: {} for {}", result.framework, path.name)
    return result


# ── Validation ───────────────────────────────────────────────────────

@router.post("/validate")
async def validate_model(req: ValidateRequest):
    """Validate an uploaded model file."""
    from validator.validator import validate_model as _validate

    path = get_model_path(req.file_path)

    result = await run_in_threadpool(_validate, path)
    logger.info("Validation result: valid={} for {}", result.is_valid, path.name)
    return result


# ── Conversion ───────────────────────────────────────────────────────

@router.post("/convert")
async def convert_model(req: ConvertRequest):
    """Convert a model to ONNX format."""
    from converter.onnx_converter import convert_to_onnx

    path = get_model_path(req.file_path)

    result = await run_in_threadpool(convert_to_onnx, path, req.model_id)

    # Optional cleanup of the raw upload after a successful conversion.
    # Disabled by default (UNIML_DELETE_RAW_AFTER_CONVERT) because deleting the
    # original file breaks later steps such as /benchmark and re-validation,
    # which still operate on the raw upload path.
    settings = get_settings()
    if (
        settings.delete_raw_after_convert
        and result.conversion_status.name in ("SUCCESS", "SKIPPED")
        and path.exists()
        and path.suffix != ".onnx"
    ):
        try:
            path.unlink()
            logger.info("Cleaned up raw upload file: {}", path.name)
        except OSError as e:
            logger.error("Failed to clean up {}: {}", path.name, e)

    logger.info("Conversion result: {} for {}", result.conversion_status, path.name)
    return result


# ── Benchmark ────────────────────────────────────────────────────────

@router.post("/benchmark")
async def benchmark_model(req: BenchmarkRequest):
    """Benchmark a model's performance."""
    from converter.benchmark import benchmark_model as _benchmark

    path = get_model_path(req.file_path)

    result = await run_in_threadpool(_benchmark, path, req.model_id)
    logger.info("Benchmark complete for {}", path.name)
    return result
