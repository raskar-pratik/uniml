# UniML API Reference

## Base URL

```
http://localhost:8000
```

---

## Health & Info

### GET /health

Health check probe.

**Response** `200 OK`
```json
{
    "status": "healthy",
    "version": "1.0.0",
    "uptime_seconds": 42.5
}
```

### GET /info

Platform metadata and capabilities.

**Response** `200 OK`
```json
{
    "name": "UniML",
    "version": "1.0.0",
    "python_version": "3.11.5",
    "supported_frameworks": ["pytorch", "tensorflow", "sklearn", "onnx"],
    "supported_extensions": [".pt", ".pth", ".pkl", ".joblib", ".h5", ".keras", ".onnx"],
    "max_upload_size_mb": 500
}
```

---

## Upload

### POST /api/v1/upload

Upload a model file.

**Request** `multipart/form-data`
- `file`: The model file

**Response** `200 OK`
```json
{
    "model_id": "a1b2c3d4e5f6",
    "filename": "model.pkl",
    "file_size_bytes": 12345,
    "file_size_human": "12.1 KB",
    "upload_time": "2026-01-01T00:00:00",
    "file_path": "/app/uploads/a1b2c3/model.pkl",
    "status": "uploaded"
}
```

**Errors**
- `400` — Empty file or no filename
- `413` — File exceeds size limit
- `415` — Unsupported file extension

---

## Detection

### POST /api/v1/detect

Detect the ML framework of an uploaded model.

**Request** `application/json`
```json
{
    "file_path": "/app/uploads/a1b2c3/model.pkl"
}
```

**Response** `200 OK`
```json
{
    "model_id": "",
    "framework": "sklearn",
    "confidence": 0.95,
    "details": "Detected as Scikit-Learn",
    "status": "detected"
}
```

---

## Validation

### POST /api/v1/validate

Validate a model file.

**Request** `application/json`
```json
{
    "file_path": "/app/uploads/a1b2c3/model.pkl"
}
```

**Response** `200 OK`
```json
{
    "model_id": "",
    "framework": "sklearn",
    "is_valid": true,
    "issues": [
        {
            "severity": "info",
            "code": "MODEL_LOADED",
            "message": "Successfully loaded estimator: LinearRegression"
        }
    ],
    "input_shape": [2],
    "output_shape": [1],
    "model_class": "LinearRegression",
    "parameters": null,
    "status": "validated"
}
```

---

## Conversion

### POST /api/v1/convert

Convert a model to ONNX format.

**Request** `application/json`
```json
{
    "file_path": "/app/uploads/a1b2c3/model.pkl",
    "model_id": "a1b2c3d4e5f6"
}
```

**Response** `200 OK`
```json
{
    "model_id": "a1b2c3d4e5f6",
    "conversion_status": "success",
    "original_format": "sklearn",
    "onnx_path": "/app/generated/a1b2c3d4e5f6/model.onnx",
    "onnx_size_bytes": 5432,
    "onnx_size_human": "5.3 KB",
    "error_message": null,
    "status": "converted"
}
```

---

## Benchmark

### POST /api/v1/benchmark

Benchmark a model's performance.

**Request** `application/json`
```json
{
    "file_path": "/app/uploads/a1b2c3/model.pkl",
    "model_id": "a1b2c3d4e5f6"
}
```

**Response** `200 OK`
```json
{
    "model_id": "a1b2c3d4e5f6",
    "framework": "sklearn",
    "inference_time_ms": 0.125,
    "memory_usage_mb": 85.3,
    "model_size_mb": 0.01,
    "onnx_size_mb": 0.005,
    "input_shape": [2],
    "output_shape": [1],
    "status": "benchmarked"
}
```

---

## Generation

### POST /api/v1/generate

Generate a deployment package.

**Request** `application/json`
```json
{
    "model_id": "a1b2c3d4e5f6",
    "project_name": "my_model_server",
    "host": "0.0.0.0",
    "port": 8080,
    "include_docker": true,
    "include_readme": true
}
```

**Response** `200 OK`
```json
{
    "model_id": "a1b2c3d4e5f6",
    "project_name": "my_model_server",
    "zip_path": "/app/generated/a1b2c3d4e5f6/my_model_server.zip",
    "zip_size_bytes": 15000,
    "zip_size_human": "14.6 KB",
    "files_generated": ["main.py", "predict.py", "config.py", "Dockerfile", "..."],
    "status": "ready"
}
```

---

## Download

### GET /api/v1/download/{model_id}

Download the generated ZIP package.

**Response** `200 OK` — `application/zip` binary stream

**Errors**
- `404` — Package not found

---

## Error Format

All errors follow the standard envelope:

```json
{
    "error": "Human-readable error message",
    "detail": "Additional technical detail (optional)",
    "code": "ERROR_CODE"
}
```
