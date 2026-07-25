"""
UniML — Global Error Handler Middleware

Catches all unhandled exceptions and returns a consistent JSON envelope.
Logs full tracebacks internally but never exposes them to the client.
"""

from __future__ import annotations

import traceback

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.exceptions import HTTPException as StarletteHTTPException

from models.schemas import ErrorResponse


def register_error_handlers(app: FastAPI) -> None:
    """Attach all exception handlers to the FastAPI app."""

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        # Normalise all HTTPExceptions into the standard error envelope while
        # preserving the intended status code and human-readable detail.
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error="Request failed",
                detail=str(exc.detail),
                code=f"HTTP_{exc.status_code}",
            ).model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        logger.warning("RequestValidationError: {}", exc.errors())
        return JSONResponse(
            status_code=422,
            content=ErrorResponse(
                error="Request validation error",
                detail="One or more request fields are invalid.",
                code="REQUEST_VALIDATION_ERROR",
            ).model_dump(),
        )

    @app.exception_handler(PermissionError)
    async def permission_error_handler(
        request: Request, exc: PermissionError
    ) -> JSONResponse:
        logger.warning("PermissionError on {}: {}", request.url.path, exc)
        return JSONResponse(
            status_code=403,
            content=ErrorResponse(
                error="Access denied",
                detail="Access to the requested resource is not allowed.",
                code="ACCESS_DENIED",
            ).model_dump(),
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        logger.warning("ValueError: {}", exc)
        return JSONResponse(
            status_code=422,
            content=ErrorResponse(
                error="Validation error",
                detail=str(exc),
                code="VALIDATION_ERROR",
            ).model_dump(),
        )

    @app.exception_handler(FileNotFoundError)
    async def file_not_found_handler(request: Request, exc: FileNotFoundError) -> JSONResponse:
        logger.warning("FileNotFoundError: {}", exc)
        return JSONResponse(
            status_code=404,
            content=ErrorResponse(
                error="File not found",
                detail=str(exc),
                code="FILE_NOT_FOUND",
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        # Log the FULL traceback internally
        logger.error(
            "Unhandled exception on {} {}:\n{}",
            request.method,
            request.url.path,
            traceback.format_exc(),
        )
        # Return a safe message to the client
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error="Internal server error",
                detail="An unexpected error occurred. Please try again.",
                code="INTERNAL_ERROR",
            ).model_dump(),
        )
