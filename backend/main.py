"""
UniML — FastAPI Application Factory

Creates and configures the FastAPI application with:
- CORS middleware
- Exception handlers
- All routers
- Lifespan events (startup/shutdown)
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from backend.config import get_settings
from backend.middleware.error_handler import register_error_handlers
from backend.security import require_api_key
from backend.utils.logging_config import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Startup and shutdown logic."""
    settings = get_settings()
    setup_logging()
    settings.ensure_dirs()
    logger.info(
        "🚀 {} v{} starting  —  upload_dir={}, generated_dir={}",
        settings.app_name,
        settings.app_version,
        settings.upload_dir,
        settings.generated_dir,
    )
    _log_converter_readiness()

    cleanup_task = asyncio.create_task(_cleanup_loop(settings))
    logger.info(
        "Cleanup sweep every {} min (removing artifacts older than {} h){}",
        settings.cleanup_interval_minutes,
        settings.cleanup_max_age_hours,
        "" if settings.cleanup_max_age_hours > 0 else " — disabled",
    )

    yield

    cleanup_task.cancel()
    logger.info("👋 {} shutting down", settings.app_name)


async def _cleanup_loop(settings) -> None:
    """Periodically delete stale uploads/ and generated/ artifacts."""
    from backend.utils.file_utils import sweep_old_artifacts

    interval = max(1, settings.cleanup_interval_minutes) * 60
    while True:
        try:
            await asyncio.sleep(interval)
            # Run the blocking filesystem work off the event loop.
            await asyncio.to_thread(sweep_old_artifacts)
        except asyncio.CancelledError:
            break
        except Exception as exc:  # pragma: no cover - defensive, keep loop alive
            logger.warning("Cleanup sweep failed: {}", exc)


def _log_converter_readiness() -> None:
    """Report which framework converters are usable in this environment.

    Turns the silent 'unsupported' failure mode into a visible startup signal:
    if PyTorch/TensorFlow libraries are missing, you see it here rather than
    only when a conversion fails. Reuses the existing handler registry.
    """
    from converter.handlers import ALL_HANDLERS

    ready, missing = [], []
    for handler in ALL_HANDLERS:
        (ready if handler.is_available() else missing).append(handler.framework_name)

    logger.info("Converters ready: {}", ", ".join(ready) or "none")
    if missing:
        logger.warning(
            "Converters unavailable (library not installed): {} — "
            "run in the Docker image or `pip install -r requirements-convert.txt` "
            "for full framework support.",
            ", ".join(missing),
        )


def create_app() -> FastAPI:
    """Build and return the configured FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description="Universal ML Deployment Platform — Upload, convert, and deploy ML models in seconds.",
        version=settings.app_version,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # ── CORS ─────────────────────────────────────────────────────
    # Credentials cannot be combined with a wildcard origin (CORS spec), so
    # allow_credentials is derived from whether the origin list is explicit.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Error handlers ───────────────────────────────────────────
    register_error_handlers(app)

    # ── Routers ──────────────────────────────────────────────────
    from backend.routers.health import router as health_router
    from backend.routers.upload import router as upload_router
    from backend.routers.convert import router as convert_router
    from backend.routers.deploy import router as deploy_router
    from backend.routers.stats import router as stats_router

    # Write endpoints (upload + detect/validate/convert/benchmark) require the
    # API key when one is configured. Read-only routers stay open.
    app.include_router(health_router)
    app.include_router(upload_router, dependencies=[Depends(require_api_key)])
    app.include_router(convert_router, dependencies=[Depends(require_api_key)])
    app.include_router(deploy_router)
    app.include_router(stats_router)

    # ── Static Frontend (SPA) ────────────────────────────────────
    # Serve the built single-page app. Mounting at "/" is done LAST so every
    # API route (and /docs, /redoc, /openapi.json) is matched first; the SPA
    # handler only sees paths no API route claimed.
    #
    # Resolution order: the built React bundle (web/dist) is preferred; the
    # legacy static frontend is used as a fallback if the bundle isn't built.
    _mount_spa(app, settings)

    return app


def _mount_spa(app: FastAPI, settings) -> None:
    """Mount the frontend, with client-side-routing fallback to index.html."""
    from starlette.exceptions import HTTPException as StarletteHTTPException
    from starlette.responses import FileResponse, Response
    from starlette.staticfiles import StaticFiles

    candidates = [
        settings.project_root / "web" / "dist",   # built React SPA
        settings.project_root / "frontend" / "static",  # legacy fallback
    ]
    static_dir = next((d for d in candidates if (d / "index.html").is_file()), None)

    if static_dir is None:
        logger.warning(
            "No built frontend found. Run `npm install && npm run build` in web/ "
            "to generate web/dist. API remains fully available."
        )
        return

    logger.info("Serving frontend from {}", static_dir)

    # Paths owned by the backend — never shadowed by the SPA fallback.
    api_prefixes = ("/api", "/health", "/info", "/docs", "/redoc", "/openapi.json")
    index_file = str(static_dir / "index.html")

    class SPAStaticFiles(StaticFiles):
        """StaticFiles that returns index.html for unknown non-API routes.

        This lets the client-side router handle deep links (e.g. /deploy) on a
        full page reload, while still returning real 404s for missing assets
        and unknown API paths.
        """

        async def get_response(self, path: str, scope):
            try:
                return await super().get_response(path, scope)
            except StarletteHTTPException as exc:
                if exc.status_code == 404:
                    request_path = scope.get("path", "/")
                    if request_path.startswith(api_prefixes):
                        raise  # let the API surface a proper 404
                    # Serve the SPA shell for client-side routes.
                    return FileResponse(index_file)
                raise

    app.mount("/", SPAStaticFiles(directory=str(static_dir), html=True), name="spa")


# The application instance used by `uvicorn backend.main:app`
app = create_app()
