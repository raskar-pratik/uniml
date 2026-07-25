# UniML Architecture

## Overview

UniML follows a **clean architecture** with clear separation between the presentation layer (a static single-page frontend), the API layer (FastAPI), and the core business logic (converter, validator, generator). The FastAPI backend serves both the REST API and the static frontend from a single process and origin.

## System Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                Static Single-Page Frontend (HTML/JS)            │
│  Dashboard │ Upload │ Validation │ Deploy │ Monitoring │ ⚙️       │
└──────────────────────────────┬───────────────────────────────────┘
                               │ fetch() — same-origin REST calls
┌──────────────────────────────▼───────────────────────────────────┐
│              FastAPI Backend (serves API + static files)         │
│  /health │ /info │ /upload │ /detect │ /validate │ /convert │ …  │
│                                                                  │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────┐  │
│  │  Middleware  │  │   Services   │  │        Utilities       │  │
│  │ Error Handler│  │   Pipeline   │  │ File Utils │ Logging   │  │
│  └─────────────┘  └──────┬───────┘  └────────────────────────┘  │
└──────────────────────────┬───────────────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────────────┐
│                      Core Engine                                 │
│                                                                  │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────┐  │
│  │  Detector   │  │  Validator   │  │  ONNX Converter        │  │
│  └──────┬──────┘  └──────────────┘  └────────────────────────┘  │
│         │                                                        │
│  ┌──────▼──────────────────────────────────────────────────────┐ │
│  │              Framework Handlers (Strategy Pattern)          │ │
│  │  PyTorchHandler │ TFHandler │ SklearnHandler │ OnnxHandler  │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────┐  │
│  │ Benchmarker │  │ API Generator│  │  Docker Generator      │  │
│  └─────────────┘  └──────────────┘  └────────────────────────┘  │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    ZIP Packager                             │ │
│  └─────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

## Design Patterns

### Strategy Pattern (Framework Handlers)
Each ML framework is a separate handler implementing a common `FrameworkHandler` protocol. Adding a new framework requires creating one new file — zero changes to existing code.

### Pipeline Pattern
The processing flow (Upload → Detect → Validate → Convert → Benchmark → Generate → Package) is modelled as a pipeline where each step is independently callable.

### Factory Pattern
The FastAPI app is created via `create_app()` factory function, enabling clean testing and configuration.

### Template Method (Code Generation)
Generated code uses Jinja2 templates, keeping the generation logic separate from the output format.

## Data Flow

1. **Upload**: User uploads model → saved to `uploads/{session_id}/`
2. **Detect**: File extension + content analysis → framework identification
3. **Validate**: Framework handler validates model integrity
4. **Convert**: Handler converts model to ONNX → saved to `generated/{model_id}/`
5. **Benchmark**: ONNX Runtime inference timing + memory measurement
6. **Generate**: Jinja2 renders FastAPI + Docker templates → saved to `generated/{model_id}/{project_name}/`
7. **Package**: Generated files **and the converted ONNX model** are zipped → `generated/{model_id}/{project_name}.zip`

## Security Model

- **Path containment**: Endpoints that accept a `file_path` (`/detect`, `/validate`, `/convert`, `/benchmark`) resolve the path and reject anything that does not live inside the managed `uploads/` or `generated/` directories. This prevents path-traversal and arbitrary-file reads from client-controlled input.
- **Upload hardening**: Uploads are extension-allow-listed, size-limited, stripped of directory components, and written into a per-upload UUID directory.
- **Untrusted model files**: Loading serialized models (`.pkl`, `.joblib`, PyTorch archives) can execute arbitrary code during deserialization — this is inherent to those formats, not specific to UniML. **Only process models from sources you trust.** For untrusted input, run UniML inside an isolated sandbox (e.g. a locked-down container) with no secrets and no outbound network access.
- **Error isolation**: All exceptions are funneled through a global handler that logs full tracebacks server-side and returns a sanitized `{error, detail, code}` envelope to the client.
- **CORS**: Credentials are only enabled when an explicit origin allow-list is configured; a wildcard origin disables credentials (per the CORS spec).
