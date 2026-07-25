"""
UniML — API Endpoint Tests

Tests for the FastAPI REST API endpoints.
"""

import pytest


class TestHealthEndpoints:
    """Test health and info endpoints."""

    def test_health_check(self, test_client):
        """GET /health should return 200 with status=healthy."""
        resp = test_client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "uptime_seconds" in data

    def test_platform_info(self, test_client):
        """GET /info should return platform metadata."""
        resp = test_client.get("/info")
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "UniML"
        assert "supported_frameworks" in data
        assert "supported_extensions" in data
        assert isinstance(data["supported_frameworks"], list)


class TestUploadEndpoints:
    """Test upload endpoints."""

    def test_upload_valid_file(self, test_client, sklearn_model_path):
        """POST /api/v1/upload should accept valid model files."""
        with open(sklearn_model_path, "rb") as f:
            resp = test_client.post(
                "/api/v1/upload",
                files={"file": ("test_model.pkl", f, "application/octet-stream")},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert "model_id" in data
        assert data["filename"] == "test_model.pkl"
        assert data["file_size_bytes"] > 0

    def test_upload_rejects_unsupported_extension(self, test_client, tmp_path):
        """POST /api/v1/upload should reject unsupported file types."""
        bad_file = tmp_path / "model.txt"
        bad_file.write_text("not a model")

        with open(bad_file, "rb") as f:
            resp = test_client.post(
                "/api/v1/upload",
                files={"file": ("model.txt", f, "text/plain")},
            )
        assert resp.status_code == 415

    def test_upload_rejects_empty_file(self, test_client, tmp_path):
        """POST /api/v1/upload should reject empty files."""
        empty = tmp_path / "empty.pkl"
        empty.touch()

        with open(empty, "rb") as f:
            resp = test_client.post(
                "/api/v1/upload",
                files={"file": ("empty.pkl", f, "application/octet-stream")},
            )
        assert resp.status_code == 400


class TestDetectEndpoint:
    """Test framework detection endpoint."""

    def test_detect_sklearn(self, test_client, sklearn_model_path):
        """POST /api/v1/detect should identify sklearn models.

        The model is uploaded first so it lives inside a managed directory —
        detection only operates on paths within uploads/ or generated/.
        """
        with open(sklearn_model_path, "rb") as f:
            upload = test_client.post(
                "/api/v1/upload",
                files={"file": ("test_model.pkl", f, "application/octet-stream")},
            )
        assert upload.status_code == 200
        file_path = upload.json()["file_path"]

        resp = test_client.post("/api/v1/detect", json={"file_path": file_path})
        assert resp.status_code == 200
        data = resp.json()
        assert data["framework"] == "sklearn"

    def test_detect_missing_file(self, test_client):
        """A managed path that does not exist should return 404."""
        from backend.config import get_settings

        settings = get_settings()
        missing = settings.upload_dir / "does-not-exist" / "model.pkl"

        resp = test_client.post(
            "/api/v1/detect",
            json={"file_path": str(missing)},
        )
        assert resp.status_code == 404

    def test_detect_rejects_path_traversal(self, test_client):
        """Paths outside the managed directories must be rejected with 403."""
        resp = test_client.post(
            "/api/v1/detect",
            json={"file_path": "/etc/passwd"},
        )
        assert resp.status_code == 403
