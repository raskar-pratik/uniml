"""In-container end-to-end conversion check (driven over the real HTTP API).

Boots the FastAPI app with uvicorn in a background thread, then creates a real
PyTorch (.pt) and TensorFlow (.h5) model and runs each through /upload -> /convert.
Writes results to /out/result.json (bind-mounted to the host). No docker exec.
"""
import json
import os
import threading
import time

import uvicorn
import requests

BASE = "http://127.0.0.1:8000"


def serve():
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, log_level="warning")


threading.Thread(target=serve, daemon=True).start()

server_up = False
for _ in range(90):
    try:
        if requests.get(f"{BASE}/health", timeout=2).status_code == 200:
            server_up = True
            break
    except Exception:
        pass
    time.sleep(1)

result = {"server_up": server_up}

# Real PyTorch model.
import torch
import torch.nn as nn

torch.save(nn.Sequential(nn.Linear(4, 8), nn.ReLU(), nn.Linear(8, 3)), "/tmp/model.pt")

# Real Keras model.
import tensorflow as tf

tf.keras.Sequential([
    tf.keras.layers.Input((4,)),
    tf.keras.layers.Dense(8, activation="relu"),
    tf.keras.layers.Dense(3),
]).save("/tmp/model.h5")


def drive(path, filename):
    with open(path, "rb") as f:
        up = requests.post(
            f"{BASE}/api/v1/upload",
            files={"file": (filename, f, "application/octet-stream")},
            timeout=120,
        )
    if up.status_code != 200:
        return {"stage": "upload", "http": up.status_code, "body": up.text[:300]}
    uj = up.json()
    conv = requests.post(
        f"{BASE}/api/v1/convert",
        json={"file_path": uj["file_path"], "model_id": uj["model_id"]},
        timeout=600,
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


result["pytorch"] = drive("/tmp/model.pt", "model.pt")
result["tensorflow"] = drive("/tmp/model.h5", "model.h5")

os.makedirs("/out", exist_ok=True)
with open("/out/result.json", "w") as f:
    json.dump(result, f, indent=2)
print("RESULT " + json.dumps(result))
