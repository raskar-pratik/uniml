"""
UniML — Scikit-Learn Handler

Handles .pkl and .joblib files.  Scikit-learn is a core dependency
and is always available.
"""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any

import joblib
import numpy as np
from loguru import logger


class SklearnHandler:
    """Strategy handler for scikit-learn models."""

    @property
    def framework_name(self) -> str:
        return "Scikit-Learn"

    # ── Availability ─────────────────────────────────────────────

    def is_available(self) -> bool:
        try:
            import sklearn  # noqa: F401
            return True
        except ImportError:
            return False

    # ── Detection ────────────────────────────────────────────────

    def can_handle(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in (".pkl", ".joblib")

    def detect_confidence(self, file_path: Path) -> float:
        ext = file_path.suffix.lower()
        if ext not in (".pkl", ".joblib"):
            return 0.0

        try:
            model = self._load(file_path)

            # Check if it's a scikit-learn estimator
            if hasattr(model, "predict") and hasattr(model, "fit"):
                return 0.95
            if hasattr(model, "transform"):
                return 0.85
            # It's a valid pickle/joblib but not sklearn
            return 0.4

        except Exception:
            return 0.2

    # ── Loading ──────────────────────────────────────────────────

    def _load(self, file_path: Path) -> Any:
        """Load using joblib or pickle depending on extension."""
        ext = file_path.suffix.lower()
        if ext == ".joblib":
            return joblib.load(str(file_path))
        else:
            with open(file_path, "rb") as f:
                return pickle.load(f)  # noqa: S301

    def load_model(self, file_path: Path) -> Any:
        model = self._load(file_path)
        logger.debug("Loaded sklearn model from {}", file_path)
        return model

    # ── Info ─────────────────────────────────────────────────────

    def get_model_info(self, file_path: Path) -> dict[str, Any]:
        info: dict[str, Any] = {
            "framework": "sklearn",
            "file_size_bytes": file_path.stat().st_size,
        }

        try:
            model = self.load_model(file_path)
            info["model_class"] = type(model).__name__

            # Number of features
            if hasattr(model, "n_features_in_"):
                info["input_shape"] = [model.n_features_in_]
            if hasattr(model, "n_classes_"):
                n = model.n_classes_
                info["output_shape"] = [int(n) if isinstance(n, (int, np.integer)) else len(n)]
            elif hasattr(model, "coef_"):
                info["output_shape"] = list(np.array(model.coef_).shape)

            # Model params
            if hasattr(model, "get_params"):
                info["hyperparameters"] = model.get_params()

        except Exception as exc:
            logger.warning("Could not extract sklearn model info: {}", exc)
            info["error"] = str(exc)

        return info

    # ── Validation ───────────────────────────────────────────────

    def validate(self, file_path: Path) -> dict[str, Any]:
        issues: list[dict[str, str]] = []

        if not file_path.exists():
            return {"is_valid": False, "issues": [
                {"severity": "critical", "code": "FILE_MISSING", "message": "File does not exist"}
            ]}

        try:
            model = self.load_model(file_path)

            if hasattr(model, "predict"):
                issues.append({
                    "severity": "info", "code": "MODEL_LOADED",
                    "message": f"Successfully loaded estimator: {type(model).__name__}"
                })
            else:
                issues.append({
                    "severity": "warning", "code": "NOT_ESTIMATOR",
                    "message": f"Loaded object ({type(model).__name__}) does not have a predict method"
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
        from skl2onnx import convert_sklearn
        from skl2onnx.common.data_types import FloatTensorType

        model = self.load_model(file_path)

        if not hasattr(model, "predict"):
            raise TypeError(f"Object of type {type(model).__name__} is not a sklearn estimator")

        # Determine input dimension
        n_features = getattr(model, "n_features_in_", None)
        if n_features is None:
            raise ValueError(
                "Cannot determine input shape. The model does not have `n_features_in_`. "
                "Ensure the model was fitted before saving."
            )

        initial_type = [("input", FloatTensorType([None, n_features]))]
        onnx_model = convert_sklearn(model, initial_types=initial_type)

        with open(output_path, "wb") as f:
            f.write(onnx_model.SerializeToString())

        logger.info("Converted sklearn model to ONNX: {}", output_path)
        return True
