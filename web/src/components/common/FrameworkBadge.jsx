import { cn } from '../../lib/cn.js'
import { frameworkMeta } from '../../lib/constants.js'

// Colored pill for an ML framework. Uses per-framework token colors.
export function FrameworkBadge({ framework, className }) {
  const meta = frameworkMeta(framework)
  const colorClass = {
    'framework-pytorch': 'bg-framework-pytorch/15 text-framework-pytorch border-framework-pytorch/30',
    'framework-tensorflow': 'bg-framework-tensorflow/15 text-framework-tensorflow border-framework-tensorflow/30',
    'framework-sklearn': 'bg-framework-sklearn/15 text-framework-sklearn border-framework-sklearn/30',
    'framework-onnx': 'bg-framework-onnx/15 text-framework-onnx border-framework-onnx/30',
    muted: 'bg-surface-3/60 text-muted border-border-strong/40',
  }[meta.color]

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-semibold',
        colorClass,
        className,
      )}
    >
      <span className="h-1.5 w-1.5 rounded-full bg-current" aria-hidden="true" />
      {meta.label}
    </span>
  )
}
