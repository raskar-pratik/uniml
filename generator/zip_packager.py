"""
UniML — ZIP Packager

Creates a downloadable ZIP archive containing:
- Generated FastAPI server code
- Docker configuration
- The ONNX model file
- README and requirements
"""

from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

from loguru import logger


def create_zip_package(
    source_dir: Path,
    output_dir: Path,
    archive_name: str = "ml_inference_server",
    onnx_model_path: str | None = None,
) -> Path:
    """
    Package the generated project directory into a ZIP file.

    If `onnx_model_path` is provided, the ONNX model is included
    in the ZIP as `model.onnx`.

    Returns the path to the created ZIP file.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    zip_path = output_dir / f"{archive_name}.zip"

    # Remove existing ZIP if present
    if zip_path.exists():
        zip_path.unlink()

    with zipfile.ZipFile(str(zip_path), "w", zipfile.ZIP_DEFLATED) as zf:
        # ── Add all generated files ──────────────────────────────
        if source_dir.exists():
            for file_path in source_dir.rglob("*"):
                if file_path.is_file() and not file_path.suffix == ".zip":
                    arcname = f"{archive_name}/{file_path.relative_to(source_dir)}"
                    zf.write(str(file_path), arcname)
                    logger.debug("Zipped: {}", arcname)

        # ── Add ONNX model ──────────────────────────────────────
        if onnx_model_path:
            model_path = Path(onnx_model_path)
            if model_path.exists():
                arcname = f"{archive_name}/model.onnx"
                zf.write(str(model_path), arcname)
                logger.debug("Zipped model: {}", arcname)
            else:
                logger.warning("ONNX model not found at {} — skipping", model_path)

    zip_size = zip_path.stat().st_size
    logger.info(
        "Created ZIP package: {} ({:.1f} MB, {} files)",
        zip_path.name,
        zip_size / (1024 * 1024),
        len(list(source_dir.rglob("*"))) if source_dir.exists() else 0,
    )

    return zip_path
