import { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'
import { X } from 'lucide-react'
import { SidebarContent } from './Sidebar.jsx'
import { Topbar } from './Topbar.jsx'
import Button from '../ui/Button.jsx'
import { cn } from '../../lib/cn.js'

export function AppLayout({ children }) {
  const [mobileOpen, setMobileOpen] = useState(false)
  const location = useLocation()

  // Close the mobile drawer on route change.
  useEffect(() => setMobileOpen(false), [location.pathname])

  return (
    <div className="min-h-screen bg-background">
      {/* Desktop sidebar */}
      <aside className="fixed inset-y-0 left-0 z-40 hidden w-64 border-r border-border bg-surface md:block">
        <SidebarContent />
      </aside>

      {/* Mobile drawer */}
      <div
        className={cn(
          'fixed inset-0 z-50 md:hidden',
          mobileOpen ? 'pointer-events-auto' : 'pointer-events-none',
        )}
        aria-hidden={!mobileOpen}
      >
        <div
          className={cn(
            'absolute inset-0 bg-black/60 backdrop-blur-sm transition-opacity duration-200',
            mobileOpen ? 'opacity-100' : 'opacity-0',
          )}
          onClick={() => setMobileOpen(false)}
        />
        <div
          className={cn(
            'absolute inset-y-0 left-0 w-72 max-w-[85%] border-r border-border bg-surface shadow-card-hover transition-transform duration-200',
            mobileOpen ? 'translate-x-0' : '-translate-x-full',
          )}
        >
          <Button
            variant="ghost"
            size="icon"
            icon={X}
            aria-label="Close navigation menu"
            className="absolute right-2 top-3"
            onClick={() => setMobileOpen(false)}
          />
          <SidebarContent onNavigate={() => setMobileOpen(false)} />
        </div>
      </div>

      {/* Main column */}
      <div className="md:pl-64">
        <Topbar onOpenSidebar={() => setMobileOpen(true)} />
        <main className="mx-auto w-full max-w-7xl px-4 py-6 md:px-8 md:py-8">{children}</main>
      </div>
    </div>
  )
}
