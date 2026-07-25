import { createContext, useCallback, useContext, useMemo, useRef, useState } from 'react'
import { Toaster } from '../components/ui/Toaster.jsx'

const ToastContext = createContext(null)

let idSeq = 0

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])
  const timers = useRef(new Map())

  const dismiss = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
    const timer = timers.current.get(id)
    if (timer) {
      clearTimeout(timer)
      timers.current.delete(id)
    }
  }, [])

  const push = useCallback(
    (message, { type = 'info', duration = 4000 } = {}) => {
      const id = ++idSeq
      setToasts((prev) => [...prev, { id, message, type }])
      if (duration) {
        timers.current.set(
          id,
          setTimeout(() => dismiss(id), duration),
        )
      }
      return id
    },
    [dismiss],
  )

  const toast = useMemo(
    () => ({
      info: (m, o) => push(m, { ...o, type: 'info' }),
      success: (m, o) => push(m, { ...o, type: 'success' }),
      error: (m, o) => push(m, { ...o, type: 'error', duration: 6000 }),
      warning: (m, o) => push(m, { ...o, type: 'warning' }),
      push,
      dismiss,
    }),
    [push, dismiss],
  )

  return (
    <ToastContext.Provider value={toast}>
      {children}
      <Toaster toasts={toasts} onDismiss={dismiss} />
    </ToastContext.Provider>
  )
}

export function useToast() {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error('useToast must be used within a ToastProvider')
  return ctx
}
