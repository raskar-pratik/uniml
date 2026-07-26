"""
UniML — Enumerations

Defines all enums used across the application.
Centralised here so every module shares the same vocabulary.
"""

from enum import Enum


class MLFramework(str, Enum):
    """Supported machine-learning frameworks."""
    PYTORCH = "pytorch"
    TENSORFLOW = "tensorflow"
    SKLEARN = "sklearn"
    ONNX = "onnx"
    UNKNOWN = "unknown"


class ModelStatus(str, Enum):
    """Lifecycle status of a model within the pipeline."""
    UPLOADED = "uploaded"
    DETECTED = "detected"
    VALIDATED = "validated"
    CONVERTING = "converting"
    CONVERTED = "converted"
    BENCHMARKED = "benchmarked"
    GENERATING = "generating"

    READY = "ready"
    FAILED = "failed"


class ConversionStatus(str, Enum):
    """Outcome of an ONNX conversion attempt."""
    SUCCESS = "success"
    SKIPPED = "skipped"        # Already ONNX
    FAILED = "failed"
    UNSUPPORTED = "unsupported"


class ValidationSeverity(str, Enum):
    """Severity levels for validation issues."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
