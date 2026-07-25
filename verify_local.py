"""Local (no Docker) end-to-end conversion check.

Replicates the deployment image's runtime: TF_USE_LEGACY_KERAS=1 (with tf-keras
installed --no-deps) so tf2onnx sees the Keras 2 API. Drives the real API via
FastAPI's TestClient: /upload -> /convert for a real PyTorch .pt and a real
TensorFlow .h5. Writes _local_result.json and prints the outcome.
"""
import os

# Must be set before TensorFlow is imported anywhere.
os.environ["TF_USE_LEGACY_KERAS"] = "1"

import json
import tempfile
from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)
tmp = Path(tempfile.mkdtemp())
result = {}


def drive(path: Path, filename: str) -> dict:
    with open(path, "rb") as f:
        up = client.post(
            "/api/v1/upload",
            files={"file": (filename, f, "application/octet-stream")},
        )
    if up.status_code != 200:
        return {"stage": "upload", "http": up.status_code, "body": up.text[:300]}
    uj = up.json()
    conv = client.post(
        "/api/v1/convert",
        json={"file_path": uj["file_path"], "model_id": uj["model_id"]},
    )
    try:
        cj = conv.json()
    except Exception:
        return {"stage": "convert", "http": conv.status_code, "raw": conv.text[:300]}
    return {
        "http": conv.status_code,
        "conversion_status": cj.get("conversion_status"),
        "original_format": cj.get("original_format"),
        "onnx_size_human": cj.get("onnx_size_human"),
        "error_message": cj.get("error_message") or cj.get("detail"),
    }


import platform

result["python"] = platform.python_version()

# Real PyTorch model.
try:
    import torch
    import torch.nn as nn

    pt_path = tmp / "model.pt"
    torch.save(nn.Sequential(nn.Linear(4, 8), nn.ReLU(), nn.Linear(8, 3)), pt_path)
    result["pytorch"] = drive(pt_path, "model.pt")
except ImportError as exc:
    result["pytorch"] = {"conversion_status": None, "error_message": f"library unavailable: {exc}"}

# Real Keras model (Keras 2 API via tf-keras + TF_USE_LEGACY_KERAS).
try:
    import tensorflow as tf

    h5_path = tmp / "model.h5"
    tf.keras.Sequential([
        tf.keras.layers.Input((4,)),
        tf.keras.layers.Dense(8, activation="relu"),
        tf.keras.layers.Dense(3),
    ]).save(str(h5_path))
    result["tensorflow"] = drive(h5_path, "model.h5")
except ImportError as exc:
    result["tensorflow"] = {"conversion_status": None, "error_message": f"library unavailable: {exc}"}

Path("_local_result.json").write_text(json.dumps(result, indent=2))
print("RESULT " + json.dumps(result))
