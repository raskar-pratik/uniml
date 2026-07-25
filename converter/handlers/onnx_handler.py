"""
UniML — ONNX Handler

Handles .onnx files.  ONNX is a core dependency.
Models that are already ONNX skip the conversion step.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import onnx
from loguru import logger


class OnnxHandler:
    """Strategy handler for ONNX models."""

    @property
    def framework_name(self) -> str:
        return "ONNX"

    # ── Availability ─────────────────────────────────────────────

    def is_available(self) -> bool:
        return True  # onnx is a core dependency

    # ── Detection ────────────────────────────────────────────────

    def can_handle(self, file_path: Path) -> bool:
        return file_path.suffix.lower() == ".onnx"

    def detect_confidence(self, file_path: Path) -> float:
        if file_path.suffix.lower() != ".onnx":
            return 0.0

        try:
            onnx.load(str(file_path))
            return 1.0
        except Exception:
            return 0.3

    # ── Loading ──────────────────────────────────────────────────

    def load_model(self, file_path: Path) -> Any:
        model = onnx.load(str(file_path))
        logger.debug("Loaded ONNX model from {}", file_path)
        return model

    # ── Info ─────────────────────────────────────────────────────

    def get_model_info(self, file_path: Path) -> dict[str, Any]:
        info: dict[str, Any] = {
            "framework": "onnx",
            "file_size_bytes": file_path.stat().st_size,
        }

        try:
            model = onnx.load(str(file_path))
            info["model_class"] = "ONNX Model"
            info["ir_version"] = model.ir_version
            info["opset_version"] = model.opset_import[0].version if model.opset_import else None
            info["producer"] = model.producer_name or "unknown"

            # Extract input/output shapes
            graph = model.graph
            if graph.input:
                inp = graph.input[0]
                shape = []
                for dim in inp.type.tensor_type.shape.dim:
                    shape.append(dim.dim_value if dim.dim_value > 0 else "dynamic")
                info["input_shape"] = shape
                info["input_name"] = inp.name

            if graph.output:
                out = graph.output[0]
                shape = []
                for dim in out.type.tensor_type.shape.dim:
                    shape.append(dim.dim_value if dim.dim_value > 0 else "dynamic")
                info["output_shape"] = shape
                info["output_name"] = out.name

            info["nodes"] = len(graph.node)

        except Exception as exc:
            logger.warning("Could not extract ONNX model info: {}", exc)
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
            model = onnx.load(str(file_path))
            onnx.checker.check_model(model)
            issues.append({
                "severity": "info", "code": "ONNX_VALID",
                "message": "ONNX model passed all validation checks"
            })
            return {"is_valid": True, "issues": issues}

        except onnx.checker.ValidationError as exc:
            issues.append({
                "severity": "critical", "code": "ONNX_INVALID",
                "message": f"ONNX validation failed: {exc}"
            })
            return {"is_valid": False, "issues": issues}

        except Exception as exc:
            issues.append({
                "severity": "critical", "code": "LOAD_FAILED",
                "message": f"Failed to load ONNX model: {exc}"
            })
            return {"is_valid": False, "issues": issues}

    # ── ONNX Conversion (no-op) ──────────────────────────────────

    def convert_to_onnx(self, file_path: Path, output_path: Path) -> bool:
        """Already ONNX — just copy the file if paths differ."""
        import shutil

        if file_path.resolve() != output_path.resolve():
            shutil.copy2(str(file_path), str(output_path))
            logger.info("Copied ONNX model to {}", output_path)

        return True
