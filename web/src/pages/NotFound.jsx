import { Link } from 'react-router-dom'
import { Home, Compass } from 'lucide-react'
import Button from '../components/ui/Button.jsx'

export default function NotFound() {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center text-center animate-fade-in">
      <span className="mb-5 grid h-16 w-16 place-items-center rounded-2xl bg-surface-2 text-muted">
        <Compass className="h-8 w-8" aria-hidden="true" />
      </span>
      <p className="metric text-sm text-primary">404</p>
      <h1 className="mt-1 text-2xl font-bold text-foreground">Page not found</h1>
      <p className="mt-2 max-w-sm text-sm text-muted">
        The page you're looking for doesn't exist or has moved.
      </p>
      <Button as={Link} to="/" icon={Home} className="mt-6">
        Back to dashboard
      </Button>
    </div>
  )
}
