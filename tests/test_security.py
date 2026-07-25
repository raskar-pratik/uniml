"""Runnable check for item (1): API key on write endpoints, skippable when unset."""

from fastapi.testclient import TestClient


def test_write_endpoints_open_when_key_unset(test_client):
    """With no UNIML_API_KEY configured (default), write endpoints must not 401."""
    resp = test_client.post("/api/v1/detect", json={"file_path": "nope"})
    assert resp.status_code != 401


def test_write_endpoints_require_key_when_set(monkeypatch):
    """With a key configured, write endpoints require a matching X-API-Key header."""
    from backend.config import get_settings
    from backend.main import create_app

    monkeypatch.setenv("UNIML_API_KEY", "s3cret")
    get_settings.cache_clear()
    try:
        client = TestClient(create_app())

        # Missing key → 401
        assert client.post("/api/v1/detect", json={"file_path": "x"}).status_code == 401

        # Wrong key → 401
        bad = client.post("/api/v1/detect", json={"file_path": "x"}, headers={"X-API-Key": "nope"})
        assert bad.status_code == 401

        # Correct key → passes auth (path validation then rejects it, but never 401)
        ok = client.post("/api/v1/detect", json={"file_path": "x"}, headers={"X-API-Key": "s3cret"})
        assert ok.status_code != 401

        # Read-only endpoints stay open without a key
        assert client.get("/api/v1/stats").status_code == 200
    finally:
        monkeypatch.delenv("UNIML_API_KEY", raising=False)
        get_settings.cache_clear()
