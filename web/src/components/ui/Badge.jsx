import { cn } from '../../lib/cn.js'

const TONES = {
  neutral: 'bg-surface-3/60 text-muted border-border-strong/40',
  success: 'bg-primary/15 text-primary border-primary/30',
  info: 'bg-info/15 text-info border-info/30',
  warning: 'bg-warning/15 text-warning border-warning/30',
  danger: 'bg-danger/15 text-danger border-danger/30',
}

export function Badge({ tone = 'neutral', dot = false, icon: Icon, className, children }) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-medium',
        TONES[tone] || TONES.neutral,
        className,
      )}
    >
      {dot && <span className="h-1.5 w-1.5 rounded-full bg-current" aria-hidden="true" />}
      {Icon && <Icon className="h-3.5 w-3.5" aria-hidden="true" />}
      {children}
    </span>
  )
}
