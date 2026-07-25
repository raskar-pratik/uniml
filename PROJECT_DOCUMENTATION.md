# UniML — Complete Project Documentation

> **UniML** is a universal ML model deployment studio. It takes a trained model
> (PyTorch, TensorFlow, scikit-learn, or ONNX), auto-detects its framework,
> validates it, converts it to ONNX, and generates a ready-to-run FastAPI +
> Docker inference package that you can download as a single ZIP.

| | |
|---|---|
| **Name** | UniML |
| **Version** | 1.0.0 |
| **Backend** | Python 3.11+, FastAPI, Pydantic v2, Loguru |
| **Frontend** | React 18, Vite 5, Tailwind CSS 3, React Router 6, lucide-react |
| **Model tooling** | ONNX, onnxruntime, PyTorch, TensorFlow, scikit-learn, skl2onnx, tf2onnx |
| **Packaging** | Jinja2 templates → FastAPI server + Dockerfile + docker-compose + README, zipped |
| **License** | MIT |
| **Default port** | 8000 (API + dashboard, single process) |

---

## Table of Contents

1. [What UniML Does](#1-what-uniml-does)
2. [Key Features](#2-key-features)
3. [Architecture Overview](#3-architecture-overview)
4. [Technology Stack](#4-technology-stack)
5. [Directory Structure](#5-directory-structure)
6. [The Pipeline, End to End](#6-the-pipeline-end-to-end)
7. [Backend Reference](#7-backend-reference)
8. [Complete API Reference](#8-complete-api-reference)
9. [Data Model & Enums](#9-data-model--enums)
10. [Model Conversion Engine](#10-model-conversion-engine)
11. [Deployment Package Generator](#11-deployment-package-generator)
12. [Frontend Reference](#12-frontend-reference)
13. [Design System](#13-design-system)
14. [Security Model](#14-security-model)
15. [Configuration & Environment Variables](#15-configuration--environment-variables)
16. [Setup & Installation](#16-setup--installation)
17. [Running the Application](#17-running-the-application)
18. [Docker Deployment](#18-docker-deployment)
19. [Testing](#19-testing)
20. [Known Limitations & Simulated Data](#20-known-limitations--simulated-data)
21. [Change Log (This Engagement)](#21-change-log-this-engagement)
22. [Troubleshooting](#22-troubleshooting)

---

## 1. What UniML Does

UniML removes the friction between "I have a trained model file" and "I have a
running inference service." The user journey is a linear, four-step pipeline:

1. **Upload** a trained model file.
2. **Inspect** it — the framework is auto-detected and the model is validated
   (structure, input/output shapes, parameter count, issues).
3. **Convert** it to ONNX, a portable runtime-agnostic format.
4. **Deploy** — generate a self-contained FastAPI inference server (optionally
   with Docker config and a README), bundled with the converted model into a
   downloadable ZIP.

UniML **packages** models for deployment; it does not host inference itself.
The generated package is what you run in production.

---

## 2. Key Features

- **Multi-framework support** — PyTorch (`.pt`, `.pth`), TensorFlow (`.h5`,
  `.keras`), scikit-learn (`.pkl`, `.joblib`), and ONNX (`.onnx`).
- **Automatic framework detection** with a confidence score.
- **Model validation** — surfaces structural issues by severity, reports input
  and output shapes, model class, and parameter counts.
- **ONNX conversion** via framework-specific handlers with graceful
  `skipped` / `failed` / `unsupported` outcomes.
- **Code generation** — a complete FastAPI inference server rendered from Jinja2
  templates, plus optional Dockerfile / docker-compose and README.
- **ZIP packaging** — the generated server **and the converted ONNX model** are
  bundled into a single downloadable archive.
- **Single-process serving** — one FastAPI process serves both the REST API and
  the compiled React dashboard.
- **Production-grade web dashboard** — React + Vite SPA with a consistent design
  system, responsive layout, accessibility baseline, and a guided pipeline UI.

---

## 3. Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                React + Vite Single-Page Dashboard                 │
│   Dashboard │ Upload │ Inspect │ Convert │ Deploy │ Monitoring    │
└──────────────────────────────┬───────────────────────────────────┘
                               │ fetch() — same-origin REST calls
┌──────────────────────────────▼───────────────────────────────────┐
│           FastAPI Backend (serves API + built SPA at /)           │
│  ┌───────────┐ ┌───────────┐ ┌──────────┐ ┌──────────┐ ┌───────┐ │
│  │  health   │ │  upload   │ │ convert  │ │  deploy  │ │ stats │ │
│  │  router   │ │  router   │ │  router  │ │  router  │ │router │ │
│  └───────────┘ └─────┬─────┘ └────┬─────┘ └────┬─────┘ └───────┘ │
│                      │            │            │                  │
│         ┌────────────▼────────────▼────────────▼─────────────┐   │
│         │            services/pipeline.py                     │   │
│         └────┬──────────────┬───────────────┬────────────────┘   │
│              │              │               │                    │
│      ┌───────▼───┐  ┌───────▼────┐  ┌────────▼─────────┐         │
│      │ converter │  │ validator  │  │    generator     │         │
│      │ detector  │  │            │  │ api / docker /   │         │
│      │ handlers  │  │            │  │ zip / templates  │         │
│      └───────────┘  └────────────┘  └──────────────────┘         │
└──────────────────────────────────────────────────────────────────┘
        │                    │                      │
   uploads/            generated/                 logs/
```

### Layers

- **Presentation** — a static React SPA (built to `web/dist`) served by FastAPI.
- **API** — FastAPI routers grouped by concern (health, upload, convert, deploy,
  stats), all responses funneled through a global error envelope.
- **Orchestration** — `services/pipeline.py` coordinates detect → validate →
  convert → generate → package.
- **Core logic** — three independent engines: `converter/`, `validator/`,
  `generator/`. These have no FastAPI dependency and are individually testable.
- **Contracts** — `models/schemas.py` (Pydantic models) and `models/enums.py`
  (shared vocabulary) define the API surface.

### Design principles

- **Clean separation** between presentation, API, and core logic.
- **Stateless service** — no database; the client threads a `model_id` through
  the pipeline, and artifacts live on disk under `uploads/` and `generated/`.
- **Lazy heavy imports** — ML libraries (torch, tf, sklearn) are imported inside
  functions so the API boots quickly and optional deps stay optional.

---

## 4. Technology Stack

### Backend
- **Python 3.11+**
- **FastAPI** — web framework and routing
- **Pydantic v2 / pydantic-settings** — schemas and configuration
- **Uvicorn** — ASGI server
- **Loguru** — structured logging with rotation/retention
- **Jinja2** — code generation templates
- **ONNX / onnxruntime** — conversion target and validation
- **skl2onnx**, **tf2onnx**, **torch.onnx** — framework-specific converters

### Frontend
- **React 18** — UI library
- **Vite 5** — build tool and dev server
- **Tailwind CSS 3** — utility-first styling with a token-based design system
- **React Router 6** — client-side routing (BrowserRouter)
- **lucide-react** — vector icon set
- **Fira Sans / Fira Code** — typography (Google Fonts)

---

## 5. Directory Structure

```
UniML/
├── backend/                     # FastAPI application
│   ├── main.py                  # App factory, CORS, error handlers, SPA serving
│   ├── config.py                # Pydantic settings (env: UNIML_*)
│   ├── middleware/
│   │   └── error_handler.py     # Global exception handlers → error envelope
│   ├── routers/
│   │   ├── health.py            # /health, /info
│   │   ├── upload.py            # /api/v1/upload
│   │   ├── convert.py           # /api/v1/detect, /validate, /convert, /benchmark
│   │   ├── deploy.py            # /api/v1/generate, /download/{model_id}
│   │   └── stats.py             # /api/v1/stats, /metrics
│   ├── services/
│   │   └── pipeline.py          # Orchestrates the full pipeline
│   └── utils/
│       ├── file_utils.py        # Safe path resolution, size formatting, saving
│       └── logging_config.py    # Loguru setup
│
├── converter/                   # Framework detection + ONNX conversion
│   ├── detector.py              # detect_framework()
│   ├── onnx_converter.py        # convert_to_onnx() orchestrator
│   ├── benchmark.py             # Inference benchmarking
│   └── handlers/
│       ├── base.py              # FrameworkHandler protocol
│       ├── pytorch_handler.py
│       ├── tensorflow_handler.py
│       ├── sklearn_handler.py
│       ├── onnx_handler.py
│       └── __init__.py          # Handler registry + find_handler()
│
├── validator/
│   └── validator.py             # Model structural validation
│
├── generator/                   # Deployment package generation
│   ├── api_generator.py         # Renders the FastAPI server
│   ├── docker_generator.py      # Renders Dockerfile + docker-compose
│   ├── zip_packager.py          # Bundles files + ONNX model into a ZIP
│   └── templates/               # Jinja2 templates
│       ├── main.py.j2
│       ├── predict.py.j2
│       ├── config.py.j2
│       ├── requirements.txt.j2
│       ├── README.md.j2
│       ├── Dockerfile.j2
│       ├── docker-compose.yml.j2
│       └── startup.sh.j2
│
├── models/
│   ├── schemas.py               # Pydantic request/response models
│   └── enums.py                 # Shared enums
│
├── web/                         # React + Vite dashboard (built → web/dist)
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js           # Dev proxy + build config
│   ├── tailwind.config.js       # Design tokens mapped to Tailwind
│   ├── postcss.config.js
│   └── src/
│       ├── main.jsx             # Entry (Router + providers)
│       ├── App.jsx              # Route definitions
│       ├── index.css            # Design tokens + base styles
│       ├── lib/                 # api.js, format.js, constants.js, cn.js
│       ├── context/             # ToastContext, PipelineContext
│       ├── hooks/               # useFetch
│       ├── components/
│       │   ├── ui/              # Button, Card, Badge, Spinner, ProgressBar,
│       │   │                    #   StatCard, Skeleton, EmptyState, Modal,
│       │   │                    #   Field (Input/Select/Switch), Toaster, Tooltip
│       │   ├── common/          # FrameworkBadge, ConfidenceMeter, Sparkline
│       │   ├── layout/          # AppLayout, Sidebar, Topbar, PageHeader, nav
│       │   └── pipeline/        # PipelineStepper, FileDropzone, RequireModel
│       └── pages/               # Dashboard, Upload, Inspect, Convert,
│                                #   Deploy, Monitoring, NotFound
│
├── frontend/static/             # Legacy static UI (fallback; superseded by web/)
├── deployment/
│   ├── Dockerfile               # Multi-stage: node build → python runtime
│   ├── docker-compose.yml
│   └── .env.example
├── docs/                        # api.md, architecture.md, user_guide.md
├── tests/                       # pytest suite (conftest, test_api, test_detector, ...)
├── uploads/                     # Uploaded model files (runtime)
├── generated/                   # Converted models + generated packages (runtime)
├── logs/                        # Application logs (runtime)
├── requirements.txt
├── README.md
└── PROJECT_DOCUMENTATION.md     # ← this file
```

---

## 6. The Pipeline, End to End

1. **Upload** — `POST /api/v1/upload` saves the file into a per-upload UUID
   directory under `uploads/` and returns a generated `model_id` plus the saved
   `file_path`.
2. **Detect** — `POST /api/v1/detect` inspects the file and returns the detected
   `framework` with a `confidence` score.
3. **Validate** — `POST /api/v1/validate` loads the model and reports
   `is_valid`, `issues[]`, `input_shape`, `output_shape`, `model_class`, and
   `parameters`.
4. **Convert** — `POST /api/v1/convert` (with the `file_path` **and** the
   `model_id` from step 1) converts to ONNX, writing to
   `generated/<model_id>/<name>.onnx`. Result status is one of `success`,
   `skipped` (already ONNX), `failed`, or `unsupported`.
5. **Generate** — `POST /api/v1/generate` renders the FastAPI server + optional
   Docker/README into `generated/<model_id>/<project_name>/`, resolves the ONNX
   artifact from `generated/<model_id>/`, and zips everything (including the
   model) to `generated/<model_id>/<project_name>.zip`.
6. **Download** — `GET /api/v1/download/<model_id>` streams the ZIP.

> **Critical detail:** the same `model_id` returned by `/upload` must be passed
> to `/convert` and `/generate` so the converted ONNX and the generated package
> resolve to the same directory. The React frontend threads this automatically
> via `PipelineContext`.

---

## 7. Backend Reference

### `backend/main.py` — Application factory
- `create_app()` builds the FastAPI app: configures CORS, registers error
  handlers, includes all routers, then mounts the SPA **last**.
- **Lifespan**: on startup, initializes logging and ensures runtime directories
  exist; logs startup/shutdown.
- **CORS**: `allow_credentials` is derived from `cors_allow_credentials` — it is
  automatically **disabled** when the origin list is `["*"]` (per the CORS spec).
- **SPA serving** (`_mount_spa`): prefers `web/dist`, falls back to
  `frontend/static`. Uses a custom `SPAStaticFiles` subclass that returns
  `index.html` for unknown non-API routes (so client-side routing works on a
  full page reload) while returning real 404s for missing assets and for unknown
  paths under `/api`, `/health`, `/info`, `/docs`, `/redoc`, `/openapi.json`.

### `backend/config.py` — Settings
- Pydantic `BaseSettings` with env prefix **`UNIML_`** and optional `.env` file.
- Properties: `max_upload_size_bytes`, `cors_allow_credentials`, `managed_dirs`
  (the `uploads/` and `generated/` directories that user paths are confined to).
- `ensure_dirs()` creates `uploads/`, `generated/`, `logs/`.
- `get_settings()` returns a cached singleton.

### `backend/middleware/error_handler.py` — Error handling
Registers handlers that all produce the standard envelope
`{ "error", "detail", "code" }`:
- `StarletteHTTPException` → preserves status, `code = HTTP_<status>`.
- `RequestValidationError` → 422, `code = REQUEST_VALIDATION_ERROR`.
- `PermissionError` → 403, `code = ACCESS_DENIED` (used by path containment).
- `ValueError` → 422, `code = VALIDATION_ERROR`.
- Generic `Exception` → 500, sanitized message (no internals leaked); full
  traceback logged server-side.

### `backend/utils/file_utils.py`
- `resolve_managed_path(file_path)` — resolves a client-supplied path and
  confirms it lives inside `uploads/` or `generated/`. Raises `ValueError`
  (malformed) or `PermissionError` (escapes managed dirs). **Primary defense
  against path traversal.**
- `format_file_size(bytes)` — human-readable size.
- File-saving helpers used by the upload router.

### `backend/services/pipeline.py`
- `generate_deployment_package(req, onnx_path=None)` — renders server + Docker,
  resolves the ONNX artifact via `_find_onnx_artifact(model_id)` when not
  supplied, packages everything into a ZIP, and honors `include_readme` /
  `include_docker`.
- `_find_onnx_artifact(model_id)` — locates `generated/<model_id>/*.onnx`.

---

## 8. Complete API Reference

Base URL: `http://localhost:8000`. All endpoints return JSON. Errors use the
envelope `{ "error": str, "detail": str|null, "code": str|null }`.

### System

#### `GET /health`
Liveness probe.
```json
{ "status": "healthy", "version": "1.0.0", "uptime_seconds": 12.34 }
```

#### `GET /info`
Platform capabilities.
```json
{
  "name": "UniML",
  "version": "1.0.0",
  "python_version": "3.11.x",
  "supported_frameworks": ["pytorch", "tensorflow", "sklearn", "onnx"],
  "supported_extensions": [".pt", ".pth", ".pkl", ".joblib", ".h5", ".keras", ".onnx"],
  "max_upload_size_mb": 500
}
```

### Pipeline

#### `POST /api/v1/upload`  *(multipart/form-data)*
Field: `file`. Saves the file and returns:
```json
{
  "model_id": "3f2c…",
  "filename": "model.pkl",
  "file_size_bytes": 1048576,
  "file_size_human": "1.0 MB",
  "upload_time": "2026-07-24T20:00:00Z",
  "file_path": "/abs/path/uploads/3f2c…/model.pkl",
  "status": "uploaded"
}
```
Errors: `400` empty file, `413` too large, `415` unsupported extension.

#### `POST /api/v1/detect`
```json
// request
{ "file_path": "/abs/path/uploads/3f2c…/model.pkl" }
// response
{ "model_id": "", "framework": "sklearn", "confidence": 0.95, "details": "…", "status": "detected" }
```
Errors: `400` invalid path, `403` path outside managed dirs, `404` not found.

#### `POST /api/v1/validate`
```json
// request
{ "file_path": "…/model.pkl" }
// response
{
  "model_id": "",
  "framework": "sklearn",
  "is_valid": true,
  "issues": [ { "severity": "warning", "code": "NO_INPUT_SHAPE", "message": "…" } ],
  "input_shape": [null, 4],
  "output_shape": [null, 3],
  "model_class": "RandomForestClassifier",
  "parameters": 12345,
  "status": "validated"
}
```

#### `POST /api/v1/convert`
```json
// request  — pass BOTH the file_path and the model_id from /upload
{ "file_path": "…/model.pkl", "model_id": "3f2c…" }
// response
{
  "model_id": "3f2c…",
  "conversion_status": "success",     // success | skipped | failed | unsupported
  "original_format": "sklearn",
  "onnx_path": "…/generated/3f2c…/model.onnx",
  "onnx_size_bytes": 524288,
  "onnx_size_human": "512.0 KB",
  "error_message": null,
  "status": "converted"
}
```

#### `POST /api/v1/benchmark`
Runs inference timing on a model path (client-supplied `file_path`, subject to
the same path containment). Returns latency/throughput metrics.

#### `POST /api/v1/generate`
```json
// request
{
  "model_id": "3f2c…",
  "project_name": "ml_inference_server",
  "host": "0.0.0.0",
  "port": 8080,
  "include_docker": true,
  "include_readme": true
}
// response
{
  "model_id": "3f2c…",
  "project_name": "ml_inference_server",
  "zip_path": "…/generated/3f2c…/ml_inference_server.zip",
  "zip_size_bytes": 2097152,
  "zip_size_human": "2.0 MB",
  "files_generated": ["main.py", "predict.py", "config.py", "requirements.txt", "README.md", "Dockerfile", "…"],
  "status": "ready"
}
```

#### `GET /api/v1/download/{model_id}`
Streams the generated ZIP as a file download (`FileResponse`).

### Stats *(simulated data — see §20)*

#### `GET /api/v1/stats`
```json
{
  "generated_models_count": 3,
  "total_storage_bytes": 12582912,
  "pipelines": [ { "name": "…", "status": "…", "throughput": 42 } ],
  "gpu_compute_load": 37.5
}
```
`pipelines` and `gpu_compute_load` are randomized/mock.

#### `GET /api/v1/metrics`
```json
{
  "throughput": 128,
  "latency_p95": 24.7,
  "error_rate": 0.12,
  "resources": { "cpu": 41, "gpu": 63, "memory": 58 },
  "log": "…"
}
```
All fields are simulated.

---

## 9. Data Model & Enums

Defined in `models/enums.py`:

| Enum | Values |
|------|--------|
| `MLFramework` | `pytorch`, `tensorflow`, `sklearn`, `onnx`, `unknown` |
| `ModelStatus` | `uploaded`, `detected`, `validated`, `converting`, `converted`, `benchmarked`, `generating`, `ready`, `failed` |
| `ConversionStatus` | `success`, `skipped`, `failed`, `unsupported` |
| `ValidationSeverity` | `info`, `warning`, `error`, `critical` |

Key Pydantic schemas (`models/schemas.py`): `UploadResponse`,
`DetectionResult`, `ValidationResult` (+ `ValidationIssue`), `ConversionResult`,
`GenerationRequest`, `GenerationResult`, `HealthResponse`, `ErrorResponse`.

---

## 10. Model Conversion Engine

### Detection — `converter/detector.py`
`detect_framework(path)` returns a `DetectionResult` with a `framework` and
`confidence`, using file extension and content signatures.

### Conversion — `converter/onnx_converter.py`
`convert_to_onnx(file_path, model_id)`:
- If already ONNX → `SKIPPED` (copies/points to the file).
- Finds a handler via the registry; if none → `UNSUPPORTED`.
- If the handler's library isn't installed → `UNSUPPORTED` with a clear message.
- Writes ONNX to `generated/<model_id or stem>/<stem>.onnx`; returns `SUCCESS`
  with sizes, or `FAILED` with the error message on exception.

### Handlers — `converter/handlers/`
A **Strategy pattern**. Each handler implements the `FrameworkHandler` protocol
(`base.py`): `can_handle(path)`, `is_available()`, `framework_name`,
`convert_to_onnx(src, dst)`. Registry (`__init__.py`) is ordered by detection
priority:

```
ALL_HANDLERS = [ OnnxHandler(), PyTorchHandler(), TensorFlowHandler(), SklearnHandler() ]
find_handler(path) → first handler whose can_handle() returns True
```

---

## 11. Deployment Package Generator

`generator/` renders a complete, runnable inference server from Jinja2 templates:

- **`api_generator.generate_api_server(...)`** — renders `main.py`, `predict.py`,
  `config.py`, `requirements.txt`, and (when `include_readme`) `README.md`.
- **`docker_generator.generate_docker_files(...)`** — renders `Dockerfile` and
  `docker-compose.yml` when `include_docker` is set.
- **`zip_packager.create_zip_package(...)`** — bundles all generated files **and
  the converted ONNX model** (packaged as `model.onnx`) into a single ZIP.

The generated server loads its model from `MODEL_PATH` (env var, default
`model.onnx`) so the packaged path is correct regardless of the host source path.
The generated server's CORS is configured with `allow_credentials=False` under a
wildcard origin (spec-correct).

---

## 12. Frontend Reference

A React + Vite single-page app in `web/`, built to `web/dist` and served by
FastAPI. Development uses the Vite dev server (port 5173) with a proxy to the
backend.

### Entry & routing
- `src/main.jsx` — mounts `<App/>` inside `BrowserRouter`, `ToastProvider`, and
  `PipelineProvider`.
- `src/App.jsx` — routes: `/` (Dashboard), `/upload`, `/inspect`, `/convert`,
  `/deploy`, `/monitoring`, `*` (NotFound). The pipeline routes are wrapped in
  `RequireModel`, which redirects to `/upload` when no model is loaded.

### State management (`src/context/`)
- **`PipelineContext`** — tracks the active model as it moves through the
  pipeline (`upload`, `detection`, `validation`, `conversion`, `generation`).
  Persisted to `localStorage` so a refresh doesn't lose progress. Exposes
  `modelId`, `filePath`, `hasUpload`, and setters. A new upload resets everything
  downstream.
- **`ToastContext`** — `toast.success/error/info/warning`, renders `<Toaster/>`.

### Data fetching
- **`hooks/useFetch.js`** — fetch-on-mount with `{ data, error, loading, refetch }`
  and `AbortController` cleanup.
- **`lib/api.js`** — centralized client with an `ApiError` type. Methods:
  `health`, `info`, `stats`, `metrics`, `upload`, `detect`, `validate`,
  `convert`, `generate`, `downloadUrl`.

### Pages (`src/pages/`)
- **Dashboard** — KPIs from `/stats` + `/info`, pipeline quick-start, supported
  frameworks and limits.
- **Upload** — drag/drop dropzone with client-side extension + size validation
  from `/info`; security callout for pickle/PyTorch files.
- **Inspect** — auto-runs `/detect` then `/validate`; shows framework,
  confidence meter, model structure, and a severity-sorted validation report.
- **Convert** — runs `/convert` (threads the real `model_id`); shows status,
  original vs ONNX size, and size delta.
- **Deploy** — validated config form (project name, host, port, include Docker,
  include README) → `/generate` → file list → **Download .zip**.
- **Monitoring** — polls `/metrics` every 3s, renders KPIs, a dependency-free
  SVG sparkline, resource bars, and a live log. Clearly labeled as simulated.
- **NotFound** — 404 with a link home.

### Component library (`src/components/`)
- **ui/** — `Button` (variants + loading + icons, 44px touch target), `Card`
  (+ Header/Body/Footer), `Badge`, `Spinner`, `ProgressBar` (determinate +
  indeterminate), `StatCard`, `Skeleton`, `EmptyState`, `Modal` (portal + Escape
  + scroll lock), `Field` (`Input`, `Select`, `Switch`), `Toaster`, `Tooltip`.
- **common/** — `FrameworkBadge` (per-framework colors), `ConfidenceMeter`,
  `Sparkline` (SVG, no chart dependency).
- **layout/** — `AppLayout` (fixed sidebar + responsive mobile drawer), `Sidebar`
  (nav + active-model summary + locked pipeline links), `Topbar` (health pill
  polling `/health`, upload CTA), `PageHeader`, `nav.js` (nav + step config).
- **pipeline/** — `PipelineStepper` (4-stage wizard header with completion
  state), `FileDropzone` (keyboard + drag/drop + validation), `RequireModel`
  (route guard).

---

## 13. Design System

Generated with the UI/UX design intelligence tooling and tuned for a developer
tool: a **data-dense dashboard** aesthetic in a **slate + green** palette.

### Color tokens
Defined as `R G B` triplets in `src/index.css` and mapped in
`tailwind.config.js` via `rgb(var(--token) / <alpha-value>)` so every color
supports opacity modifiers.

| Token | Hex | Use |
|-------|-----|-----|
| `--bg` | `#0F172A` | app background |
| `--surface` | `#1E293B` | cards / panels |
| `--surface-2` | `#272F42` | insets / muted surfaces |
| `--surface-3` | `#334155` | controls |
| `--border` / `--border-strong` | subtle / `#475569` | hairlines / borders |
| `--fg` | `#F8FAFC` | primary text |
| `--muted-fg` | `#94A3B8` | secondary text |
| `--primary` | `#22C55E` | primary actions (convert/deploy/download) |
| `--info` | `#38BDF8` | informational |
| `--warning` | `#F59E0B` | warnings |
| `--danger` | `#EF4444` | errors / destructive |
| framework colors | torch orange, tf orange, sklearn sky, onnx indigo | framework badges |

### Typography
- **Fira Sans** — body and headings.
- **Fira Code** — metrics, numbers, code, and eyebrow labels (`.metric`,
  `.eyebrow` utilities).

### Spacing, radius, motion
- 4/8px spacing scale (Tailwind default), radii `lg`/`xl`/`2xl`.
- Transitions in the 150–300ms range with custom easings; **respects
  `prefers-reduced-motion`** (animations reduced to near-zero).

### Accessibility baseline
- Visible focus rings via `:focus-visible`.
- 44×44px minimum touch targets on primary controls.
- ARIA roles/labels on interactive components (switch, progressbar, dialog,
  tooltip, toasts with `aria-live`).
- WCAG AA contrast target for body text.

---

## 14. Security Model

- **Path containment** — endpoints that accept a client-supplied `file_path`
  (`/detect`, `/validate`, `/convert`, `/benchmark`) resolve the path via
  `resolve_managed_path()` and reject anything outside `uploads/` or
  `generated/` with `403`. Prevents path traversal / arbitrary file reads.
- **Upload hardening** — extension allow-list, size limit (default 500 MB),
  directory components stripped, saved into a per-upload UUID directory.
- **Untrusted models** — loading `.pkl` / `.joblib` / PyTorch files can execute
  arbitrary code during deserialization (inherent to those formats). **Only
  process models you trust**; run untrusted input in an isolated sandbox with no
  secrets and no outbound network. The Upload page surfaces this warning.
- **Error isolation** — all exceptions funnel through a global handler that logs
  full tracebacks server-side and returns a sanitized `{error, detail, code}`
  envelope.
- **CORS** — credentials enabled only with an explicit origin allow-list; a
  wildcard origin disables credentials (spec-compliant).
- **No built-in authentication** — the API is unauthenticated. This is fine for
  local use; **add authentication/authorization before any shared or production
  deployment.**

---

## 15. Configuration & Environment Variables

All settings load from environment variables prefixed **`UNIML_`** (or a `.env`
file in the project root). Defaults live in `backend/config.py`.

| Variable | Default | Description |
|----------|---------|-------------|
| `UNIML_APP_NAME` | `UniML` | Application name |
| `UNIML_APP_VERSION` | `1.0.0` | Version string |
| `UNIML_DEBUG` | `false` | Debug flag |
| `UNIML_HOST` | `0.0.0.0` | Bind host |
| `UNIML_PORT` | `8000` | Bind port |
| `UNIML_CORS_ORIGINS` | `["*"]` | Allowed origins (credentials off if `*`) |
| `UNIML_UPLOAD_DIR` | `./uploads` | Upload storage |
| `UNIML_GENERATED_DIR` | `./generated` | Generated artifacts |
| `UNIML_LOG_DIR` | `./logs` | Log directory |
| `UNIML_MAX_UPLOAD_SIZE_MB` | `500` | Max upload size |
| `UNIML_ALLOWED_EXTENSIONS` | `.pt,.pth,.pkl,.joblib,.h5,.keras,.onnx` | Accepted file types |
| `UNIML_DELETE_RAW_AFTER_CONVERT` | `false` | Delete raw upload after conversion (off so benchmark/re-validate keep working) |
| `UNIML_LOG_LEVEL` | `INFO` | Log level |
| `UNIML_LOG_ROTATION` | `10 MB` | Log rotation size |
| `UNIML_LOG_RETENTION` | `30 days` | Log retention |

---

## 16. Setup & Installation

### Prerequisites
- Python 3.11+
- Node.js 18+ (to build the dashboard)

### Backend
```bash
python -m venv .venv
# Windows:  .\.venv\Scripts\activate
# Unix:     source .venv/bin/activate
pip install -r requirements.txt
```

### Frontend (build the dashboard)
```bash
cd web
npm install
npm run build      # outputs to web/dist
cd ..
```

---

## 17. Running the Application

### Production-style (single process serves API + dashboard)
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```
- Dashboard: <http://localhost:8000>
- API docs (Swagger): <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>

### Frontend development (hot reload)
Run both together:
```bash
# Terminal 1 — backend
uvicorn backend.main:app --reload --port 8000

# Terminal 2 — Vite dev server (proxies API to :8000)
cd web && npm run dev        # http://localhost:5173
```

---

## 18. Docker Deployment

`deployment/Dockerfile` is a **multi-stage** build:

1. **Stage 1 (node:20-slim)** — installs `web/` deps and runs `npm run build` to
   produce `web/dist`.
2. **Stage 2 (python:3.11-slim)** — installs Python deps, copies the app, and
   copies the built dashboard from stage 1 into `web/dist`.

```bash
# from the project root
docker build -f deployment/Dockerfile -t uniml:latest .
docker run -p 8000:8000 uniml:latest
# or:
docker compose -f deployment/docker-compose.yml up --build
```

A root `.dockerignore` excludes `node_modules`, virtualenvs, runtime data
(`uploads/`, `generated/`, `logs/`), and local env files from the build context.

---

## 19. Testing

The backend test suite lives in `tests/` and runs with **pytest**.

```bash
pytest -q            # run all tests
pytest tests/test_api.py -q
```

Coverage includes health/info endpoints, upload, framework detection (including
a **path-traversal rejection** test asserting `403` for out-of-bounds paths),
and the converter/detector logic. As of the last run: **29 passed**.

> On Windows PowerShell, if terminal stdout is not surfaced, redirect to a file
> (`pytest ... > out.txt 2>&1`) and read it — the shell may report a misleading
> exit code even when tests pass.

---

## 20. Known Limitations & Simulated Data

- **`/api/v1/stats` and `/api/v1/metrics` return simulated data.** The
  `pipelines`, `gpu_compute_load`, throughput, latency, error rate, and resource
  figures are randomized on the backend. The Monitoring page labels this openly.
  Wire these to a real serving/telemetry stack for production observability.
- **No authentication** on the API (see §14).
- **No persistent database** — state is on disk and the client carries the
  `model_id`. Restarting does not lose generated artifacts, but there is no
  server-side index of jobs.
- **Conversion coverage** depends on installed optional libraries and each
  framework's ONNX export support; some exotic architectures may report
  `failed` or `unsupported`.
- **`frontend/static/`** is the legacy UI, retained only as a fallback; the
  active dashboard is the React app in `web/` (served from `web/dist`).

---

## 21. Change Log (This Engagement)

### Backend hardening
- Added the missing `ErrorResponse` schema and wired global exception handlers
  (previously `error_handler.py` referenced an undefined `ErrorResponse`, which
  would crash on any error). All errors now return `{error, detail, code}`.
- Added **path containment** (`resolve_managed_path`) and applied it to
  client-supplied `file_path` endpoints → traversal now returns `403`.
- Fixed CORS: `allow_credentials` is disabled under a wildcard origin.
- Gated raw-upload deletion behind `UNIML_DELETE_RAW_AFTER_CONVERT` (default
  off) so convert-then-benchmark no longer breaks.
- Fixed the deployment generator so the **ONNX model is actually included** in
  the ZIP (previously `onnx_path` was never passed, producing a package that
  referenced a missing `model.onnx`). Added `include_readme` support end to end.
- Fixed the generated server template's CORS (`allow_credentials=False`).

### Documentation & tests
- Synced `README.md`, `docs/architecture.md`, `docs/user_guide.md` with reality
  (removed the obsolete Streamlit references; added a Security Model section).
- Removed the unused `streamlit` dependency from `requirements.txt`.
- Updated detect tests to exercise the real upload flow and added a
  path-traversal rejection test. Full suite: **29 passed**.

### Frontend redesign
- Replaced the disconnected static mockup with a production **React + Vite +
  Tailwind** SPA organized around the real pipeline, with a reusable component
  library, design system, responsive layout, and accessibility baseline.
- Threaded the real `model_id` through convert → generate → download (the old
  client sent an empty `model_id`, which broke the pipeline).
- Updated `backend/main.py` to serve `web/dist` with a client-side routing
  fallback; updated the Dockerfile to a multi-stage build and added
  `.dockerignore`.

---

## 22. Troubleshooting

| Symptom | Cause / Fix |
|---------|-------------|
| Dashboard shows a blank page or 404 at `/` | `web/dist` not built. Run `cd web && npm install && npm run build`. |
| "API offline" pill in the top bar | Backend not running on port 8000, or reached from a different origin. Start `uvicorn backend.main:app --port 8000`. |
| `403` from detect/validate/convert | The `file_path` is outside `uploads/`/`generated/`. Use the `file_path` returned by `/upload`. |
| `415` on upload | File extension not in the allow-list (see `UNIML_ALLOWED_EXTENSIONS`). |
| Conversion returns `unsupported` | The framework's converter library isn't installed, or the format has no handler. Install the relevant optional dependency. |
| Generated ZIP missing the model | Ensure `/convert` ran with the same `model_id` used for `/generate`. |
| `npm` blocked by PowerShell execution policy | Invoke `npm.cmd` directly, or adjust the execution policy for your shell. |
| Deep link (e.g. `/deploy`) 404s on refresh in production | Ensure you're running the FastAPI server (which has the SPA fallback), not a bare static file server. |

---

*This document describes UniML v1.0.0. Generated as a complete project reference.*
