import { cn } from '../../lib/cn.js'

export function Card({ className, hover = false, children, ...props }) {
  return (
    <div
      className={cn(
        'card',
        hover && 'transition-shadow duration-200 hover:shadow-card-hover',
        className,
      )}
      {...props}
    >
      {children}
    </div>
  )
}

export function CardHeader({ className, title, subtitle, icon: Icon, action, children }) {
  return (
    <div className={cn('flex items-start justify-between gap-4 p-5 pb-0', className)}>
      <div className="flex items-start gap-3 min-w-0">
        {Icon && (
          <span className="mt-0.5 grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-surface-2 text-primary">
            <Icon className="h-5 w-5" aria-hidden="true" />
          </span>
        )}
        <div className="min-w-0">
          {title && <h3 className="truncate text-base font-semibold text-foreground">{title}</h3>}
          {subtitle && <p className="mt-0.5 text-sm text-muted">{subtitle}</p>}
          {children}
        </div>
      </div>
      {action && <div className="shrink-0">{action}</div>}
    </div>
  )
}

export function CardBody({ className, children }) {
  return <div className={cn('p-5', className)}>{children}</div>
}

export function CardFooter({ className, children }) {
  return (
    <div className={cn('flex items-center gap-3 border-t border-border px-5 py-4', className)}>
      {children}
    </div>
  )
}
