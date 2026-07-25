import { cn } from '../../lib/cn.js'

const TONE_BG = {
  primary: 'bg-primary',
  info: 'bg-info',
  warning: 'bg-warning',
  danger: 'bg-danger',
}

export function ProgressBar({
  value = 0,
  tone = 'primary',
  indeterminate = false,
  className,
  showLabel = false,
}) {
  const pct = Math.max(0, Math.min(100, value))
  return (
    <div className={cn('flex items-center gap-3', className)}>
      <div
        className="relative h-2 flex-1 overflow-hidden rounded-full bg-surface-3/70"
        role="progressbar"
        aria-valuenow={indeterminate ? undefined : Math.round(pct)}
        aria-valuemin={0}
        aria-valuemax={100}
      >
        {indeterminate ? (
          <div className="absolute inset-y-0 left-0 w-1/3 animate-[shimmer_1.2s_infinite] rounded-full bg-primary" />
        ) : (
          <div
            className={cn('h-full rounded-full transition-[width] duration-500 ease-out', TONE_BG[tone])}
            style={{ width: `${pct}%` }}
          />
        )}
      </div>
      {showLabel && !indeterminate && (
        <span className="metric w-10 text-right text-xs text-muted">{Math.round(pct)}%</span>
      )}
    </div>
  )
}
