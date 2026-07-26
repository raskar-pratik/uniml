"""In-container end-to-end conversion check (driven in-process via TestClient).

Runs inside the deployment image. Creates a real PyTorch (.pt) and TensorFlow
(.h5) model and pushes each through /upload -> /convert using FastAPI's
TestClient, so no HTTP server / port / background thread is involved (which is
what previously failed with connection-refused). Writes results to
/out/result.json (bind-mounted to the host) and prints the outcome. The job
fails unless BOTH report conversion_status == "success".
"""
import os

# Must be set before TensorFlow is imported anywhere so tf.keras resolves to the
# Keras 2 API (tf-keras) that tf2onnx requires. The image also sets this as an
# ENV; setting it here too keeps the script correct if run standalone.
os.environ.setdefault("TF_USE_LEGACY_KERAS", "1")

import json
import platform
import tempfile
from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)
tmp = Path(tempfile.mkdtemp())
result = {"python": platform.python_version()}


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

os.makedirs("/out", exist_ok=True)
with open("/out/result.json", "w") as f:
    json.dump(result, f, indent=2)
print("RESULT " + json.dumps(result))
