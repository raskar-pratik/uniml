import { Link } from 'react-router-dom'
import {
  Package,
  HardDrive,
  FileBox,
  ArrowRight,
  UploadCloud,
  ScanSearch,
  Repeat2,
  Rocket,
  Boxes,
} from 'lucide-react'
import { PageHeader } from '../components/layout/PageHeader.jsx'
import { StatCard } from '../components/ui/StatCard.jsx'
import { Card, CardHeader, CardBody } from '../components/ui/Card.jsx'
import Button from '../components/ui/Button.jsx'
import { Badge } from '../components/ui/Badge.jsx'
import { FrameworkBadge } from '../components/common/FrameworkBadge.jsx'
import { EmptyState } from '../components/ui/EmptyState.jsx'
import { Skeleton } from '../components/ui/Skeleton.jsx'
import { useFetch } from '../hooks/useFetch.js'
import { api } from '../lib/api.js'
import { formatBytes } from '../lib/format.js'
import { usePipeline } from '../context/PipelineContext.jsx'

const STEP_CARDS = [
  { to: '/upload', icon: UploadCloud, title: 'Upload', desc: 'PyTorch, TensorFlow, scikit-learn or ONNX.' },
  { to: '/job', icon: ScanSearch, title: 'Inspect', desc: 'Auto-detect framework and validate structure.' },
  { to: '/job', icon: Repeat2, title: 'Convert', desc: 'Produce a portable ONNX artifact.' },
  { to: '/job', icon: Rocket, title: 'Deploy', desc: 'Generate a FastAPI + Docker package.' },
]

export default function Dashboard() {
  const { data: stats, loading: statsLoading } = useFetch((s) => api.stats(s))
  const { data: info, loading: infoLoading } = useFetch((s) => api.info(s))
  const { hasUpload, upload } = usePipeline()

  return (
    <div className="animate-fade-in">
      <PageHeader
        eyebrow="Overview"
        title="Model Deployment Studio"
        description="Turn any trained model into a production-ready ONNX inference service — upload, inspect, convert, and package in four steps."
        actions={
          <Button as={Link} to="/upload" icon={UploadCloud}>
            New conversion
          </Button>
        }
      />

      {/* KPIs — sourced from GET /api/v1/stats */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <StatCard
          label="Packages generated"
          value={stats?.generated_models_count ?? 0}
          icon={Package}
          tone="primary"
          loading={statsLoading}
          hint="Deployment packages in this workspace"
        />
        <StatCard
          label="Artifacts on disk"
          value={statsLoading ? '' : formatBytes(stats?.total_storage_bytes ?? 0)}
          icon={HardDrive}
          tone="info"
          loading={statsLoading}
          hint="Total size of generated output"
        />
        <StatCard
          label="Models uploaded"
          value={stats?.uploaded_models_count ?? 0}
          icon={FileBox}
          tone="warning"
          loading={statsLoading}
          hint="Uploaded, awaiting or mid-conversion"
        />
      </div>

      <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Pipeline quick-start */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader
              title="Conversion pipeline"
              subtitle="Four steps from a trained model to a deployable service."
              icon={Boxes}
              action={
                hasUpload && (
                  <Button as={Link} to="/job" variant="secondary" size="sm" iconRight={ArrowRight}>
                    Resume
                  </Button>
                )
              }
            />
            <CardBody>
              {hasUpload && (
                <div className="mb-4 flex items-center justify-between rounded-lg border border-primary/30 bg-primary/5 px-4 py-3">
                  <div className="min-w-0">
                    <p className="text-xs text-muted">Active model</p>
                    <p className="truncate text-sm font-medium text-foreground">{upload.filename}</p>
                  </div>
                  <Badge tone="success" dot>
                    In progress
                  </Badge>
                </div>
              )}
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                {STEP_CARDS.map((step, i) => (
                  <Link
                    key={step.to}
                    to={step.to}
                    className="group flex items-start gap-3 rounded-lg border border-border bg-surface-2/40 p-4 transition-colors hover:border-primary/40 hover:bg-surface-2"
                  >
                    <span className="grid h-10 w-10 shrink-0 place-items-center rounded-lg bg-surface-3 text-primary">
                      <step.icon className="h-5 w-5" aria-hidden="true" />
                    </span>
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="metric text-xs text-muted">{`0${i + 1}`}</span>
                        <span className="font-medium text-foreground">{step.title}</span>
                      </div>
                      <p className="mt-0.5 text-sm text-muted">{step.desc}</p>
                    </div>
                  </Link>
                ))}
              </div>
            </CardBody>
          </Card>
        </div>

        {/* Platform capabilities — sourced from GET /info */}
        <Card>
          <CardHeader title="Platform" subtitle="Supported frameworks & limits" />
          <CardBody className="space-y-4">
            {infoLoading ? (
              <div className="space-y-3">
                <Skeleton className="h-5 w-3/4" />
                <Skeleton className="h-5 w-1/2" />
                <Skeleton className="h-5 w-2/3" />
              </div>
            ) : info ? (
              <>
                <div>
                  <p className="eyebrow mb-2">Frameworks</p>
                  <div className="flex flex-wrap gap-2">
                    {info.supported_frameworks.map((fw) => (
                      <FrameworkBadge key={fw} framework={fw} />
                    ))}
                  </div>
                </div>
                <div>
                  <p className="eyebrow mb-2">Accepted extensions</p>
                  <div className="flex flex-wrap gap-1.5">
                    {info.supported_extensions.map((ext) => (
                      <code
                        key={ext}
                        className="metric rounded bg-surface-2 px-1.5 py-0.5 text-xs text-muted"
                      >
                        {ext}
                      </code>
                    ))}
                  </div>
                </div>
                <dl className="grid grid-cols-2 gap-3 border-t border-border pt-4 text-sm">
                  <div>
                    <dt className="text-xs text-muted">Max upload</dt>
                    <dd className="metric font-medium text-foreground">{info.max_upload_size_mb} MB</dd>
                  </div>
                  <div>
                    <dt className="text-xs text-muted">Python</dt>
                    <dd className="metric font-medium text-foreground">{info.python_version}</dd>
                  </div>
                </dl>
              </>
            ) : (
              <EmptyState title="Platform info unavailable" description="Could not reach the backend." />
            )}
          </CardBody>
        </Card>
      </div>
    </div>
  )
}
