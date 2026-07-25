"""
UniML — Application Configuration

All settings are loaded from environment variables (with sensible defaults)
using pydantic-settings.  Override any value by setting the corresponding
env var or by placing a `.env` file in the project root.
"""

from pathlib import Path
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


# Project root is two levels up from this file (backend/config.py → UniML/)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Central configuration for the UniML platform."""

    model_config = SettingsConfigDict(
        env_file=str(_PROJECT_ROOT / ".env"),
        env_prefix="UNIML_",
        case_sensitive=False,
    )

    # ── General ──────────────────────────────────────────────────────
    app_name: str = "UniML"
    app_version: str = "1.0.0"
    debug: bool = False

    # ── Server ───────────────────────────────────────────────────────
    host: str = "0.0.0.0"
    port: int = 8000
    # Comma-separated origins via UNIML_CORS_ORIGINS, or "*" for any.
    # Note: credentials are automatically disabled when "*" is used, per the
    # CORS spec (a wildcard origin cannot be combined with credentials).
    cors_origins: list[str] = ["*"]

    # ── Paths ────────────────────────────────────────────────────────
    project_root: Path = _PROJECT_ROOT
    upload_dir: Path = _PROJECT_ROOT / "uploads"
    generated_dir: Path = _PROJECT_ROOT / "generated"
    log_dir: Path = _PROJECT_ROOT / "logs"
    templates_dir: Path = _PROJECT_ROOT / "generator" / "templates"

    # ── Upload Limits ────────────────────────────────────────────────
    max_upload_size_mb: int = 500
    allowed_extensions: list[str] = [
        ".pt", ".pth", ".pkl", ".joblib",
        ".h5", ".keras", ".onnx",
    ]

    # ── Behaviour ────────────────────────────────────────────────────
    # When True, the original uploaded file is deleted after a successful
    # ONNX conversion to save disk space. Disabled by default so that
    # subsequent steps (e.g. benchmarking, re-validation) keep working.
    delete_raw_after_convert: bool = False

    # ── Security ─────────────────────────────────────────────────────
    # A single shared key required on write endpoints via the `X-API-Key`
    # header. When unset (the default), write endpoints are open — convenient
    # for local dev. Set UNIML_API_KEY in any shared/production deployment.
    api_key: str | None = None

    # ── Cleanup ──────────────────────────────────────────────────────
    # A background sweep deletes top-level entries in uploads/ and generated/
    # older than this many hours, at the given interval. Keeps disk from
    # filling with abandoned jobs. Set max age to 0 to disable the sweep.
    cleanup_max_age_hours: int = 24
    cleanup_interval_minutes: int = 60

    # ── Logging ──────────────────────────────────────────────────────
    log_level: str = "INFO"
    log_rotation: str = "10 MB"
    log_retention: str = "30 days"

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    @property
    def cors_allow_credentials(self) -> bool:
        """
        Credentials may only be allowed when the origin list is explicit.
        The CORS spec forbids combining a wildcard origin with credentials,
        and browsers reject such responses.
        """
        return "*" not in self.cors_origins

    @property
    def managed_dirs(self) -> tuple[Path, ...]:
        """Directories that user-supplied file paths are allowed to reference."""
        return (self.upload_dir.resolve(), self.generated_dir.resolve())

    def ensure_dirs(self) -> None:
        """Create runtime directories if they don't exist."""
        for d in (self.upload_dir, self.generated_dir, self.log_dir):
            d.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings singleton."""
    return Settings()
