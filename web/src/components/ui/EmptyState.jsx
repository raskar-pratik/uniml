import { cn } from '../../lib/cn.js'

export function EmptyState({ icon: Icon, title, description, action, className }) {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center rounded-xl border border-dashed border-border-strong/50 bg-surface/40 px-6 py-12 text-center',
        className,
      )}
    >
      {Icon && (
        <span className="mb-4 grid h-14 w-14 place-items-center rounded-2xl bg-surface-2 text-muted">
          <Icon className="h-7 w-7" aria-hidden="true" />
        </span>
      )}
      {title && <h3 className="text-base font-semibold text-foreground">{title}</h3>}
      {description && <p className="mt-1 max-w-sm text-sm text-muted">{description}</p>}
      {action && <div className="mt-5">{action}</div>}
    </div>
  )
}
