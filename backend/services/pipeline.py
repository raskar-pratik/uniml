"""
UniML — Pipeline Service

Orchestrates the full model deployment pipeline:
Upload → Detect → Validate → Convert → Benchmark → Generate → Package

Each step is individually callable AND can be chained together
into a complete pipeline run.
"""

from __future__ import annotations

from pathlib import Path

from loguru import logger

from backend.config import get_settings
from backend.utils.file_utils import format_file_size
from models.enums import ModelStatus
from models.schemas import (
    GenerationRequest,
    GenerationResult,
)



def _find_onnx_artifact(model_id: str) -> Path | None:
    """
    Locate the converted ONNX model for a given model_id.

    The converter writes the artifact to ``generated/<model_id>/<name>.onnx``
    (directly under the model directory, not inside a project sub-folder), so
    we search that directory non-recursively.
    """
    settings = get_settings()
    model_dir = settings.generated_dir / model_id
    if not model_dir.is_dir():
        return None
    onnx_files = sorted(model_dir.glob("*.onnx"))
    return onnx_files[0] if onnx_files else None


def generate_deployment_package(
    req: GenerationRequest,
    onnx_path: str | None = None,
) -> GenerationResult:
    """
    Generate FastAPI server + Docker config + ZIP archive.

    Called either as part of the full pipeline or independently
    via the /api/v1/generate endpoint.

    If ``onnx_path`` is not supplied, the converted ONNX artifact is resolved
    from the model's generated directory so the packaged server ships with the
    actual model rather than a missing placeholder.
    """
    from generator.api_generator import generate_api_server
    from generator.docker_generator import generate_docker_files
    from generator.zip_packager import create_zip_package

    settings = get_settings()

    # Resolve the converted model if the caller did not pass one explicitly.
    if onnx_path is None:
        resolved = _find_onnx_artifact(req.model_id)
        if resolved is not None:
            onnx_path = str(resolved)
            logger.info("Resolved ONNX artifact for packaging: {}", onnx_path)
        else:
            logger.warning(
                "No ONNX artifact found for model_id={} — the generated package "
                "will not contain a model. Convert the model before generating.",
                req.model_id,
            )

    # Create output directory
    output_dir = settings.generated_dir / req.model_id / req.project_name
    output_dir.mkdir(parents=True, exist_ok=True)

    files_generated: list[str] = []

    # ── Generate FastAPI server ──────────────────────────────────
    logger.info("Generating FastAPI server in {}", output_dir)
    api_files = generate_api_server(
        output_dir=output_dir,
        project_name=req.project_name,
        model_path=onnx_path,
        host=req.host,
        port=req.port,
        include_readme=req.include_readme,
    )
    files_generated.extend(api_files)

    # ── Generate Docker files ────────────────────────────────────
    if req.include_docker:
        logger.info("Generating Docker configuration")
        docker_files = generate_docker_files(
            output_dir=output_dir,
            project_name=req.project_name,
            port=req.port,
        )
        files_generated.extend(docker_files)

    # ── Package into ZIP ─────────────────────────────────────────
    logger.info("Creating ZIP package")
    zip_path = create_zip_package(
        source_dir=output_dir,
        output_dir=settings.generated_dir / req.model_id,
        archive_name=req.project_name,
        onnx_model_path=onnx_path,
    )
    files_generated.append(str(zip_path))

    zip_size = zip_path.stat().st_size

    return GenerationResult(
        model_id=req.model_id,
        project_name=req.project_name,
        zip_path=str(zip_path),
        zip_size_bytes=zip_size,
        zip_size_human=format_file_size(zip_size),
        files_generated=files_generated,
    )
