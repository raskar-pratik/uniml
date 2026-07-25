import { Loader2 } from 'lucide-react'
import { cn } from '../../lib/cn.js'

export function Spinner({ className, size = 20, label = 'Loading' }) {
  return (
    <span role="status" aria-live="polite" className="inline-flex items-center gap-2">
      <Loader2
        className={cn('animate-spin text-primary', className)}
        style={{ width: size, height: size }}
        aria-hidden="true"
      />
      <span className="sr-only">{label}</span>
    </span>
  )
}
