import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  ScanSearch,
  ShieldCheck,
  Repeat2,
  BadgeCheck,
  Package,
  Play,
  RotateCcw,
  Download,
  Check,
  X,
  UploadCloud,
  FileCode2,
  FileBox,
  FileArchive,
  Copy,
  DownloadCloud,
  CircleDot,
} from 'lucide-react'
import { PageHeader } from '../components/layout/PageHeader.jsx'
import { Card, CardHeader, CardBody } from '../components/ui/Card.jsx'
import { Badge } from '../components/ui/Badge.jsx'
import { ProgressBar } from '../components/ui/ProgressBar.jsx'
import { EmptyState } from '../components/ui/EmptyState.jsx'
import Button from '../components/ui/Button.jsx'
import { Spinner } from '../components/ui/Spinner.jsx'
import { FrameworkBadge } from '../components/common/FrameworkBadge.jsx'
import { ConfidenceMeter } from '../components/common/ConfidenceMeter.jsx'
import { api } from '../lib/api.js'
import { usePipeline } from '../context/PipelineContext.jsx'
import { useToast } from '../context/ToastContext.jsx'
import { cn } from '../lib/cn.js'
import { formatBytes, formatNumber, formatShape } from '../lib/format.js'
import { SEVERITY_TONE, SEVERITY_ORDER } from '../lib/constants.js'

// ── Stage definitions ────────────────────────────────────────────────
// Each stage maps to a real backend call. `verifying` re-validates the ONNX
// artifact (a genuine onnx.checker integrity pass), so no stage is decorative.
const STAGES = [
  { key: 'detecting', label: 'Detect framework', icon: ScanSearch },
  { key: 'validating', label: 'Validate model', icon: ShieldCheck },
  { key: 'converting', label: 'Convert to ONNX', icon: Repeat2 },
  { key: 'verifying', label: 'Verify ONNX', icon: BadgeCheck },
  { key: 'packaging', label: 'Package deployment', icon: Package },
]

// Overall status → badge tone + label (the 7 statuses from the spec).
const STATUS_META = {
  queued: { tone: 'neutral', label: 'Queued' },
  detecting: { tone: 'info', label: 'Detecting' },
  validating: { tone: 'info', label: 'Validating' },
  converting: { tone: 'info', label: 'Converting' },
  verifying: { tone: 'info', label: 'Verifying' },
  packaging: { tone: 'info', label: 'Packaging' },
  ready: { tone: 'success', label: 'Ready' },
  failed: { tone: 'danger', label: 'Failed' },
}

// Deterministic defaults for the one-click package step. Full control lives on
// the Deploy page — this keeps the "run everything" action lazy and predictable.
const PACKAGE_DEFAULTS = {
  project_name: 'ml_inference_server',
  host: '0.0.0.0',
  port: 8080,
  include_docker: true,
  include_readme: true,
}

const PENDING = { status: 'pending' }

// Seed stage state from whatever the pipeline context already holds, so
// arriving here after running earlier steps shows them as complete.
function seedStages({ detection, validation, conversion, generation }) {
  const convDone = conversion && ['success', 'skipped'].includes(conversion.conversion_status)
  return {
    detecting: detection ? { status: 'done' } : PENDING,
    validating: validation ? { status: 'done' } : PENDING,
    converting: convDone
      ? { status: 'done' }
      : conversion
        ? { status: 'failed', message: conversion.error_message || 'Conversion failed' }
        : PENDING,
    // A finished package implies verify + package already succeeded.
    verifying: generation ? { status: 'done' } : PENDING,
    packaging: generation ? { status: 'done' } : PENDING,
  }
}

function nowStamp() {
  return new Date().toLocaleTimeString('en-US', { hour12: false })
}

const LOG_TONE = {
  info: 'text-muted',
  success: 'text-primary',
  warn: 'text-warning',
  error: 'text-danger',
}

