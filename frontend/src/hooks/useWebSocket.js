import { useState, useEffect, useRef, useCallback } from 'react'

const WS_URL = 'ws://localhost:8000/ws/alerts'
const MAX_ALERTS = 50
const RECONNECT_DELAY = 3000

/**
 * Custom hook for WebSocket connection to receive real-time alerts.
 * Handles auto-reconnection and alert state management.
 */
export function useWebSocket() {
  const [alerts, setAlerts] = useState([])
  const [connected, setConnected] = useState(false)
  const wsRef = useRef(null)
  const reconnectTimer = useRef(null)

  const connect = useCallback(() => {
    try {
      const ws = new WebSocket(WS_URL)

      ws.onopen = () => {
        console.log('🔌 WebSocket connected')
        setConnected(true)
      }

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)

          if (message.type === 'alert' && message.data) {
            setAlerts((prev) => {
              const updated = [message.data, ...prev]
              // Keep only the latest MAX_ALERTS
              return updated.slice(0, MAX_ALERTS)
            })
          }
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err)
        }
      }

      ws.onclose = () => {
        console.log('🔌 WebSocket disconnected')
        setConnected(false)
        // Auto-reconnect
        reconnectTimer.current = setTimeout(connect, RECONNECT_DELAY)
      }

      ws.onerror = (err) => {
        console.error('WebSocket error:', err)
        ws.close()
      }

      wsRef.current = ws
    } catch (err) {
      console.error('Failed to create WebSocket:', err)
      reconnectTimer.current = setTimeout(connect, RECONNECT_DELAY)
    }
  }, [])

  useEffect(() => {
    connect()

    return () => {
      if (reconnectTimer.current) {
        clearTimeout(reconnectTimer.current)
      }
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [connect])

  const clearAlerts = useCallback(() => {
    setAlerts([])
  }, [])

  return { alerts, connected, clearAlerts }
}
