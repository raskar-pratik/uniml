"""
UniML — API Server Generator

Generates a production-ready FastAPI inference server from Jinja2 templates.
The generated code uses ONNX Runtime for inference.
"""

from __future__ import annotations

from pathlib import Path

from loguru import logger

from generator import render_templates


def generate_api_server(
    output_dir: Path,
    project_name: str = "ml_inference_server",
    model_path: str | None = None,
    host: str = "0.0.0.0",
    port: int = 8080,
    include_readme: bool = True,
) -> list[str]:
    """
    Generate a complete FastAPI inference server.

    Returns a list of generated file paths (relative to output_dir).
    """
    context = {
        "project_name": project_name,
        "model_path": model_path or "model.onnx",
        "host": host,
        "port": port,
    }

    template_map = {
        "main.py.j2": "main.py",
        "predict.py.j2": "predict.py",
        "config.py.j2": "config.py",
        "requirements.txt.j2": "requirements.txt",
    }
    if include_readme:
        template_map["README.md.j2"] = "README.md"

    generated_files = render_templates(template_map, context, output_dir)
    logger.info("Generated {} API server files in {}", len(generated_files), output_dir)
    return generated_files
