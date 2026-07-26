"""
UniML — Pydantic Schemas

All request / response models for the REST API and internal data transfer.
Using Pydantic v2 with strict validation.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator

from models.enums import (
    ConversionStatus,
    MLFramework,
    ModelStatus,
    ValidationSeverity,
)


# ── Helpers ──────────────────────────────────────────────────────────

def _new_id() -> str:
    """Generate a short unique ID for a model session."""
    return uuid.uuid4().hex[:12]


# ── Upload ───────────────────────────────────────────────────────────

class UploadResponse(BaseModel):
    """Returned after a successful file upload."""
    model_id: str = Field(default_factory=_new_id, description="Unique model session ID")
    filename: str
    file_size_bytes: int
    file_size_human: str
    upload_time: datetime = Field(default_factory=datetime.utcnow)
    file_path: str
    status: ModelStatus = ModelStatus.UPLOADED


# ── Detection ────────────────────────────────────────────────────────

class DetectionResult(BaseModel):
    """Result of the framework auto-detection step."""
    model_id: str
    framework: MLFramework
    confidence: float = Field(ge=0.0, le=1.0, description="Detection confidence 0–1")
    details: str = ""
    status: ModelStatus = ModelStatus.DETECTED


# ── Validation ───────────────────────────────────────────────────────

class ValidationIssue(BaseModel):
    """A single validation finding."""
    severity: ValidationSeverity
    code: str
    message: str


class ValidationReport(BaseModel):
    """Full validation report for an uploaded model."""
    model_id: str
    framework: MLFramework
    is_valid: bool
    issues: list[ValidationIssue] = Field(default_factory=list)
    input_shape: Optional[list[int | str]] = None
    output_shape: Optional[list[int | str]] = None
    model_class: Optional[str] = None
    parameters: Optional[int] = None
    status: ModelStatus = ModelStatus.VALIDATED


# ── Conversion ───────────────────────────────────────────────────────

class ConversionResult(BaseModel):
    """Outcome of an ONNX conversion."""
    model_id: str
    conversion_status: ConversionStatus
    original_format: MLFramework
    onnx_path: Optional[str] = None
    onnx_size_bytes: Optional[int] = None
    onnx_size_human: Optional[str] = None
    error_message: Optional[str] = None
    status: ModelStatus = ModelStatus.CONVERTED


# ── Benchmark ────────────────────────────────────────────────────────

class BenchmarkResult(BaseModel):
    """Performance benchmark numbers for a model."""
    model_id: str
    framework: MLFramework
    inference_time_ms: Optional[float] = None
    memory_usage_mb: Optional[float] = None
    model_size_mb: float
    onnx_size_mb: Optional[float] = None
    input_shape: Optional[list[int | str]] = None
    output_shape: Optional[list[int | str]] = None
    status: ModelStatus = ModelStatus.BENCHMARKED


# ── Generation ───────────────────────────────────────────────────────

class GenerationRequest(BaseModel):
    """User-configurable options for code generation."""
    model_id: str
    project_name: str = "ml_inference_server"
    host: str = "0.0.0.0"
    port: int = 8080
    include_docker: bool = True
    include_readme: bool = True


class GenerationResult(BaseModel):
    """Result of the code-generation + packaging step."""
    model_id: str
    project_name: str
    zip_path: str
    zip_size_bytes: int
    zip_size_human: str
    files_generated: list[str]
    status: ModelStatus = ModelStatus.READY



# ── Errors ───────────────────────────────────────────────────────────

class ErrorResponse(BaseModel):
    """Standard error envelope returned by all exception handlers."""
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None


# ── Health ───────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    """Health-check response."""
    status: str = "healthy"
    version: str
    uptime_seconds: float


class PlatformInfo(BaseModel):
    """Platform metadata returned by GET /info."""
    name: str = "UniML"
    version: str
    python_version: str
    supported_frameworks: list[str]
    supported_extensions: list[str]
    max_upload_size_mb: int


