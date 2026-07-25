// Centralized API client for the UniML backend.
// In dev, Vite proxies these paths to http://localhost:8000.
// In prod, the SPA is served by FastAPI so requests are same-origin.

export class ApiError extends Error {
  constructor(message, { status, code } = {}) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = code
  }
}

async function parseError(res) {
  // Backend returns a standard envelope: { error, detail, code }.
  // Fall back gracefully for non-JSON responses.
  let detail
  let code
  try {
    const body = await res.json()
    detail = body.detail || body.error
    code = body.code
  } catch {
    detail = await res.text().catch(() => res.statusText)
  }
  return new ApiError(detail || `Request failed (${res.status})`, {
    status: res.status,
    code,
  })
}

async function request(path, { method = 'GET', body, isForm = false, signal } = {}) {
  const headers = {}
  let payload = body
  if (body && !isForm) {
    headers['Content-Type'] = 'application/json'
    payload = JSON.stringify(body)
  }

  let res
  try {
    res = await fetch(path, { method, headers, body: payload, signal })
  } catch (err) {
    if (err.name === 'AbortError') throw err
    throw new ApiError('Network error — is the backend running on port 8000?', {
      status: 0,
    })
  }

  if (!res.ok) throw await parseError(res)
  if (res.status === 204) return null

  const contentType = res.headers.get('content-type') || ''
  if (contentType.includes('application/json')) return res.json()
  return res
}

export const api = {
  health: (signal) => request('/health', { signal }),
  info: (signal) => request('/info', { signal }),
  stats: (signal) => request('/api/v1/stats', { signal }),

  upload(file, { signal } = {}) {
    const form = new FormData()
    form.append('file', file)
    return request('/api/v1/upload', { method: 'POST', body: form, isForm: true, signal })
  },

  detect: (filePath, signal) =>
    request('/api/v1/detect', { method: 'POST', body: { file_path: filePath }, signal }),

  validate: (filePath, signal) =>
    request('/api/v1/validate', { method: 'POST', body: { file_path: filePath }, signal }),

  convert: (filePath, modelId, signal) =>
    request('/api/v1/convert', {
      method: 'POST',
      body: { file_path: filePath, model_id: modelId },
      signal,
    }),

  generate: (options, signal) =>
    request('/api/v1/generate', { method: 'POST', body: options, signal }),

  // The download endpoint streams a file; return the URL for a direct browser download.
  downloadUrl: (modelId) => `/api/v1/download/${encodeURIComponent(modelId)}`,
}
