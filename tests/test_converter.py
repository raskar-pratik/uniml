"""
UniML — Converter Tests

Tests for the ONNX conversion engine.
"""

from pathlib import Path

import pytest


class TestOnnxConversion:
    """Test suite for ONNX conversion."""

    def test_convert_sklearn_to_onnx(self, sklearn_model_path, tmp_path):
        """Should convert a sklearn .pkl model to ONNX."""
        from converter.onnx_converter import convert_to_onnx
        from models.enums import ConversionStatus

        result = convert_to_onnx(sklearn_model_path, model_id="test_sklearn")

        assert result.conversion_status == ConversionStatus.SUCCESS
        assert result.onnx_path is not None
        assert Path(result.onnx_path).exists()
        assert Path(result.onnx_path).suffix == ".onnx"

    def test_onnx_file_skips_conversion(self, onnx_model_path):
        """Should skip conversion for files already in ONNX format."""
        from converter.onnx_converter import convert_to_onnx
        from models.enums import ConversionStatus

        result = convert_to_onnx(onnx_model_path, model_id="test_onnx")

        assert result.conversion_status == ConversionStatus.SKIPPED
        assert result.onnx_path is not None

    def test_conversion_result_structure(self, sklearn_model_path):
        """Conversion result should have the expected fields."""
        from converter.onnx_converter import convert_to_onnx
        from models.schemas import ConversionResult

        result = convert_to_onnx(sklearn_model_path, model_id="test_struct")

        assert isinstance(result, ConversionResult)
        assert hasattr(result, "conversion_status")
        assert hasattr(result, "original_format")
        assert hasattr(result, "onnx_path")

    def test_converted_onnx_is_valid(self, sklearn_model_path):
        """The converted ONNX file should pass ONNX validation."""
        import onnx
        from converter.onnx_converter import convert_to_onnx

        result = convert_to_onnx(sklearn_model_path, model_id="test_valid")
        assert result.onnx_path is not None

        model = onnx.load(result.onnx_path)
        onnx.checker.check_model(model)
