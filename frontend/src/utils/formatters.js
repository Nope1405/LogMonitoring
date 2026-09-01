import { format, formatDistanceToNow } from 'date-fns'

/**
 * Format a number with thousand separators.
 */
export function formatNumber(num) {
  if (num == null) return '—'
  return new Intl.NumberFormat('en-US').format(num)
}

/**
 * Format a timestamp for display.
 */
export function formatTimestamp(ts) {
  if (!ts) return '—'
  return format(new Date(ts), 'yyyy-MM-dd HH:mm:ss')
}

/**
 * Format a timestamp as relative time (e.g., "2 minutes ago").
 */
export function formatRelativeTime(ts) {
  if (!ts) return '—'
  return formatDistanceToNow(new Date(ts), { addSuffix: true })
}

/**
 * Format response time in ms.
 */
export function formatResponseTime(ms) {
  if (ms == null) return '—'
  if (ms < 1000) return `${ms}ms`
  return `${(ms / 1000).toFixed(2)}s`
}

/**
 * Get status code color class.
 */
export function getStatusColor(code) {
  if (code >= 500) return 'var(--accent-red)'
  if (code >= 400) return 'var(--accent-amber)'
  if (code >= 300) return 'var(--accent-cyan)'
  return 'var(--accent-green)'
}
