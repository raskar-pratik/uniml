"""Runnable check for item (3): /stats returns real values, /metrics is gone."""


def test_stats_returns_real_fields_only(test_client):
    resp = test_client.get("/api/v1/stats")
    assert resp.status_code == 200
    data = resp.json()

    # Real, computed fields are present and numeric.
    assert isinstance(data["generated_models_count"], int)
    assert isinstance(data["uploaded_models_count"], int)
    assert isinstance(data["total_storage_bytes"], int)

    # No fabricated fields remain.
    assert "gpu_compute_load" not in data
    assert "pipelines" not in data


def test_metrics_endpoint_removed(test_client):
    """The simulated telemetry endpoint has been deleted."""
    assert test_client.get("/api/v1/metrics").status_code == 404
