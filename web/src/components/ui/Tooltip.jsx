import { cn } from '../../lib/cn.js'

// Lightweight CSS-only tooltip. Content is also exposed via aria-label on the
// trigger wrapper so it is accessible without hover.
export function Tooltip({ label, side = 'top', children, className }) {
  const pos = {
    top: 'bottom-full left-1/2 -translate-x-1/2 mb-2',
    bottom: 'top-full left-1/2 -translate-x-1/2 mt-2',
    left: 'right-full top-1/2 -translate-y-1/2 mr-2',
    right: 'left-full top-1/2 -translate-y-1/2 ml-2',
  }[side]

  return (
    <span className={cn('group/tt relative inline-flex', className)}>
      {children}
      <span
        role="tooltip"
        className={cn(
          'pointer-events-none absolute z-50 whitespace-nowrap rounded-md border border-border bg-surface-3 px-2 py-1 text-xs text-foreground shadow-card',
          'opacity-0 transition-opacity duration-150 group-hover/tt:opacity-100 group-focus-within/tt:opacity-100',
          pos,
        )}
      >
        {label}
      </span>
    </span>
  )
}
