import { useCallback, useRef, useState } from 'react'
import { UploadCloud, FileBox } from 'lucide-react'
import { cn } from '../../lib/cn.js'
import { formatBytes } from '../../lib/format.js'

export function FileDropzone({ accept = [], maxSizeMb, disabled, onFile, selectedFile }) {
  const inputRef = useRef(null)
  const [dragging, setDragging] = useState(false)
  const [error, setError] = useState(null)

  const acceptAttr = accept.join(',')

  const validate = useCallback(
    (file) => {
      setError(null)
      const ext = '.' + file.name.split('.').pop().toLowerCase()
      if (accept.length && !accept.includes(ext)) {
        setError(`Unsupported file type "${ext}". Allowed: ${accept.join(', ')}`)
        return false
      }
      if (maxSizeMb && file.size > maxSizeMb * 1024 * 1024) {
        setError(`File is ${formatBytes(file.size)} — exceeds the ${maxSizeMb} MB limit.`)
        return false
      }
      return true
    },
    [accept, maxSizeMb],
  )

  const handleFiles = useCallback(
    (files) => {
      const file = files?.[0]
      if (!file) return
      if (validate(file)) onFile?.(file)
    },
    [validate, onFile],
  )

  return (
    <div>
      <div
        role="button"
        tabIndex={disabled ? -1 : 0}
        aria-disabled={disabled}
        aria-label="Upload a model file. Click or drag and drop."
        onClick={() => !disabled && inputRef.current?.click()}
        onKeyDown={(e) => {
          if ((e.key === 'Enter' || e.key === ' ') && !disabled) {
            e.preventDefault()
            inputRef.current?.click()
          }
        }}
        onDragOver={(e) => {
          e.preventDefault()
          if (!disabled) setDragging(true)
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault()
          setDragging(false)
          if (!disabled) handleFiles(e.dataTransfer.files)
        }}
        className={cn(
          'flex flex-col items-center justify-center rounded-xl border-2 border-dashed px-6 py-12 text-center transition-colors duration-150',
          disabled
            ? 'cursor-not-allowed border-border bg-surface/40 opacity-60'
            : 'cursor-pointer',
          dragging
            ? 'border-primary bg-primary/10'
            : 'border-border-strong/60 bg-surface-2/40 hover:border-primary/50 hover:bg-surface-2',
        )}
      >
        <span
          className={cn(
            'mb-4 grid h-16 w-16 place-items-center rounded-2xl transition-colors',
            dragging ? 'bg-primary/20 text-primary' : 'bg-surface-2 text-muted',
          )}
        >
          {selectedFile ? <FileBox className="h-8 w-8" /> : <UploadCloud className="h-8 w-8" />}
        </span>

        {selectedFile ? (
          <div>
            <p className="font-medium text-foreground">{selectedFile.name}</p>
            <p className="metric mt-1 text-sm text-muted">{formatBytes(selectedFile.size)}</p>
            <p className="mt-2 text-xs text-primary">Click to choose a different file</p>
          </div>
        ) : (
          <div>
            <p className="font-medium text-foreground">
              Drag &amp; drop your model here, or <span className="text-primary">browse</span>
            </p>
            <p className="mt-1 text-sm text-muted">
              {accept.length ? accept.join(', ') : 'Any model file'}
              {maxSizeMb ? ` · up to ${maxSizeMb} MB` : ''}
            </p>
          </div>
        )}

        <input
          ref={inputRef}
          type="file"
          accept={acceptAttr}
          className="sr-only"
          disabled={disabled}
          onChange={(e) => {
            handleFiles(e.target.files)
            e.target.value = ''
          }}
        />
      </div>
      {error && (
        <p className="mt-2 text-sm text-danger" role="alert">
          {error}
        </p>
      )}
    </div>
  )
}
