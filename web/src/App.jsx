import { Routes, Route, Navigate } from 'react-router-dom'
import { AppLayout } from './components/layout/AppLayout.jsx'
import { RequireModel } from './components/pipeline/RequireModel.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Upload from './pages/Upload.jsx'
import JobDetail from './pages/JobDetail.jsx'
import NotFound from './pages/NotFound.jsx'

export default function App() {
  return (
    <AppLayout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/upload" element={<Upload />} />
        <Route
          path="/job"
          element={
            <RequireModel>
              <JobDetail />
            </RequireModel>
          }
        />
        {/* Retired standalone pages — the full pipeline now lives in Job Detail.
            Redirect old links so existing bookmarks keep working. */}
        <Route path="/inspect" element={<Navigate to="/job" replace />} />
        <Route path="/convert" element={<Navigate to="/job" replace />} />
        <Route path="/deploy" element={<Navigate to="/job" replace />} />
        {/* Monitoring retired with the simulated /metrics endpoint. */}
        <Route path="/monitoring" element={<Navigate to="/" replace />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </AppLayout>
  )
}
