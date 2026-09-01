import { useState, useEffect, useCallback } from 'react'
import { fetchDashboardMetrics } from '../services/api'

const POLL_INTERVAL = 10_000 // 10 seconds

/**
 * Custom hook for fetching dashboard metrics.
 * Auto-refreshes every 10 seconds.
 */
export function useDashboard() {
  const [metrics, setMetrics] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchData = useCallback(async () => {
    try {
      setLoading(true)
      const data = await fetchDashboardMetrics()
      setMetrics(data)
      setError(null)
    } catch (err) {
      setError(err.message)
      console.error('Failed to fetch dashboard metrics:', err)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    // Initial fetch
    fetchData()

    // Set up polling
    const intervalId = setInterval(fetchData, POLL_INTERVAL)

    return () => clearInterval(intervalId)
  }, [fetchData])

  return { metrics, loading, error, refetch: fetchData }
}
