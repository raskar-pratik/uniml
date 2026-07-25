import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Menu, UploadCloud, CircleDot } from 'lucide-react'
import Button from '../ui/Button.jsx'
import { api } from '../../lib/api.js'
import { cn } from '../../lib/cn.js'

// Health indicator dot — polls /health lightly so users know the backend is up.
function HealthPill() {
  const [status, setStatus] = useState('checking') // checking | healthy | down
  const [version, setVersion] = useState(null)

  useEffect(() => {
    let active = true
    const check = async () => {
      try {
        const res = await api.health()
        if (!active) return
        setStatus('healthy')
        setVersion(res.version)
      } catch {
        if (active) setStatus('down')
      }
    }
    check()
    const id = setInterval(check, 15000)
    return () => {
      active = false
      clearInterval(id)
    }
  }, [])

  const tone = {
    checking: 'text-muted',
    healthy: 'text-primary',
    down: 'text-danger',
  }[status]

  const label = {
    checking: 'Connecting…',
    healthy: version ? `API v${version}` : 'Online',
    down: 'API offline',
  }[status]

  return (
    <span
      className="hidden items-center gap-1.5 rounded-full border border-border bg-surface-2 px-3 py-1.5 text-xs font-medium sm:inline-flex"
      title={status === 'down' ? 'Backend not reachable on :8000' : 'Backend healthy'}
    >
      <CircleDot className={cn('h-3.5 w-3.5', tone, status === 'healthy' && 'animate-pulse')} aria-hidden="true" />
      <span className="text-muted">{label}</span>
    </span>
  )
}

export function Topbar({ onOpenSidebar }) {
  const navigate = useNavigate()
  return (
    <header className="sticky top-0 z-30 flex h-16 items-center gap-3 border-b border-border bg-background/80 px-4 backdrop-blur-xl md:px-6">
      <Button
        variant="ghost"
        size="icon"
        className="md:hidden"
        icon={Menu}
        onClick={onOpenSidebar}
        aria-label="Open navigation menu"
      />
      <div className="flex-1" />
      <HealthPill />
      <Button icon={UploadCloud} onClick={() => navigate('/upload')} size="md">
        <span className="hidden sm:inline">Upload model</span>
        <span className="sm:hidden">Upload</span>
      </Button>
    </header>
  )
}
