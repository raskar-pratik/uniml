import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowRight, ShieldAlert, Trash2 } from 'lucide-react'
import { PageHeader } from '../components/layout/PageHeader.jsx'
import { FileDropzone } from '../components/pipeline/FileDropzone.jsx'
import { Card, CardBody } from '../components/ui/Card.jsx'
import Button from '../components/ui/Button.jsx'
import { ProgressBar } from '../components/ui/ProgressBar.jsx'
import { useFetch } from '../hooks/useFetch.js'
import { api } from '../lib/api.js'
import { usePipeline } from '../context/PipelineContext.jsx'
import { useToast } from '../context/ToastContext.jsx'

export default function Upload() {
  const navigate = useNavigate()
  const toast = useToast()
  const { setUpload, upload, reset } = usePipeline()
  const { data: info } = useFetch((s) => api.info(s))

  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)

  const accept = info?.supported_extensions ?? ['.pt', '.pth', '.pkl', '.joblib', '.h5', '.keras', '.onnx']
  const maxSizeMb = info?.max_upload_size_mb ?? 500

  const handleUpload = async () => {
    if (!file) return
    setUploading(true)
    try {
      const res = await api.upload(file)
      setUpload(res)
      toast.success(`Uploaded ${res.filename}`)
      navigate('/job')
    } catch (err) {
      toast.error(err.message || 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="animate-fade-in">
      <PageHeader eyebrow="New job" title="Upload a model" description="Drop a trained model file to begin. It stays inside this workspace." />

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <Card>
            <CardBody>
              <FileDropzone
                accept={accept}
                maxSizeMb={maxSizeMb}
                disabled={uploading}
                selectedFile={file}
                onFile={setFile}
              />

              {uploading && (
                <div className="mt-4">
                  <p className="mb-2 text-sm text-muted">Uploading &amp; saving to workspace…</p>
                  <ProgressBar indeterminate />
                </div>
              )}

              <div className="mt-5 flex flex-wrap items-center justify-between gap-3">
                <p className="text-sm text-muted">
                  {file ? 'Ready to upload.' : 'Select a file to continue.'}
                </p>
                <div className="flex gap-2">
                  {file && !uploading && (
                    <Button variant="ghost" icon={Trash2} onClick={() => setFile(null)}>
                      Clear
                    </Button>
                  )}
                  <Button
                    onClick={handleUpload}
                    disabled={!file}
                    loading={uploading}
                    iconRight={ArrowRight}
                  >
                    Upload &amp; continue
                  </Button>
                </div>
              </div>
            </CardBody>
          </Card>

          {upload && !file && (
            <div className="mt-4 flex flex-wrap items-center justify-between gap-3 rounded-lg border border-border bg-surface-2/50 px-4 py-3">
              <div className="min-w-0 text-sm">
                <span className="text-muted">Last uploaded: </span>
                <span className="font-medium text-foreground">{upload.filename}</span>
                <span className="metric ml-2 text-muted">{upload.fileSizeHuman}</span>
              </div>
              <div className="flex gap-2">
                <Button variant="ghost" size="sm" onClick={reset}>
                  Discard
                </Button>
                <Button size="sm" variant="secondary" iconRight={ArrowRight} onClick={() => navigate('/job')}>
                  Continue
                </Button>
              </div>
            </div>
          )}
        </div>

        {/* Security note — pickle-based formats execute code on load */}
        <aside>
          <Card className="border-warning/30 bg-warning/5">
            <CardBody>
              <div className="flex items-start gap-3">
                <span className="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-warning/15 text-warning">
                  <ShieldAlert className="h-5 w-5" aria-hidden="true" />
                </span>
                <div>
                  <h3 className="text-sm font-semibold text-foreground">Only upload models you trust</h3>
                  <p className="mt-1 text-sm text-muted">
                    Loading <code className="metric text-xs">.pkl</code>,{' '}
                    <code className="metric text-xs">.joblib</code> and PyTorch files can execute
                    code during deserialization. Run untrusted models in an isolated sandbox.
                  </p>
                </div>
              </div>
            </CardBody>
          </Card>
        </aside>
      </div>
    </div>
  )
}
