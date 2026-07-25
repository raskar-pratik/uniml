import { ProgressBar } from '../ui/ProgressBar.jsx'

// Renders a 0..1 detection confidence as a labeled meter.
export function ConfidenceMeter({ value }) {
  const pct = Math.round((value ?? 0) * 100)
  const tone = pct >= 80 ? 'primary' : pct >= 50 ? 'info' : 'warning'
  return (
    <div className="w-full">
      <div className="mb-1 flex items-center justify-between text-xs">
        <span className="text-muted">Detection confidence</span>
        <span className="metric font-semibold text-foreground">{pct}%</span>
      </div>
      <ProgressBar value={pct} tone={tone} />
    </div>
  )
}
