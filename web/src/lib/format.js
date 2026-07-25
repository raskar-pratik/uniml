// Small pure formatting helpers shared across pages.

export function formatBytes(bytes, decimals = 1) {
  if (bytes == null || Number.isNaN(bytes)) return '—'
  if (bytes === 0) return '0 B'
  const k = 1024
  const units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
  const i = Math.min(Math.floor(Math.log(bytes) / Math.log(k)), units.length - 1)
  const value = bytes / Math.pow(k, i)
  return `${value.toFixed(i === 0 ? 0 : decimals)} ${units[i]}`
}

export function formatNumber(n) {
  if (n == null || Number.isNaN(n)) return '—'
  return new Intl.NumberFormat('en-US').format(n)
}

export function formatDuration(seconds) {
  if (seconds == null) return '—'
  const s = Math.floor(seconds % 60)
  const m = Math.floor((seconds / 60) % 60)
  const h = Math.floor((seconds / 3600) % 24)
  const d = Math.floor(seconds / 86400)
  const parts = []
  if (d) parts.push(`${d}d`)
  if (h) parts.push(`${h}h`)
  if (m) parts.push(`${m}m`)
  parts.push(`${s}s`)
  return parts.join(' ')
}

export function formatPercent(n, decimals = 0) {
  if (n == null || Number.isNaN(n)) return '—'
  return `${n.toFixed(decimals)}%`
}

export function shortId(id) {
  if (!id) return '—'
  return id.length > 10 ? `${id.slice(0, 8)}…` : id
}

// Turn a shape array like [null, 3, 224, 224] into "N × 3 × 224 × 224".
export function formatShape(shape) {
  if (!shape || !shape.length) return '—'
  return shape.map((d) => (d == null || d === -1 ? 'N' : d)).join(' × ')
}
