// Shared vocab aligned with the backend enums (models/enums.py).

export const FRAMEWORK_META = {
  pytorch: { label: 'PyTorch', color: 'framework-pytorch', ext: '.pt / .pth' },
  tensorflow: { label: 'TensorFlow', color: 'framework-tensorflow', ext: '.h5 / .keras' },
  sklearn: { label: 'scikit-learn', color: 'framework-sklearn', ext: '.pkl / .joblib' },
  onnx: { label: 'ONNX', color: 'framework-onnx', ext: '.onnx' },
  unknown: { label: 'Unknown', color: 'muted', ext: '—' },
}

export function frameworkMeta(fw) {
  return FRAMEWORK_META[fw] || FRAMEWORK_META.unknown
}

// Maps ConversionStatus -> badge tone.
export const CONVERSION_TONE = {
  success: 'success',
  skipped: 'info',
  failed: 'danger',
  unsupported: 'warning',
}

// Maps ValidationSeverity -> badge tone.
export const SEVERITY_TONE = {
  info: 'info',
  warning: 'warning',
  error: 'danger',
  critical: 'danger',
}

export const SEVERITY_ORDER = { critical: 0, error: 1, warning: 2, info: 3 }
