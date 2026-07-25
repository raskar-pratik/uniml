"""
UniML — Converter Handlers Package

Each handler implements a common protocol for a specific ML framework.
The handler registry auto-discovers all handlers in this package.
"""

from pathlib import Path

from converter.handlers.base import FrameworkHandler
from converter.handlers.pytorch_handler import PyTorchHandler
from converter.handlers.tensorflow_handler import TensorFlowHandler
from converter.handlers.sklearn_handler import SklearnHandler
from converter.handlers.onnx_handler import OnnxHandler

# Handler registry — ordered by detection priority
ALL_HANDLERS: list[FrameworkHandler] = [
    OnnxHandler(),
    PyTorchHandler(),
    TensorFlowHandler(),
    SklearnHandler(),
]


def find_handler(file_path: Path) -> FrameworkHandler | None:
    """Find the first handler that can handle this file."""
    for handler in ALL_HANDLERS:
        if handler.can_handle(file_path):
            return handler
    return None


__all__ = ["ALL_HANDLERS", "FrameworkHandler", "find_handler"]
