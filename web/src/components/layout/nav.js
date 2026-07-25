import { LayoutDashboard, UploadCloud, ListChecks } from 'lucide-react'

// Primary navigation. The full pipeline lives in the Job page; Upload just
// creates a job and hands off to it.
export const NAV_ITEMS = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/upload', label: 'Upload', icon: UploadCloud },
  { to: '/job', label: 'Job', icon: ListChecks, requiresModel: true },
]
