import { useEffect, useRef } from 'react'
import { createPortal } from 'react-dom'
import { X } from 'lucide-react'
import { cn } from '../../lib/cn.js'
import Button from './Button.jsx'

export function Modal({ open, onClose, title, description, children, footer, size = 'md' }) {
  const panelRef = useRef(null)

  useEffect(() => {
    if (!open) return
    const onKey = (e) => e.key === 'Escape' && onClose?.()
    document.addEventListener('keydown', onKey)
    const prevOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    panelRef.current?.focus()
    return () => {
      document.removeEventListener('keydown', onKey)
      document.body.style.overflow = prevOverflow
    }
  }, [open, onClose])

  if (!open) return null

  const width = { sm: 'max-w-sm', md: 'max-w-lg', lg: 'max-w-2xl' }[size]

  return createPortal(
    <div
      className="fixed inset-0 z-[100] flex items-end justify-center p-0 sm:items-center sm:p-4"
      role="dialog"
      aria-modal="true"
      aria-label={title}
    >
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm animate-fade-in"
        onClick={onClose}
        aria-hidden="true"
      />
      <div
        ref={panelRef}
        tabIndex={-1}
        className={cn(
          'relative w-full rounded-t-2xl sm:rounded-2xl border border-border bg-surface shadow-card-hover outline-none',
          'animate-slide-up',
          width,
        )}
      >
        <div className="flex items-start justify-between gap-4 p-5 pb-0">
          <div>
            {title && <h2 className="text-lg font-semibold text-foreground">{title}</h2>}
            {description && <p className="mt-1 text-sm text-muted">{description}</p>}
          </div>
          <Button variant="ghost" size="icon" onClick={onClose} icon={X} aria-label="Close dialog" />
        </div>
        <div className="p-5">{children}</div>
        {footer && (
          <div className="flex justify-end gap-3 border-t border-border px-5 py-4">{footer}</div>
        )}
      </div>
    </div>,
    document.body,
  )
}
