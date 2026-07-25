import { cn } from '../../lib/cn.js'

export function Skeleton({ className }) {
  return (
    <div
      className={cn(
        'relative overflow-hidden rounded-md bg-surface-3/50',
        'after:absolute after:inset-0 after:-translate-x-full after:animate-shimmer',
        'after:bg-gradient-to-r after:from-transparent after:via-white/5 after:to-transparent',
        className,
      )}
      aria-hidden="true"
    />
  )
}
