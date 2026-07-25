"""
UniML — TensorFlow / Keras Handler

Handles .h5 and .keras files.  TensorFlow is an optional dependency;
the handler degrades gracefully when it is not installed.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from loguru import logger


class TensorFlowHandler:
    """Strategy handler for TensorFlow / Keras models."""

    @property
    def framework_name(self) -> str:
        return "TensorFlow"

    # ── Availability ─────────────────────────────────────────────

    def is_available(self) -> bool:
        try:
            import tensorflow  # noqa: F401
            return True
        except ImportError:
            return False

    # ── Detection ────────────────────────────────────────────────

    def can_handle(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in (".h5", ".keras")

    def detect_confidence(self, file_path: Path) -> float:
        ext = file_path.suffix.lower()
        if ext not in (".h5", ".keras"):
            return 0.0

        if not self.is_available():
            return 0.6

        try:
            import tensorflow as tf
            tf.keras.models.load_model(str(file_path), compile=False)
            return 0.95
        except Exception:
            return 0.3

    # ── Loading ──────────────────────────────────────────────────

    def load_model(self, file_path: Path) -> Any:
        import tensorflow as tf
        model = tf.keras.models.load_model(str(file_path), compile=False)
        logger.debug("Loaded TensorFlow model from {}", file_path)
        return model

    # ── Info ─────────────────────────────────────────────────────

    def get_model_info(self, file_path: Path) -> dict[str, Any]:
        info: dict[str, Any] = {
            "framework": "tensorflow",
            "file_size_bytes": file_path.stat().st_size,
        }

        if not self.is_available():
            info["warning"] = "TensorFlow not installed — limited info"
            return info

        try:
            import tensorflow as tf
            model = tf.keras.models.load_model(str(file_path), compile=False)
            info["model_class"] = model.__class__.__name__
            info["parameters"] = model.count_params()

            if model.input_shape:
                info["input_shape"] = list(model.input_shape)
            if model.output_shape:
                info["output_shape"] = list(model.output_shape)

            info["layers"] = len(model.layers)

        except Exception as exc:
            logger.warning("Could not extract TF model info: {}", exc)
            info["error"] = str(exc)

        return info

    # ── Validation ───────────────────────────────────────────────

    def validate(self, file_path: Path) -> dict[str, Any]:
        issues: list[dict[str, str]] = []

        if not file_path.exists():
            return {"is_valid": False, "issues": [
                {"severity": "critical", "code": "FILE_MISSING", "message": "File does not exist"}
            ]}

        if not self.is_available():
            return {"is_valid": True, "issues": [
                {"severity": "warning", "code": "TF_NOT_INSTALLED",
                 "message": "TensorFlow is not installed — cannot fully validate"}
            ]}

        try:
            import tensorflow as tf
            model = tf.keras.models.load_model(str(file_path), compile=False)
            issues.append({
                "severity": "info", "code": "MODEL_LOADED",
                "message": f"Successfully loaded Keras model: {model.__class__.__name__} "
                           f"({model.count_params()} parameters)"
            })
            return {"is_valid": True, "issues": issues}

        except Exception as exc:
            issues.append({
                "severity": "critical", "code": "LOAD_FAILED",
                "message": f"Failed to load model: {exc}"
            })
            return {"is_valid": False, "issues": issues}

    # ── ONNX Conversion ─────────────────────────────────────────

    def convert_to_onnx(self, file_path: Path, output_path: Path) -> bool:
        import tensorflow as tf

        try:
            import tf2onnx
        except ImportError:
            raise ImportError(
                "tf2onnx is required for TensorFlow→ONNX conversion. "
                "Install it with: pip install tf2onnx"
            )

        model = tf.keras.models.load_model(str(file_path), compile=False)

        # Build a concrete function from the Keras model
        input_spec = [tf.TensorSpec(model.input_shape, tf.float32, name="input")]

        # Convert using tf2onnx
        model_proto, _ = tf2onnx.convert.from_keras(
            model,
            input_signature=input_spec,
            opset=17,
            output_path=str(output_path),
        )

        logger.info("Converted TensorFlow model to ONNX: {}", output_path)
        return True