export default function JobDetail() {
  const toast = useToast()
  const pipeline = usePipeline()
  const {
    upload,
    modelId,
    filePath,
    hasUpload,
    detection,
    validation,
    conversion,
    generation,
    setDetection,
    setValidation,
    setConversion,
    setGeneration,
  } = pipeline

  const [stages, setStages] = useState(() => seedStages(pipeline))
  const [logs, setLogs] = useState([])
  const [running, setRunning] = useState(false)
  const [activeKey, setActiveKey] = useState(null)

  const logRef = useRef(null)
  const endRef = useRef(null)
  const runningRef = useRef(false)

  // Reset when the active job changes (new upload).
  useEffect(() => {
    setStages(seedStages(pipeline))
    setLogs([])
    setActiveKey(null)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [modelId])

  // Auto-scroll the console to the newest line, but only if the user is already
  // near the bottom (don't fight manual scroll). Honors reduced-motion.
  useEffect(() => {
    const el = logRef.current
    if (!el) return
    const nearBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 60
    if (nearBottom) {
      const reduce = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
      endRef.current?.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'end' })
    }
  }, [logs])

  const log = useCallback((level, message) => {
    setLogs((prev) => [...prev, { id: prev.length, t: nowStamp(), level, message }])
  }, [])

  const setStage = useCallback((key, patch) => {
    setStages((prev) => ({ ...prev, [key]: { ...prev[key], ...patch } }))
  }, [])

  const doneCount = STAGES.filter((s) => stages[s.key]?.status === 'done').length
  const failedStage = STAGES.find((s) => stages[s.key]?.status === 'failed')
  const progress = (doneCount / STAGES.length) * 100

  const overallStatus = useMemo(() => {
    if (failedStage) return 'failed'
    if (doneCount === STAGES.length) return 'ready'
    if (running && activeKey) return activeKey
    return 'queued'
  }, [failedStage, doneCount, running, activeKey])

  const isReady = overallStatus === 'ready'

  // ── Orchestrator ───────────────────────────────────────────────────
  // Runs stages from `startIndex` to the end, using local vars for results so
  // each step reads fresh output rather than not-yet-committed context state.
  const runFrom = useCallback(
    async (startIndex) => {
      if (runningRef.current) return
      runningRef.current = true
      setRunning(true)

      let onnxPath = conversion?.onnx_path ?? null

      for (let i = startIndex; i < STAGES.length; i++) {
        const { key, label } = STAGES[i]
        setActiveKey(key)
        setStage(key, { status: 'running', message: undefined })
        log('info', `${label}…`)

        try {
          if (key === 'detecting') {
            const r = await api.detect(filePath)
            setDetection(r)
            log('success', `Detected ${r.framework} (${Math.round((r.confidence ?? 0) * 100)}% confidence)`)
          } else if (key === 'validating') {
            const r = await api.validate(filePath)
            setValidation(r)
            const errors = (r.issues || []).filter((x) => x.severity === 'error' || x.severity === 'critical')
            if (errors.length) log('warn', `Validation flagged ${errors.length} issue(s) — continuing`)
            else log('success', 'Model structure looks valid')
          } else if (key === 'converting') {
            const r = await api.convert(filePath, modelId)
            setConversion(r)
            if (!['success', 'skipped'].includes(r.conversion_status)) {
              throw new Error(r.error_message || `Conversion ${r.conversion_status}`)
            }
            onnxPath = r.onnx_path
            log('success', `ONNX ready (${r.onnx_size_human || formatBytes(r.onnx_size_bytes)})`)
          } else if (key === 'verifying') {
            if (!onnxPath) throw new Error('No ONNX artifact to verify')
            const r = await api.validate(onnxPath)
            if (!r.is_valid) throw new Error('ONNX failed the integrity check')
            log('success', 'ONNX passed integrity check')
          } else if (key === 'packaging') {
            const r = await api.generate({ model_id: modelId, ...PACKAGE_DEFAULTS })
            setGeneration(r)
            log('success', `Packaged ${r.files_generated?.length ?? 0} files (${r.zip_size_human || formatBytes(r.zip_size_bytes)})`)
          }
          setStage(key, { status: 'done' })
        } catch (err) {
          setStage(key, { status: 'failed', message: err.message })
          log('error', `${label} failed: ${err.message}`)
          setActiveKey(null)
          setRunning(false)
          runningRef.current = false
          toast.error(`${label} failed`)
          return
        }
      }

      setActiveKey(null)
      setRunning(false)
      runningRef.current = false
      log('success', 'Pipeline complete — deployment package is ready')
      toast.success('Job ready to download')
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [filePath, modelId, conversion],
  )

  const handleRun = useCallback(() => {
    const firstPending = STAGES.findIndex((s) => stages[s.key]?.status !== 'done')
    runFrom(firstPending === -1 ? 0 : firstPending)
  }, [stages, runFrom])

  const handleRerun = useCallback(() => {
    setStages(Object.fromEntries(STAGES.map((s) => [s.key, { status: 'pending' }])))
    setLogs([])
    log('info', 'Re-running full pipeline')
    runFrom(0)
  }, [log, runFrom])

  const handleRetry = useCallback(() => {
    const idx = STAGES.findIndex((s) => stages[s.key]?.status === 'failed')
    if (idx !== -1) runFrom(idx)
  }, [stages, runFrom])

  const copyLogs = useCallback(() => {
    const text = logs.map((l) => `${l.t} [${l.level.toUpperCase()}] ${l.message}`).join('\n')
    navigator.clipboard?.writeText(text)
    toast.info('Log copied to clipboard')
  }, [logs, toast])

  const downloadLogs = useCallback(() => {
    const text = logs.map((l) => `${l.t} [${l.level.toUpperCase()}] ${l.message}`).join('\n')
    const url = URL.createObjectURL(new Blob([text], { type: 'text/plain' }))
    const a = document.createElement('a')
    a.href = url
    a.download = `${upload?.filename || 'job'}-log.txt`
    a.click()
    URL.revokeObjectURL(url)
  }, [logs, upload])

  // ── Empty state ────────────────────────────────────────────────────
  if (!hasUpload) {
    return (
      <div className="animate-fade-in">
        <PageHeader eyebrow="Job" title="Job detail" />
        <EmptyState
          icon={UploadCloud}
          title="No active job"
          description="Upload a model to create a job and run the conversion pipeline."
          action={
            <Button as={Link} to="/upload" icon={UploadCloud}>
              Upload a model
            </Button>
          }
        />
      </div>
    )
  }

  const statusMeta = STATUS_META[overallStatus]
  const sortedIssues = [...(validation?.issues ?? [])].sort(
    (a, b) => (SEVERITY_ORDER[a.severity] ?? 9) - (SEVERITY_ORDER[b.severity] ?? 9),
  )

  return (
    <div className="animate-fade-in">
      <PageHeader
        eyebrow="Job"
        title={upload.filename}
        actions={
          <>
            {isReady ? (
              <Button variant="secondary" icon={RotateCcw} onClick={handleRerun} disabled={running}>
                Re-run
              </Button>
            ) : failedStage ? (
              <Button variant="secondary" icon={RotateCcw} onClick={handleRetry} loading={running}>
                Retry
              </Button>
            ) : (
              <Button icon={Play} onClick={handleRun} loading={running}>
                {doneCount > 0 ? 'Resume pipeline' : 'Run pipeline'}
              </Button>
            )}
            <Button
              as="a"
              href={isReady ? api.downloadUrl(modelId) : undefined}
              variant={isReady ? 'primary' : 'outline'}
              icon={Download}
              className={cn(!isReady && 'pointer-events-none opacity-50')}
              aria-disabled={!isReady}
            >
              Download ZIP
            </Button>
          </>
        }
      />

      {/* Summary bar */}
      <Card className="mb-6">
        <CardBody className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex flex-wrap items-center gap-3">
            <Badge tone={statusMeta.tone} dot>
              {statusMeta.label}
            </Badge>
            {detection && <FrameworkBadge framework={detection.framework} />}
            <span className="metric text-sm text-muted">{upload.fileSizeHuman}</span>
            <span className="metric text-xs text-muted/70" title={modelId}>
              #{String(modelId).slice(0, 8)}
            </span>
          </div>
          <div className="flex items-center gap-3 sm:w-64">
            <ProgressBar
              value={progress}
              tone={failedStage ? 'danger' : isReady ? 'primary' : 'info'}
              showLabel
            />
          </div>
        </CardBody>
      </Card>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-5">
        {/* Left: pipeline + details */}
        <div className="space-y-6 lg:col-span-3">
          <Card>
            <CardHeader title="Pipeline" subtitle={`${doneCount} of ${STAGES.length} stages complete`} />
            <CardBody>
              <ol className="space-y-1">
                {STAGES.map((stage, i) => {
                  const st = stages[stage.key]?.status ?? 'pending'
                  const msg = stages[stage.key]?.message
                  const Icon = stage.icon
                  const isActive = st === 'running'
                  return (
                    <li
                      key={stage.key}
                      aria-current={isActive ? 'step' : undefined}
                      className={cn(
                        'flex items-start gap-3 rounded-lg border px-3 py-3 transition-colors',
                        isActive
                          ? 'border-info/40 bg-info/5'
                          : st === 'failed'
                            ? 'border-danger/30 bg-danger/5'
                            : st === 'done'
                              ? 'border-primary/20 bg-primary/5'
                              : 'border-border bg-surface-2/30',
                      )}
                    >
                      <span
                        className={cn(
                          'mt-0.5 grid h-8 w-8 shrink-0 place-items-center rounded-full border',
                          st === 'done'
                            ? 'border-primary bg-primary text-primary-fg'
                            : st === 'failed'
                              ? 'border-danger bg-danger text-white'
                              : isActive
                                ? 'border-info text-info'
                                : 'border-border-strong text-muted',
                        )}
                      >
                        {st === 'done' ? (
                          <Check className="h-4 w-4" aria-hidden="true" />
                        ) : st === 'failed' ? (
                          <X className="h-4 w-4" aria-hidden="true" />
                        ) : isActive ? (
                          <Spinner size={16} />
                        ) : (
                          <Icon className="h-4 w-4" aria-hidden="true" />
                        )}
                      </span>
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center justify-between gap-2">
                          <span className="metric text-[10px] uppercase tracking-wider text-muted">
                            {`Stage 0${i + 1}`}
                          </span>
                          <span
                            className={cn(
                              'text-xs font-medium capitalize',
                              st === 'failed' ? 'text-danger' : st === 'done' ? 'text-primary' : 'text-muted',
                            )}
                          >
                            {st === 'running' ? 'running' : st}
                          </span>
                        </div>
                        <p className="text-sm font-medium text-foreground">{stage.label}</p>
                        {msg && <p className="mt-0.5 text-xs text-danger">{msg}</p>}
                      </div>
                    </li>
                  )
                })}
              </ol>
            </CardBody>
          </Card>

          {/* Detection + validation + conversion details */}
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <Card>
              <CardHeader title="Detection" />
              <CardBody className="space-y-3">
                {detection ? (
                  <>
                    <FrameworkBadge framework={detection.framework} />
                    <ConfidenceMeter value={detection.confidence} />
                  </>
                ) : (
                  <p className="text-sm text-muted">Not run yet.</p>
                )}
              </CardBody>
            </Card>

            <Card>
              <CardHeader
                title="Conversion"
                action={
                  conversion && (
                    <Badge tone={['success', 'skipped'].includes(conversion.conversion_status) ? 'success' : 'danger'}>
                      {conversion.conversion_status}
                    </Badge>
                  )
                }
              />
              <CardBody>
                {conversion ? (
                  <dl className="grid grid-cols-2 gap-3 text-sm">
                    <div>
                      <dt className="text-xs text-muted">Original</dt>
                      <dd className="metric font-medium text-foreground">{upload.fileSizeHuman}</dd>
                    </div>
                    <div>
                      <dt className="text-xs text-muted">ONNX</dt>
                      <dd className="metric font-medium text-foreground">
                        {conversion.onnx_size_human || formatBytes(conversion.onnx_size_bytes)}
                      </dd>
                    </div>
                  </dl>
                ) : (
                  <p className="text-sm text-muted">Not run yet.</p>
                )}
              </CardBody>
            </Card>
          </div>

          <Card>
            <CardHeader
              title="Validation"
              subtitle={validation ? `${sortedIssues.length} finding(s)` : undefined}
              action={
                validation && (
                  <Badge tone={validation.is_valid ? 'success' : 'danger'}>
                    {validation.is_valid ? 'Valid' : 'Invalid'}
                  </Badge>
                )
              }
            />
            <CardBody>
              {!validation ? (
                <p className="text-sm text-muted">Not run yet.</p>
              ) : (
                <>
                  <dl className="mb-4 grid grid-cols-2 gap-3 text-sm sm:grid-cols-4">
                    <div>
                      <dt className="text-xs text-muted">Class</dt>
                      <dd className="metric truncate font-medium text-foreground">{validation.model_class || '—'}</dd>
                    </div>
                    <div>
                      <dt className="text-xs text-muted">Params</dt>
                      <dd className="metric font-medium text-foreground">
                        {validation.parameters != null ? formatNumber(validation.parameters) : '—'}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-xs text-muted">Input</dt>
                      <dd className="metric font-medium text-foreground">{formatShape(validation.input_shape)}</dd>
                    </div>
                    <div>
                      <dt className="text-xs text-muted">Output</dt>
                      <dd className="metric font-medium text-foreground">{formatShape(validation.output_shape)}</dd>
                    </div>
                  </dl>
                  {sortedIssues.length > 0 && (
                    <ul className="space-y-1.5">
                      {sortedIssues.map((issue, i) => {
                        const tone = SEVERITY_TONE[issue.severity] || 'info'
                        const color = { info: 'text-info', warning: 'text-warning', danger: 'text-danger' }[tone]
                        return (
                          <li key={i} className="flex items-start gap-2 text-sm">
                            <CircleDot className={cn('mt-0.5 h-3.5 w-3.5 shrink-0', color)} aria-hidden="true" />
                            <span className="text-muted">
                              <span className="capitalize text-foreground">{issue.severity}</span> · {issue.message}
                            </span>
                          </li>
                        )
                      })}
                    </ul>
                  )}
                </>
              )}
            </CardBody>
          </Card>
        </div>

        {/* Right: log console + artifacts */}
        <div className="space-y-6 lg:col-span-2">
          <Card className="flex flex-col">
            <CardHeader
              title="Activity log"
              action={
                <div className="flex gap-1">
                  <Button variant="ghost" size="icon" icon={Copy} onClick={copyLogs} aria-label="Copy log" disabled={!logs.length} />
                  <Button variant="ghost" size="icon" icon={DownloadCloud} onClick={downloadLogs} aria-label="Download log" disabled={!logs.length} />
                </div>
              }
            />
            <CardBody>
              <div
                ref={logRef}
                role="log"
                aria-live="polite"
                aria-relevant="additions"
                aria-label="Job activity log"
                className="h-72 overflow-y-auto rounded-lg border border-border bg-background/70 p-3"
              >
                {logs.length === 0 ? (
                  <p className="metric text-xs text-muted/60">
                    No activity yet. Run the pipeline to stream progress here.
                  </p>
                ) : (
                  logs.map((l) => (
                    <p key={l.id} className="metric whitespace-pre-wrap text-xs leading-relaxed">
                      <span className="text-muted/50">{l.t}</span>{' '}
                      <span className={LOG_TONE[l.level]}>{l.message}</span>
                    </p>
                  ))
                )}
                <div ref={endRef} />
              </div>
            </CardBody>
          </Card>

          <Card>
            <CardHeader title="Artifacts" icon={Package} />
            <CardBody className="space-y-2">
              {conversion && ['success', 'skipped'].includes(conversion.conversion_status) && (
                <ArtifactRow
                  icon={FileBox}
                  name="model.onnx"
                  meta={conversion.onnx_size_human || formatBytes(conversion.onnx_size_bytes)}
                />
              )}
              {generation && (
                <>
                  <ArtifactRow
                    icon={FileArchive}
                    name={`${generation.project_name}.zip`}
                    meta={generation.zip_size_human || formatBytes(generation.zip_size_bytes)}
                    href={api.downloadUrl(modelId)}
                  />
                  <details className="rounded-lg border border-border bg-surface-2/30 p-3">
                    <summary className="cursor-pointer text-sm text-muted">
                      {generation.files_generated?.length ?? 0} generated files
                    </summary>
                    <ul className="mt-2 space-y-1">
                      {(generation.files_generated ?? []).map((f) => (
                        <li key={f} className="flex items-center gap-2 text-xs text-muted">
                          <FileCode2 className="h-3.5 w-3.5 shrink-0 text-muted/70" aria-hidden="true" />
                          <code className="metric truncate">{f}</code>
                        </li>
                      ))}
                    </ul>
                  </details>
                </>
              )}
              {!conversion && !generation && <p className="text-sm text-muted">No artifacts yet.</p>}
            </CardBody>
          </Card>
        </div>
      </div>
    </div>
  )
}

// Small inline row — kept local to this page (single consumer; no premature abstraction).
function ArtifactRow({ icon: Icon, name, meta, href }) {
  return (
    <div className="flex items-center justify-between gap-3 rounded-lg border border-border bg-surface-2/40 p-3">
      <div className="flex min-w-0 items-center gap-3">
        <span className="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-surface-3 text-primary">
          <Icon className="h-4 w-4" aria-hidden="true" />
        </span>
        <div className="min-w-0">
          <p className="truncate text-sm font-medium text-foreground">{name}</p>
          <p className="metric text-xs text-muted">{meta}</p>
        </div>
      </div>
      {href && (
        <Button as="a" href={href} variant="ghost" size="icon" icon={Download} aria-label={`Download ${name}`} />
      )}
    </div>
  )
}
