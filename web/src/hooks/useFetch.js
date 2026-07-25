import { useCallback, useEffect, useState } from 'react'

// Minimal fetch-on-mount hook with loading/error state and manual refetch.
// `fn` receives an AbortSignal and should return a promise.
export function useFetch(fn, deps = []) {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  const run = useCallback((signal) => {
    setLoading(true)
    setError(null)
    return fn(signal)
      .then((res) => {
        if (!signal?.aborted) setData(res)
      })
      .catch((err) => {
        if (err.name !== 'AbortError' && !signal?.aborted) setError(err)
      })
      .finally(() => {
        if (!signal?.aborted) setLoading(false)
      })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)

  useEffect(() => {
    const controller = new AbortController()
    run(controller.signal)
    return () => controller.abort()
  }, [run])

  const refetch = useCallback(() => {
    const controller = new AbortController()
    return run(controller.signal)
  }, [run])

  return { data, error, loading, refetch, setData }
}
