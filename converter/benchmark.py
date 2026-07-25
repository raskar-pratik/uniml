"""
UniML — Model Benchmark

Measures model performance metrics:
- Inference time (ONNX Runtime)
- Memory usage
- File sizes
- Input/output shapes
"""

from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import psutil
from loguru import logger

from backend.utils.file_utils import format_file_size
from converter.detector import detect_framework
from converter.handlers import find_handler
from models.enums import MLFramework
from models.schemas import BenchmarkResult


def benchmark_model(file_path: Path, model_id: str = "") -> BenchmarkResult:
    """
    Benchmark a model's performance.

    If an ONNX version exists, uses ONNX Runtime for inference timing.
    Otherwise reports file-level metrics only.
    """
    detection = detect_framework(file_path)
    framework = detection.framework
    file_size = file_path.stat().st_size

    # ── Gather model info ────────────────────────────────────────
    input_shape = None
    output_shape = None

    handler = find_handler(file_path)
    if handler and handler.is_available():
        try:
            info = handler.get_model_info(file_path)
            input_shape = info.get("input_shape")
            output_shape = info.get("output_shape")
        except Exception as exc:
            logger.warning("Could not get model info for benchmark: {}", exc)

    # ── Try ONNX Runtime inference benchmark ─────────────────────
    inference_time_ms = None
    onnx_size_mb = None

    # Check if there's an ONNX version in the generated directory
    onnx_path = _find_onnx_model(file_path, model_id)

    if onnx_path and onnx_path.exists():
        onnx_size_mb = round(onnx_path.stat().st_size / (1024 * 1024), 2)
        inference_time_ms = _benchmark_onnx_inference(onnx_path, input_shape)
    elif framework == MLFramework.ONNX:
        onnx_size_mb = round(file_size / (1024 * 1024), 2)
        inference_time_ms = _benchmark_onnx_inference(file_path, input_shape)

    # ── Memory usage ─────────────────────────────────────────────
    process = psutil.Process()
    memory_mb = round(process.memory_info().rss / (1024 * 1024), 2)

    return BenchmarkResult(
        model_id=model_id,
        framework=framework,
        inference_time_ms=inference_time_ms,
        memory_usage_mb=memory_mb,
        model_size_mb=round(file_size / (1024 * 1024), 2),
        onnx_size_mb=onnx_size_mb,
        input_shape=input_shape,
        output_shape=output_shape,
    )


def _benchmark_onnx_inference(
    onnx_path: Path,
    input_shape: list | None,
    num_runs: int = 10,
    warmup_runs: int = 3,
) -> float | None:
    """
    Run inference with ONNX Runtime and return the average time in ms.
    """
    try:
        import onnxruntime as ort

        session = ort.InferenceSession(str(onnx_path))
        input_meta = session.get_inputs()[0]
        input_name = input_meta.name

        # Build a dummy input matching the expected shape
        shape = list(input_meta.shape)
        # Replace dynamic dims ('batch_size', None, etc.) with 1
        shape = [1 if isinstance(d, str) or d is None or d <= 0 else d for d in shape]

        dummy_input = np.random.randn(*shape).astype(np.float32)

        # Warmup
        for _ in range(warmup_runs):
            session.run(None, {input_name: dummy_input})

        # Timed runs
        times = []
        for _ in range(num_runs):
            start = time.perf_counter()
            session.run(None, {input_name: dummy_input})
            elapsed = (time.perf_counter() - start) * 1000  # ms
            times.append(elapsed)

        avg_time = round(sum(times) / len(times), 3)
        logger.info("ONNX inference benchmark: {:.3f} ms avg over {} runs", avg_time, num_runs)
        return avg_time

    except Exception as exc:
        logger.warning("ONNX benchmark failed: {}", exc)
        return None


def _find_onnx_model(file_path: Path, model_id: str) -> Path | None:
    """Look for a converted ONNX model in the generated directory."""
    from backend.config import get_settings

    settings = get_settings()

    # Check by model_id first
    if model_id:
        candidate = settings.generated_dir / model_id / f"{file_path.stem}.onnx"
        if candidate.exists():
            return candidate

    # Check by filename
    candidate = settings.generated_dir / file_path.stem / f"{file_path.stem}.onnx"
    if candidate.exists():
        return candidate

    return None


