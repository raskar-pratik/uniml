import { cn } from '../../lib/cn.js'
import { Card } from './Card.jsx'
import { Skeleton } from './Skeleton.jsx'

export function StatCard({ label, value, unit, icon: Icon, tone = 'primary', hint, loading }) {
  const toneText = {
    primary: 'text-primary',
    info: 'text-info',
    warning: 'text-warning',
    danger: 'text-danger',
  }[tone]

  return (
    <Card className="p-5" hover>
      <div className="flex items-center justify-between">
        <span className="eyebrow">{label}</span>
        {Icon && (
          <span className={cn('grid h-8 w-8 place-items-center rounded-lg bg-surface-2', toneText)}>
            <Icon className="h-4 w-4" aria-hidden="true" />
          </span>
        )}
      </div>
      <div className="mt-3 flex items-baseline gap-1.5">
        {loading ? (
          <Skeleton className="h-9 w-24" />
        ) : (
          <>
            <span className="metric text-3xl font-bold text-foreground">{value}</span>
            {unit && <span className="metric text-sm text-muted">{unit}</span>}
          </>
        )}
      </div>
      {hint && <p className="mt-1 text-xs text-muted">{hint}</p>}
    </Card>
  )
}
