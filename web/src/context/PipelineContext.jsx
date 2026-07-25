import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'

// Tracks the active model as it moves through the pipeline:
// upload -> detect/validate -> convert -> generate.
// Persisted to localStorage so a refresh doesn't lose progress.

const PipelineContext = createContext(null)
const STORAGE_KEY = 'uniml.pipeline.v1'

const EMPTY = {
  upload: null, // { modelId, filePath, filename, fileSizeBytes, fileSizeHuman }
  detection: null,
  validation: null,
  conversion: null,
  generation: null,
}

function load() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? { ...EMPTY, ...JSON.parse(raw) } : EMPTY
  } catch {
    return EMPTY
  }
}

export function PipelineProvider({ children }) {
  const [state, setState] = useState(load)

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
    } catch {
      /* storage may be unavailable (private mode) — non-fatal */
    }
  }, [state])

  const setUpload = useCallback((res) => {
    // A brand-new upload invalidates everything downstream.
    setState({
      ...EMPTY,
      upload: {
        modelId: res.model_id,
        filePath: res.file_path,
        filename: res.filename,
        fileSizeBytes: res.file_size_bytes,
        fileSizeHuman: res.file_size_human,
      },
    })
  }, [])

  const setDetection = useCallback((detection) => setState((s) => ({ ...s, detection })), [])
  const setValidation = useCallback((validation) => setState((s) => ({ ...s, validation })), [])
  const setConversion = useCallback((conversion) => setState((s) => ({ ...s, conversion })), [])
  const setGeneration = useCallback((generation) => setState((s) => ({ ...s, generation })), [])
  const reset = useCallback(() => setState(EMPTY), [])

  const value = useMemo(
    () => ({
      ...state,
      modelId: state.upload?.modelId ?? null,
      filePath: state.upload?.filePath ?? null,
      hasUpload: Boolean(state.upload),
      setUpload,
      setDetection,
      setValidation,
      setConversion,
      setGeneration,
      reset,
    }),
    [state, setUpload, setDetection, setValidation, setConversion, setGeneration, reset],
  )

  return <PipelineContext.Provider value={value}>{children}</PipelineContext.Provider>
}

export function usePipeline() {
  const ctx = useContext(PipelineContext)
  if (!ctx) throw new Error('usePipeline must be used within a PipelineProvider')
  return ctx
}
