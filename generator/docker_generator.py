"""
UniML — Docker Configuration Generator

Generates Dockerfile, docker-compose.yml, and startup script from templates.
"""

from __future__ import annotations

from pathlib import Path

from loguru import logger

from generator import render_templates


def generate_docker_files(
    output_dir: Path,
    project_name: str = "ml_inference_server",
    host: str = "0.0.0.0",
    port: int = 8080,
) -> list[str]:
    """
    Generate Docker deployment files.

    Returns a list of generated file names.
    """
    context = {
        "project_name": project_name,
        "host": host,
        "port": port,
    }

    template_map = {
        "Dockerfile.j2": "Dockerfile",
        "docker-compose.yml.j2": "docker-compose.yml",
        "startup.sh.j2": "startup.sh",
    }

    generated_files = render_templates(template_map, context, output_dir)
    logger.info("Generated {} Docker files in {}", len(generated_files), output_dir)
    return generated_files
