"""
UniML — Test Fixtures

Shared pytest fixtures for test data, temporary files, and API clients.
"""

import os
import pickle
import sys
import tempfile
from pathlib import Path

import numpy as np
import pytest
from fastapi.testclient import TestClient

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def test_client():
    """Create a FastAPI test client."""
    from backend.main import app
    return TestClient(app)





@pytest.fixture
def sklearn_model_path(tmp_path) -> Path:
    """Create a small sklearn model and save it as a .pkl file."""
    from sklearn.linear_model import LinearRegression

    model = LinearRegression()
    X = np.array([[1, 2], [3, 4], [5, 6], [7, 8]])
    y = np.array([1, 2, 3, 4])
    model.fit(X, y)

    path = tmp_path / "test_model.pkl"
    with open(path, "wb") as f:
        pickle.dump(model, f)

    return path


@pytest.fixture
def sklearn_joblib_path(tmp_path) -> Path:
    """Create a small sklearn model and save it as a .joblib file."""
    import joblib
    from sklearn.ensemble import RandomForestClassifier

    model = RandomForestClassifier(n_estimators=5, random_state=42)
    X = np.array([[1, 2], [3, 4], [5, 6], [7, 8]])
    y = np.array([0, 1, 0, 1])
    model.fit(X, y)

    path = tmp_path / "test_model.joblib"
    joblib.dump(model, str(path))

    return path


@pytest.fixture
def onnx_model_path(tmp_path) -> Path:
    """Create a minimal ONNX model file for testing."""
    import onnx
    from onnx import helper, TensorProto

    # Create a simple ONNX model (identity)
    X = helper.make_tensor_value_info("input", TensorProto.FLOAT, [None, 2])
    Y = helper.make_tensor_value_info("output", TensorProto.FLOAT, [None, 2])

    identity_node = helper.make_node("Identity", ["input"], ["output"])

    graph = helper.make_graph([identity_node], "test_graph", [X], [Y])
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 17)])
    model.ir_version = 8

    path = tmp_path / "test_model.onnx"
    onnx.save(model, str(path))

    return path


@pytest.fixture
def empty_file(tmp_path) -> Path:
    """Create an empty file."""
    path = tmp_path / "empty.pkl"
    path.touch()
    return path


@pytest.fixture
def invalid_file(tmp_path) -> Path:
    """Create a file with invalid content."""
    path = tmp_path / "invalid.pkl"
    path.write_text("this is not a valid pickle file")
    return path
