"""
UniML — PyTorch Handler

Handles .pt and .pth files.  PyTorch is an optional dependency;
the handler degrades gracefully when torch is not installed.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from loguru import logger


class PyTorchHandler:
    """Strategy handler for PyTorch models."""

    @property
    def framework_name(self) -> str:
        return "PyTorch"

    # ── Availability ─────────────────────────────────────────────

    def is_available(self) -> bool:
        try:
            import torch  # noqa: F401
            return True
        except ImportError:
            return False

    # ── Detection ────────────────────────────────────────────────

    def can_handle(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in (".pt", ".pth")

    def detect_confidence(self, file_path: Path) -> float:
        ext = file_path.suffix.lower()
        if ext not in (".pt", ".pth"):
            return 0.0

        if not self.is_available():
            # Extension matches, but we can't verify contents
            return 0.6

        try:
            import torch
            # Attempt to load — if it succeeds, high confidence
            torch.load(file_path, map_location="cpu", weights_only=False)
            return 0.95
        except Exception:
            return 0.3

    # ── Loading ──────────────────────────────────────────────────

    def load_model(self, file_path: Path) -> Any:
        import torch
        model = torch.load(file_path, map_location="cpu", weights_only=False)
        logger.debug("Loaded PyTorch model from {}", file_path)
        return model

    # ── Info ─────────────────────────────────────────────────────

    def get_model_info(self, file_path: Path) -> dict[str, Any]:
        import torch

        info: dict[str, Any] = {
            "framework": "pytorch",
            "file_size_bytes": file_path.stat().st_size,
        }

        try:
            model = self.load_model(file_path)

            if isinstance(model, torch.nn.Module):
                info["model_class"] = model.__class__.__name__
                total_params = sum(p.numel() for p in model.parameters())
                info["parameters"] = total_params
                info["trainable_parameters"] = sum(
                    p.numel() for p in model.parameters() if p.requires_grad
                )
                # Try to infer shapes from first layer
                info["is_module"] = True
            elif isinstance(model, dict):
                info["model_class"] = "state_dict"
                info["keys"] = list(model.keys())[:10]
                info["is_module"] = False
            else:
                info["model_class"] = type(model).__name__
                info["is_module"] = False

        except Exception as exc:
            logger.warning("Could not extract PyTorch model info: {}", exc)
            info["error"] = str(exc)

        return info

    # ── Validation ───────────────────────────────────────────────

    def validate(self, file_path: Path) -> dict[str, Any]:
        issues: list[dict[str, str]] = []
        is_valid = True

        if not file_path.exists():
            return {"is_valid": False, "issues": [
                {"severity": "critical", "code": "FILE_MISSING", "message": "File does not exist"}
            ]}

        if not self.is_available():
            return {"is_valid": True, "issues": [
                {"severity": "warning", "code": "TORCH_NOT_INSTALLED",
                 "message": "PyTorch is not installed — cannot fully validate"}
            ]}

        try:
            import torch
            model = torch.load(file_path, map_location="cpu", weights_only=False)

            if isinstance(model, torch.nn.Module):
                issues.append({
                    "severity": "info", "code": "MODULE_LOADED",
                    "message": f"Successfully loaded nn.Module: {model.__class__.__name__}"
                })
            elif isinstance(model, dict):
                issues.append({
                    "severity": "info", "code": "STATE_DICT_LOADED",
                    "message": "Loaded state dict — ONNX conversion requires a full module"
                })
                issues.append({
                    "severity": "warning", "code": "STATE_DICT_ONLY",
                    "message": "State dicts cannot be directly converted to ONNX without the model class"
                })
            else:
                issues.append({
                    "severity": "info", "code": "OBJECT_LOADED",
                    "message": f"Loaded object of type: {type(model).__name__}"
                })

        except Exception as exc:
            is_valid = False
            issues.append({
                "severity": "critical", "code": "LOAD_FAILED",
                "message": f"Failed to load model: {exc}"
            })

        return {"is_valid": is_valid, "issues": issues}

    # ── ONNX Conversion ─────────────────────────────────────────

    def convert_to_onnx(self, file_path: Path, output_path: Path) -> bool:
        import torch

        model = torch.load(file_path, map_location="cpu", weights_only=False)

        if not isinstance(model, torch.nn.Module):
            raise TypeError(
                "Only nn.Module instances can be converted to ONNX. "
                "State dicts require the model class definition."
            )

        model.eval()

        # Try to infer a dummy input shape from the first parameter
        first_param = next(model.parameters(), None)
        if first_param is not None:
            in_features = first_param.shape[-1]
            dummy_input = torch.randn(1, in_features)
        else:
            # Fallback: 1×3×224×224 (common for vision models)
            dummy_input = torch.randn(1, 3, 224, 224)

        torch.onnx.export(
            model,
            dummy_input,
            str(output_path),
            export_params=True,
            opset_version=17,
            do_constant_folding=True,
            input_names=["input"],
            output_names=["output"],
            dynamic_axes={
                "input": {0: "batch_size"},
                "output": {0: "batch_size"},
            },
        )

        logger.info("Converted PyTorch model to ONNX: {}", output_path)
        return True
