# ── Stage 1: build the React dashboard ───────────────────────────────
FROM node:20-slim AS frontend
WORKDIR /web

# Install deps first for layer caching
COPY web/package.json web/package-lock.json* ./
RUN npm ci

# Build the SPA -> /web/dist
COPY web/ ./
RUN npm run build

# ── Stage 2: python runtime ───────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY requirements.txt requirements-convert.txt ./

# Core deps, then the conversion stack. torch is pulled from the CPU wheel index
# (no CUDA) to keep the image lean; the remaining convert deps come from PyPI.
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements-convert.txt

# Conversion runtime shims (separate layer so the heavy torch/TF layer above
# stays cached):
#   - onnxscript backs torch's ONNX exporter (torch>=2.x needs it at export time)
#   - tf-keras provides the Keras 2 API that tf2onnx requires; TF_USE_LEGACY_KERAS
#     makes `tf.keras` resolve to it (TensorFlow 2.16+ ships Keras 3, which
#     tf2onnx cannot consume).
# tf-keras is installed with --no-deps so it reuses the already-installed
# tensorflow-cpu instead of pulling the full ~600MB `tensorflow` meta-package.
RUN pip install --no-cache-dir onnxscript \
    && pip install --no-cache-dir --no-deps tf-keras
ENV TF_USE_LEGACY_KERAS=1

# Copy application code
COPY . .

# Bring in the compiled dashboard from the build stage
COPY --from=frontend /web/dist ./web/dist

# Create runtime directories
RUN mkdir -p uploads generated logs

# Expose the single port serving both the REST API and the built frontend
EXPOSE 8000

# Run the backend (also serves the dashboard at /)
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
