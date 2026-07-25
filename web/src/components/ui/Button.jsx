import { forwardRef } from 'react'
import { Loader2 } from 'lucide-react'
import { cn } from '../../lib/cn.js'

const VARIANTS = {
  primary:
    'bg-primary text-primary-fg hover:bg-primary/90 active:bg-primary/80 shadow-sm font-semibold',
  secondary:
    'bg-surface-3 text-foreground hover:bg-surface-3/80 active:bg-surface-3/70 border border-border-strong/50',
  outline:
    'border border-border-strong text-foreground hover:bg-surface-2 active:bg-surface-3',
  ghost: 'text-muted hover:text-foreground hover:bg-surface-2',
  danger: 'bg-danger text-white hover:bg-danger/90 active:bg-danger/80 font-semibold',
}

const SIZES = {
  sm: 'h-9 px-3 text-sm gap-1.5',
  md: 'h-11 px-4 text-sm gap-2', // 44px tall — meets touch-target guidance
  lg: 'h-12 px-6 text-base gap-2',
  icon: 'h-11 w-11 p-0',
}

const Button = forwardRef(function Button(
  {
    as: Comp = 'button',
    variant = 'primary',
    size = 'md',
    loading = false,
    icon: Icon,
    iconRight: IconRight,
    className,
    children,
    disabled,
    ...props
  },
  ref,
) {
  const isDisabled = disabled || loading
  return (
    <Comp
      ref={ref}
      disabled={Comp === 'button' ? isDisabled : undefined}
      aria-disabled={isDisabled || undefined}
      aria-busy={loading || undefined}
      className={cn(
        'inline-flex items-center justify-center rounded-lg font-sans transition-colors duration-150',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-background',
        'disabled:pointer-events-none disabled:opacity-50 select-none whitespace-nowrap',
        VARIANTS[variant],
        SIZES[size],
        className,
      )}
      {...props}
    >
      {loading ? (
        <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
      ) : (
        Icon && <Icon className="h-4 w-4 shrink-0" aria-hidden="true" />
      )}
      {children && <span className={size === 'icon' ? 'sr-only' : undefined}>{children}</span>}
      {IconRight && !loading && <IconRight className="h-4 w-4 shrink-0" aria-hidden="true" />}
    </Comp>
  )
})

export default Button
