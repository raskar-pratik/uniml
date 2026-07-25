"""
UniML — Framework Detector

Uses the handler registry to auto-detect which ML framework
produced a given model file.  Returns the best match with confidence.
"""

from __future__ import annotations

from pathlib import Path

from loguru import logger

from converter.handlers import ALL_HANDLERS
from models.enums import MLFramework
from models.schemas import DetectionResult


# Map handler framework names → enum values
_NAME_TO_ENUM: dict[str, MLFramework] = {
    "PyTorch": MLFramework.PYTORCH,
    "TensorFlow": MLFramework.TENSORFLOW,
    "Scikit-Learn": MLFramework.SKLEARN,
    "ONNX": MLFramework.ONNX,
}


def detect_framework(file_path: Path) -> DetectionResult:
    """
    Detect the ML framework by querying each registered handler.

    Returns the handler with the highest confidence score.
    """
    best_handler = None
    best_confidence = 0.0

    for handler in ALL_HANDLERS:
        if not handler.can_handle(file_path):
            continue

        try:
            confidence = handler.detect_confidence(file_path)
            logger.debug(
                "Handler {} confidence={:.2f} for {}",
                handler.framework_name, confidence, file_path.name,
            )
            if confidence > best_confidence:
                best_confidence = confidence
                best_handler = handler
        except Exception as exc:
            logger.warning(
                "Handler {} errored during detection: {}",
                handler.framework_name, exc,
            )

    if best_handler is None:
        logger.warning("No handler matched {}", file_path.name)
        return DetectionResult(
            model_id="",
            framework=MLFramework.UNKNOWN,
            confidence=0.0,
            details="No registered handler could identify this file.",
        )

    framework_enum = _NAME_TO_ENUM.get(best_handler.framework_name, MLFramework.UNKNOWN)
    available_note = "" if best_handler.is_available() else " (library not installed)"

    return DetectionResult(
        model_id="",
        framework=framework_enum,
        confidence=round(best_confidence, 2),
        details=f"Detected as {best_handler.framework_name}{available_note}",
    )
