"""
UniML — ONNX Converter

Orchestrates the conversion of any supported model to ONNX format.
Delegates the actual conversion to the appropriate framework handler.
"""

from __future__ import annotations

from pathlib import Path

from loguru import logger

from backend.config import get_settings
from backend.utils.file_utils import format_file_size
from converter.detector import detect_framework
from converter.handlers import find_handler
from models.enums import ConversionStatus, MLFramework
from models.schemas import ConversionResult


def convert_to_onnx(file_path: Path, model_id: str = "") -> ConversionResult:
    """
    Convert a model file to ONNX format.

    - If the model is already ONNX, copies it and returns SKIPPED.
    - If the framework handler supports conversion, runs it.
    - Returns FAILED or UNSUPPORTED on error or missing support.
    """
    settings = get_settings()
    detection = detect_framework(file_path)
    framework = detection.framework

    # ── Already ONNX ─────────────────────────────────────────────
    if framework == MLFramework.ONNX:
        logger.info("Model is already ONNX — skipping conversion")
        return ConversionResult(
            model_id=model_id,
            conversion_status=ConversionStatus.SKIPPED,
            original_format=framework,
            onnx_path=str(file_path),
            onnx_size_bytes=file_path.stat().st_size,
            onnx_size_human=format_file_size(file_path.stat().st_size),
        )

    # ── Find handler ─────────────────────────────────────────────
    handler = find_handler(file_path)

    if handler is None:
        logger.warning("No handler found for {}", file_path.name)
        return ConversionResult(
            model_id=model_id,
            conversion_status=ConversionStatus.UNSUPPORTED,
            original_format=framework,
            error_message="No handler available for this file format",
        )

    if not handler.is_available():
        logger.warning("{} library not installed", handler.framework_name)
        return ConversionResult(
            model_id=model_id,
            conversion_status=ConversionStatus.UNSUPPORTED,
            original_format=framework,
            error_message=f"{handler.framework_name} library is not installed",
        )

    # ── Run conversion ───────────────────────────────────────────
    output_dir = settings.generated_dir / (model_id or file_path.stem)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{file_path.stem}.onnx"

    try:
        handler.convert_to_onnx(file_path, output_path)

        if not output_path.exists():
            raise FileNotFoundError(f"ONNX output not created at {output_path}")

        onnx_size = output_path.stat().st_size
        logger.info(
            "✅ Conversion successful: {} → {} ({})",
            file_path.name, output_path.name, format_file_size(onnx_size),
        )

        return ConversionResult(
            model_id=model_id,
            conversion_status=ConversionStatus.SUCCESS,
            original_format=framework,
            onnx_path=str(output_path),
            onnx_size_bytes=onnx_size,
            onnx_size_human=format_file_size(onnx_size),
        )

    except Exception as exc:
        logger.error("❌ Conversion failed: {}", exc)
        return ConversionResult(
            model_id=model_id,
            conversion_status=ConversionStatus.FAILED,
            original_format=framework,
            error_message=str(exc),
        )
