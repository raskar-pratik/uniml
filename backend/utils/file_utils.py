"""
UniML — File Utilities

Secure helpers for file I/O: upload handling, path validation,
size formatting, and extension checking.
"""

from __future__ import annotations

import shutil
import time
import uuid
from pathlib import Path

from loguru import logger

from backend.config import get_settings


# ── Size Formatting ──────────────────────────────────────────────────

def format_file_size(size_bytes: int) -> str:
    """Return a human-readable file size string."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(size_bytes) < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0  # type: ignore[assignment]
    return f"{size_bytes:.1f} PB"


# ── Extension Validation ────────────────────────────────────────────

def validate_extension(filename: str) -> bool:
    """Check whether the file extension is in the allow-list."""
    settings = get_settings()
    ext = Path(filename).suffix.lower()
    return ext in settings.allowed_extensions



# ── Path Security ────────────────────────────────────────────────────

def safe_upload_path(filename: str) -> Path:
    """
    Build a safe upload path.

    * Strips directory components from the filename (prevents traversal).
    * Prefixes with a UUID so filenames never collide.
    * Resolves the path and confirms it lives under the upload directory.
    """
    settings = get_settings()

    # Strip any directory parts from the client-provided filename
    clean_name = Path(filename).name

    # Create a unique subdirectory per upload
    session_id = uuid.uuid4().hex[:12]
    session_dir = settings.upload_dir / session_id
    session_dir.mkdir(parents=True, exist_ok=True)

    target = (session_dir / clean_name).resolve()

    # Ensure the resolved path is still under the upload directory
    if not str(target).startswith(str(settings.upload_dir.resolve())):
        raise ValueError(f"Path traversal detected: {filename}")

    logger.debug("Safe upload path: {}", target)
    return target


def resolve_managed_path(file_path: str) -> Path:
    """
    Resolve a client-supplied file path and confirm it lives inside one of
    the server's managed directories (uploads/ or generated/).

    This is the primary defence against path-traversal / arbitrary-file-read:
    endpoints such as /detect, /validate, /convert and /benchmark accept a
    `file_path` that originates from the client, so it must never be trusted
    to point anywhere on the host filesystem.

    Raises:
        ValueError:        the path is malformed.
        PermissionError:   the resolved path escapes the managed directories.
    """
    settings = get_settings()

    try:
        candidate = Path(file_path).resolve()
    except (OSError, RuntimeError) as exc:  # pragma: no cover - defensive
        raise ValueError(f"Invalid file path: {file_path}") from exc

    for base in settings.managed_dirs:
        try:
            candidate.relative_to(base)
            return candidate
        except ValueError:
            continue

    logger.warning("Rejected out-of-bounds file path: {}", file_path)
    raise PermissionError(
        "The requested path is outside the allowed directories."
    )


# ── File Save ────────────────────────────────────────────────────────

async def save_upload(file_content: bytes, filename: str) -> Path:
    """
    Persist uploaded bytes to a safe location on disk.

    Returns the absolute path of the saved file.
    """
    target = safe_upload_path(filename)
    target.write_bytes(file_content)
    logger.info("Saved upload: {} ({} bytes)", target, len(file_content))
    return target


# ── Cleanup ──────────────────────────────────────────────────────────

def sweep_old_artifacts(max_age_hours: int | None = None, dirs=None) -> int:
    """
    Delete top-level entries in the managed directories older than
    ``max_age_hours``, returning the number of entries removed.

    Only direct children of uploads/ and generated/ are considered (each is a
    per-upload / per-model directory or file), so this can't wander outside the
    managed roots. Dotfiles (e.g. .gitkeep) are always preserved so the
    directory structure survives in version control.

    A max age of 0 (or negative) disables the sweep.
    """
    settings = get_settings()
    if max_age_hours is None:
        max_age_hours = settings.cleanup_max_age_hours
    if max_age_hours <= 0:
        return 0
    if dirs is None:
        dirs = settings.managed_dirs

    cutoff = time.time() - max_age_hours * 3600
    removed = 0

    for base in dirs:
        base = Path(base)
        if not base.is_dir():
            continue
        for entry in base.iterdir():
            if entry.name.startswith("."):  # keep .gitkeep and friends
                continue
            try:
                if entry.stat().st_mtime >= cutoff:
                    continue
                if entry.is_dir():
                    shutil.rmtree(entry)
                else:
                    entry.unlink()
                removed += 1
            except OSError as exc:
                logger.warning("Cleanup could not remove {}: {}", entry, exc)

    if removed:
        logger.info(
            "Cleanup removed {} stale artifact(s) older than {}h", removed, max_age_hours
        )
    return removed

