"""
UniML — Detector Tests

Tests for the framework auto-detection engine.
"""

from pathlib import Path

import pytest


class TestFrameworkDetection:
    """Test suite for framework detection."""

    def test_detect_sklearn_pkl(self, sklearn_model_path):
        """Should detect a .pkl file as sklearn."""
        from converter.detector import detect_framework
        from models.enums import MLFramework

        result = detect_framework(sklearn_model_path)
        assert result.framework == MLFramework.SKLEARN
        assert result.confidence > 0.5

    def test_detect_sklearn_joblib(self, sklearn_joblib_path):
        """Should detect a .joblib file as sklearn."""
        from converter.detector import detect_framework
        from models.enums import MLFramework

        result = detect_framework(sklearn_joblib_path)
        assert result.framework == MLFramework.SKLEARN
        assert result.confidence > 0.5

    def test_detect_onnx(self, onnx_model_path):
        """Should detect an .onnx file as ONNX."""
        from converter.detector import detect_framework
        from models.enums import MLFramework

        result = detect_framework(onnx_model_path)
        assert result.framework == MLFramework.ONNX
        assert result.confidence >= 0.9

    def test_detect_unknown_extension(self, tmp_path):
        """Should return UNKNOWN for unsupported extensions."""
        from converter.detector import detect_framework
        from models.enums import MLFramework

        path = tmp_path / "model.xyz"
        path.write_text("some data")

        result = detect_framework(path)
        assert result.framework == MLFramework.UNKNOWN

    def test_detect_returns_detection_result(self, sklearn_model_path):
        """Detection result should have required fields."""
        from converter.detector import detect_framework
        from models.schemas import DetectionResult

        result = detect_framework(sklearn_model_path)
        assert isinstance(result, DetectionResult)
        assert hasattr(result, "framework")
        assert hasattr(result, "confidence")
        assert 0.0 <= result.confidence <= 1.0
