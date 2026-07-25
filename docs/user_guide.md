# UniML User Guide

## Getting Started

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/UniML.git
   cd UniML
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Optional: Install full ML support**
   ```bash
   # PyTorch (CPU)
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
   
   # TensorFlow
   pip install tensorflow tf2onnx
   ```

5. **Build the dashboard** (React + Vite, requires Node.js 18+)
   ```bash
   cd web
   npm install
   npm run build
   cd ..
   ```

### Running UniML

A single process serves both the API and the compiled web dashboard:

```bash
uvicorn backend.main:app --reload --port 8000
```

Open your browser to **http://localhost:8000**. Interactive API documentation
is available at **http://localhost:8000/docs**.

> Working on the UI? Run `npm run dev` inside `web/` for a hot-reloading dev
> server on port 5173 that proxies API calls to the backend on port 8000.

---

## Workflow

### Step 1: Upload a Model

1. Navigate to the **Upload** page
2. Drag and drop your model file (`.pt`, `.pkl`, `.h5`, `.onnx`, etc.)
3. Click **Upload & Process**
4. The framework will be automatically detected

### Step 2: Validate & Convert

1. Go to the **Conversion** page
2. Click **Validate Model** to check integrity
3. Click **Convert to ONNX** to convert
4. Click **Run Benchmark** for performance metrics

### Step 3: Generate Deployment Package

1. Navigate to the **Deployment** page
2. Configure project name, host, and port
3. Click **Generate Deployment Package**

### Step 4: Download

1. Go to the **Download** page
2. Click the download button to get your ZIP
3. Follow the instructions to run locally or with Docker

---

## Supported Formats

| Extension | Framework | Notes |
|-----------|-----------|-------|
| `.pt`, `.pth` | PyTorch | Requires `torch` |
| `.h5`, `.keras` | TensorFlow/Keras | Requires `tensorflow` + `tf2onnx` |
| `.pkl` | Scikit-Learn | Always available |
| `.joblib` | Scikit-Learn | Always available |
| `.onnx` | ONNX | Always available, skips conversion |

---

## Tips

- **Check Settings page** to verify which frameworks are installed
- **View Logs** to debug any issues during processing
- **Conversion requires a fitted model** — sklearn models must have been `.fit()` before saving
- **PyTorch nn.Module required** — state dicts alone cannot be converted to ONNX
