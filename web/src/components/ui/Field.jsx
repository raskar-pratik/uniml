import { useId } from 'react'
import { cn } from '../../lib/cn.js'

const baseControl =
  'w-full rounded-lg border border-border-strong/60 bg-surface-2 px-3 text-sm text-foreground ' +
  'placeholder:text-muted/70 transition-colors duration-150 ' +
  'focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/40 ' +
  'disabled:cursor-not-allowed disabled:opacity-60'

function Label({ htmlFor, children, hint }) {
  return (
    <div className="mb-1.5 flex items-center justify-between">
      <label htmlFor={htmlFor} className="text-sm font-medium text-foreground">
        {children}
      </label>
      {hint && <span className="text-xs text-muted">{hint}</span>}
    </div>
  )
}

export function Input({ label, hint, error, prefix, className, id, ...props }) {
  const autoId = useId()
  const fieldId = id || autoId
  return (
    <div>
      {label && <Label htmlFor={fieldId} hint={hint}>{label}</Label>}
      <div className="relative flex items-center">
        {prefix && (
          <span className="pointer-events-none absolute left-3 font-mono text-sm text-muted">
            {prefix}
          </span>
        )}
        <input
          id={fieldId}
          className={cn(baseControl, 'h-11', prefix && 'pl-9', error && 'border-danger focus:border-danger focus:ring-danger/40', className)}
          aria-invalid={error ? 'true' : undefined}
          {...props}
        />
      </div>
      {error && <p className="mt-1 text-xs text-danger">{error}</p>}
    </div>
  )
}

export function Select({ label, hint, error, className, id, children, ...props }) {
  const autoId = useId()
  const fieldId = id || autoId
  return (
    <div>
      {label && <Label htmlFor={fieldId} hint={hint}>{label}</Label>}
      <select
        id={fieldId}
        className={cn(baseControl, 'h-11 appearance-none bg-[length:1rem] pr-9', className)}
        style={{
          backgroundImage:
            "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='none' stroke='%2394A3B8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m4 6 4 4 4-4'/%3E%3C/svg%3E\")",
          backgroundRepeat: 'no-repeat',
          backgroundPosition: 'right 0.75rem center',
        }}
        {...props}
      >
        {children}
      </select>
      {error && <p className="mt-1 text-xs text-danger">{error}</p>}
    </div>
  )
}

export function Switch({ checked, onChange, label, description, id, disabled }) {
  const autoId = useId()
  const fieldId = id || autoId
  return (
    <label
      htmlFor={fieldId}
      className={cn(
        'flex items-center justify-between gap-4 rounded-lg border border-border bg-surface-2/50 p-3',
        disabled ? 'opacity-60' : 'cursor-pointer',
      )}
    >
      <span className="min-w-0">
        <span className="block text-sm font-medium text-foreground">{label}</span>
        {description && <span className="mt-0.5 block text-xs text-muted">{description}</span>}
      </span>
      <button
        id={fieldId}
        type="button"
        role="switch"
        aria-checked={checked}
        disabled={disabled}
        onClick={() => onChange?.(!checked)}
        className={cn(
          'relative inline-flex h-6 w-11 shrink-0 items-center rounded-full transition-colors duration-200',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-surface',
          checked ? 'bg-primary' : 'bg-surface-3',
        )}
      >
        <span
          className={cn(
            'inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform duration-200',
            checked ? 'translate-x-6' : 'translate-x-1',
          )}
        />
      </button>
    </label>
  )
}
