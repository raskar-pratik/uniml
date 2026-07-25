"""
UniML — Base Framework Handler

Defines the Protocol (interface) that every framework handler must implement.
Uses Python's Protocol for structural subtyping (duck-typing with type safety).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class FrameworkHandler(Protocol):
    """
    Contract for ML framework handlers.

    Each handler knows how to:
    - Detect if a file belongs to its framework
    - Load and validate the model
    - Extract metadata (shapes, parameters)
    - Convert to ONNX
    - Run basic benchmarks
    """

    @property
    def framework_name(self) -> str:
        """Human-readable framework name."""
        ...

    def can_handle(self, file_path: Path) -> bool:
        """
        Return True if this handler can process the given file.
        Should be fast — typically checks extension and/or magic bytes.
        """
        ...

    def detect_confidence(self, file_path: Path) -> float:
        """
        Return a confidence score (0.0–1.0) that this file belongs
        to this handler's framework.
        """
        ...

    def load_model(self, file_path: Path) -> Any:
        """Load the model from disk and return it."""
        ...

    def get_model_info(self, file_path: Path) -> dict[str, Any]:
        """
        Return metadata about the model:
        - input_shape, output_shape
        - model_class, parameters
        - framework-specific details
        """
        ...

    def validate(self, file_path: Path) -> dict[str, Any]:
        """
        Validate the model and return a dict with:
        - is_valid: bool
        - issues: list of {severity, code, message}
        """
        ...

    def convert_to_onnx(self, file_path: Path, output_path: Path) -> bool:
        """
        Convert the model to ONNX format.
        Returns True on success, raises on failure.
        """
        ...

    def is_available(self) -> bool:
        """
        Check if the required libraries for this handler are installed.
        Allows graceful degradation when optional deps are missing.
        """
        ...
