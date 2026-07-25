"""
UniML — Structured Logging Configuration

Uses Loguru for structured, rotated logging to both console and files.
All modules should import `logger` from this module.
"""

import sys
from pathlib import Path

from loguru import logger

from backend.config import get_settings


def setup_logging() -> None:
    """
    Configure Loguru with:
    - Console sink (coloured, human-readable)
    - File sink (JSON-structured, rotated)
    - Separate error log file
    """
    settings = get_settings()

    # Remove default handler
    logger.remove()

    # ── Console ──────────────────────────────────────────────────
    logger.add(
        sys.stderr,
        level=settings.log_level,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> — "
            "<level>{message}</level>"
        ),
        colorize=True,
    )

    # ── General log file ─────────────────────────────────────────
    log_dir = Path(settings.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    logger.add(
        str(log_dir / "uniml_{time:YYYY-MM-DD}.log"),
        level=settings.log_level,
        rotation=settings.log_rotation,
        retention=settings.log_retention,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} — {message}",
        encoding="utf-8",
    )

    # ── Error-only log file ──────────────────────────────────────
    logger.add(
        str(log_dir / "errors_{time:YYYY-MM-DD}.log"),
        level="ERROR",
        rotation=settings.log_rotation,
        retention=settings.log_retention,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} — {message}\n{exception}",
        encoding="utf-8",
        backtrace=True,
        diagnose=True,
    )

    logger.info("Logging initialised  —  level={}, dir={}", settings.log_level, log_dir)
