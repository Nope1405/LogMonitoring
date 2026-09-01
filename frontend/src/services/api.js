import axios from 'axios'

const API_BASE = 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

/**
 * Fetch dashboard metrics (time-series data + summary stats).
 * @param {number} minutes - Time window in minutes (default: 10)
 */
export async function fetchDashboardMetrics(minutes = 10) {
  const { data } = await api.get('/dashboard/metrics', {
    params: { minutes },
  })
  return data
}

/**
 * Fetch suspicious IP addresses.
 * @param {number} minutes - Time window
 * @param {number} threshold - Minimum request count
 */
export async function fetchSuspiciousIPs(minutes = 5, threshold = 50) {
  const { data } = await api.get('/dashboard/suspicious-ips', {
    params: { minutes, threshold },
  })
  return data
}

/**
 * Fetch recent alerts.
 * @param {number} limit - Max alerts to return
 * @param {boolean} unresolvedOnly - Filter to unresolved alerts
 */
export async function fetchAlerts(limit = 20, unresolvedOnly = false) {
  const { data } = await api.get('/dashboard/alerts', {
    params: { limit, unresolved_only: unresolvedOnly },
  })
  return data
}

/**
 * Send a single log event to the backend.
 * @param {Object} event - Log event data
 */
export async function sendLogEvent(event) {
  const { data } = await api.post('/logs/', event)
  return data
}

export default api
