"""
UniML — API key dependency for write endpoints.

A single shared key checked against the `X-API-Key` header. When
``settings.api_key`` is unset (the default), the check is skipped entirely so
local development needs no configuration. Set ``UNIML_API_KEY`` to lock down
write endpoints in any shared/production deployment.
"""

from __future__ import annotations

import secrets

from fastapi import Header, HTTPException, status

from backend.config import get_settings


async def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """FastAPI dependency: enforce the shared API key on a route.

    - No key configured  → allow (local dev).
    - Key configured     → require a matching `X-API-Key` header, else 401.
    """
    expected = get_settings().api_key
    if not expected:
        return

    if not x_api_key or not secrets.compare_digest(x_api_key, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
