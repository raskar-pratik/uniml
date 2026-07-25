import { createPortal } from 'react-dom'
import { CheckCircle2, Info, TriangleAlert, XCircle, X } from 'lucide-react'
import { cn } from '../../lib/cn.js'

const CONFIG = {
  success: { icon: CheckCircle2, accent: 'border-l-primary text-primary' },
  error: { icon: XCircle, accent: 'border-l-danger text-danger' },
  warning: { icon: TriangleAlert, accent: 'border-l-warning text-warning' },
  info: { icon: Info, accent: 'border-l-info text-info' },
}

export function Toaster({ toasts, onDismiss }) {
  if (typeof document === 'undefined') return null
  return createPortal(
    <div
      className="pointer-events-none fixed inset-x-0 bottom-0 z-[200] flex flex-col items-center gap-2 p-4 sm:bottom-4 sm:right-4 sm:left-auto sm:items-end"
      aria-live="polite"
      aria-atomic="false"
    >
      {toasts.map((t) => {
        const { icon: Icon, accent } = CONFIG[t.type] || CONFIG.info
        return (
          <div
            key={t.id}
            role="status"
            className={cn(
              'pointer-events-auto flex w-full max-w-sm items-start gap-3 rounded-lg border border-l-4 border-border bg-surface-2 p-3 pr-2 shadow-card-hover',
              'animate-slide-in-right',
              accent,
            )}
          >
            <Icon className="mt-0.5 h-5 w-5 shrink-0" aria-hidden="true" />
            <p className="flex-1 py-0.5 text-sm text-foreground">{t.message}</p>
            <button
              onClick={() => onDismiss(t.id)}
              className="rounded p-1 text-muted transition-colors hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
              aria-label="Dismiss notification"
            >
              <X className="h-4 w-4" aria-hidden="true" />
            </button>
          </div>
        )
      })}
    </div>,
    document.body,
  )
}
