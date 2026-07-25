import { Navigate, useLocation } from 'react-router-dom'
import { usePipeline } from '../../context/PipelineContext.jsx'

// Guards pipeline pages that need an uploaded model. Redirects to /upload
// while remembering the intended destination.
export function RequireModel({ children }) {
  const { hasUpload } = usePipeline()
  const location = useLocation()
  if (!hasUpload) {
    return <Navigate to="/upload" replace state={{ from: location.pathname }} />
  }
  return children
}
