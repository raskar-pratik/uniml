"""
UniML — Stats Router

Dashboard statistics computed from the real state on disk. No simulated values.
(The previous /metrics endpoint returned fabricated inference telemetry and has
been removed — UniML packages models, it does not host them.)
"""

from pathlib import Path

from fastapi import APIRouter

from backend.config import get_settings

router = APIRouter(prefix="/api/v1", tags=["Stats"])


def _dir_stats(base: Path) -> tuple[int, int]:
    """Return (top-level entry count, total size in bytes) for a directory."""
    count = 0
    size = 0
    if base.is_dir():
        for item in base.iterdir():
            if item.name.startswith("."):  # ignore .gitkeep etc.
                continue
            count += 1
            if item.is_dir():
                size += sum(f.stat().st_size for f in item.rglob("*") if f.is_file())
            elif item.is_file():
                size += item.stat().st_size
    return count, size


@router.get("/stats")
async def get_stats():
    """Real workspace statistics derived from uploads/ and generated/."""
    settings = get_settings()
    generated_count, generated_size = _dir_stats(settings.generated_dir)
    upload_count, upload_size = _dir_stats(settings.upload_dir)

    return {
        "generated_models_count": generated_count,
        "uploaded_models_count": upload_count,
        "total_storage_bytes": generated_size + upload_size,
    }
