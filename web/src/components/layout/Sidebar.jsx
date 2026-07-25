import { NavLink } from 'react-router-dom'
import { Boxes, Lock } from 'lucide-react'
import { cn } from '../../lib/cn.js'
import { NAV_ITEMS } from './nav.js'
import { usePipeline } from '../../context/PipelineContext.jsx'
import { Tooltip } from '../ui/Tooltip.jsx'

function NavItem({ item, onNavigate, locked }) {
  const Icon = item.icon
  const content = (
    <NavLink
      to={item.to}
      end={item.end}
      onClick={(e) => {
        if (locked) {
          e.preventDefault()
          return
        }
        onNavigate?.()
      }}
      aria-disabled={locked || undefined}
      className={({ isActive }) =>
        cn(
          'group relative flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors duration-150',
          locked
            ? 'cursor-not-allowed text-muted/50'
            : isActive
              ? 'bg-primary/10 text-primary'
              : 'text-muted hover:bg-surface-2 hover:text-foreground',
        )
      }
    >
      {({ isActive }) => (
        <>
          <span
            className={cn(
              'absolute left-0 top-1/2 h-5 w-0.5 -translate-y-1/2 rounded-full bg-primary transition-opacity',
              isActive && !locked ? 'opacity-100' : 'opacity-0',
            )}
            aria-hidden="true"
          />
          <Icon className="h-5 w-5 shrink-0" aria-hidden="true" />
          <span className="flex-1">{item.label}</span>
          {item.step && (
            <span className="metric text-[10px] text-muted/60">{`0${item.step}`}</span>
          )}
          {locked && <Lock className="h-3.5 w-3.5" aria-hidden="true" />}
        </>
      )}
    </NavLink>
  )

  return locked ? (
    <Tooltip label="Upload a model first" side="right" className="block">
      {content}
    </Tooltip>
  ) : (
    content
  )
}

export function SidebarContent({ onNavigate }) {
  const { hasUpload, upload } = usePipeline()

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center gap-2.5 px-5 py-5">
        <span className="grid h-9 w-9 place-items-center rounded-lg bg-primary text-primary-fg">
          <Boxes className="h-5 w-5" aria-hidden="true" />
        </span>
        <div className="leading-tight">
          <p className="text-base font-bold tracking-tight text-foreground">UniML</p>
          <p className="eyebrow">Deploy Studio</p>
        </div>
      </div>

      <nav className="flex-1 space-y-1 px-3 py-2" aria-label="Primary">
        {NAV_ITEMS.map((item) => (
          <NavItem
            key={item.to}
            item={item}
            onNavigate={onNavigate}
            locked={item.requiresModel && !hasUpload}
          />
        ))}
      </nav>

      <div className="border-t border-border p-3">
        {hasUpload ? (
          <div className="rounded-lg bg-surface-2 p-3">
            <p className="eyebrow mb-1">Active model</p>
            <p className="truncate text-sm font-medium text-foreground" title={upload.filename}>
              {upload.filename}
            </p>
            <p className="metric mt-0.5 text-xs text-muted">{upload.fileSizeHuman}</p>
          </div>
        ) : (
          <div className="rounded-lg border border-dashed border-border-strong/50 p-3 text-center">
            <p className="text-xs text-muted">No model loaded</p>
          </div>
        )}
      </div>
    </div>
  )
}
