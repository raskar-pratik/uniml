"""
UniML — Generator Package

Generates deployment-ready code: FastAPI server, Docker config, and ZIP packages.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader
from loguru import logger

from backend.config import get_settings


def render_templates(
    template_map: dict[str, str],
    context: dict[str, Any],
    output_dir: Path,
) -> list[str]:
    """
    Render Jinja2 templates from the configured templates directory.

    Args:
        template_map: Mapping of template filename → output filename.
        context: Template variables.
        output_dir: Where to write rendered files.

    Returns:
        List of generated output filenames.
    """
    settings = get_settings()
    env = Environment(
        loader=FileSystemLoader(str(settings.templates_dir)),
        keep_trailing_newline=True,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    generated_files: list[str] = []

    for template_name, output_name in template_map.items():
        try:
            template = env.get_template(template_name)
            rendered = template.render(**context)

            output_file = output_dir / output_name
            output_file.write_text(rendered, encoding="utf-8")
            generated_files.append(output_name)

            logger.debug("Generated: {}", output_file)

        except Exception as exc:
            logger.error("Failed to generate {}: {}", output_name, exc)

    return generated_files
