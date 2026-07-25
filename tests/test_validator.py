"""
UniML — Validator Tests

Tests for the model validation engine.
"""

from pathlib import Path

import pytest


class TestModelValidation:
    """Test suite for model validation."""

    def test_validate_sklearn_model(self, sklearn_model_path):
        """Should validate a valid sklearn model."""
        from validator.validator import validate_model

        result = validate_model(sklearn_model_path)
        assert result.is_valid is True
        assert result.framework.value == "sklearn"

    def test_validate_onnx_model(self, onnx_model_path):
        """Should validate a valid ONNX model."""
        from validator.validator import validate_model

        result = validate_model(onnx_model_path)
        assert result.is_valid is True
        assert result.framework.value == "onnx"

    def test_validate_missing_file(self, tmp_path):
        """Should fail validation for missing files."""
        from validator.validator import validate_model

        result = validate_model(tmp_path / "nonexistent.pkl")
        assert result.is_valid is False
        assert any(i.code == "FILE_MISSING" for i in result.issues)

    def test_validate_empty_file(self, empty_file):
        """Should fail validation for empty files."""
        from validator.validator import validate_model

        result = validate_model(empty_file)
        assert result.is_valid is False

    def test_validation_report_structure(self, sklearn_model_path):
        """Validation report should have the expected structure."""
        from validator.validator import validate_model
        from models.schemas import ValidationReport

        result = validate_model(sklearn_model_path)
        assert isinstance(result, ValidationReport)
        assert hasattr(result, "is_valid")
        assert hasattr(result, "framework")
        assert hasattr(result, "issues")
        assert isinstance(result.issues, list)

    def test_validate_extracts_model_info(self, sklearn_model_path):
        """Should extract model class and input shape for sklearn."""
        from validator.validator import validate_model

        result = validate_model(sklearn_model_path)
        assert result.model_class is not None
        assert result.input_shape is not None
