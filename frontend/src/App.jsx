import { useState, useEffect } from 'react'
import Layout from './components/Layout'
import StatCard from './components/StatCard'
import RequestChart from './components/RequestChart'
import AlertTable from './components/AlertTable'
import LogTable from './components/LogTable'
import { useDashboard } from './hooks/useDashboard'
import { useWebSocket } from './hooks/useWebSocket'
import { Activity, AlertTriangle, Globe, Zap } from 'lucide-react'

function App() {
  const { metrics, loading, error } = useDashboard()
  const { alerts, connected } = useWebSocket()

  return (
    <Layout wsConnected={connected}>
      <div className="animate-fade-in">
        {/* Header */}
        <div style={{ marginBottom: '32px' }}>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 800, marginBottom: '4px' }}>
            <span className="gradient-text">Dashboard</span>
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
            Real-time log monitoring and alerting system
          </p>
        </div>

        {/* Stat Cards */}
        <div className="grid-4" style={{ marginBottom: '24px' }}>
          <StatCard
            id="stat-total-requests"
            icon={<Activity size={22} />}
            label="Total Requests (10m)"
            value={metrics?.total_requests_10m ?? '—'}
            color="blue"
          />
          <StatCard
            id="stat-error-count"
            icon={<AlertTriangle size={22} />}
            label="Errors (10m)"
            value={metrics?.total_errors_10m ?? '—'}
            color="red"
          />
          <StatCard
            id="stat-error-rate"
            icon={<Zap size={22} />}
            label="Error Rate"
            value={metrics?.error_rate != null ? `${metrics.error_rate}%` : '—'}
            color="amber"
          />
          <StatCard
            id="stat-unique-ips"
            icon={<Globe size={22} />}
            label="Unique IPs (10m)"
            value={metrics?.unique_ips_10m ?? '—'}
            color="green"
          />
        </div>

        {/* Charts Row */}
        <div className="grid-2" style={{ marginBottom: '24px' }}>
          <RequestChart
            id="chart-requests"
            data={metrics?.time_series ?? []}
            loading={loading}
          />
          <AlertTable
            id="alert-table"
            alerts={alerts}
          />
        </div>

        {/* Log Table */}
        <LogTable
          id="log-table"
          data={metrics?.time_series ?? []}
        />
      </div>
    </Layout>
  )
}

export default App
