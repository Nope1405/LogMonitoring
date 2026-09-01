import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  Area,
  AreaChart,
} from 'recharts'
import { format } from 'date-fns'

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null

  return (
    <div
      style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border-light)',
        borderRadius: 'var(--radius-md)',
        padding: '12px 16px',
        boxShadow: 'var(--shadow-lg)',
      }}
    >
      <p style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginBottom: '8px' }}>
        {label}
      </p>
      {payload.map((entry, index) => (
        <div key={index} style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
          <span style={{ width: 8, height: 8, borderRadius: '50%', background: entry.color }} />
          <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{entry.name}:</span>
          <span style={{ fontSize: '0.8rem', fontWeight: 600, fontFamily: 'var(--font-mono)' }}>
            {entry.value}
          </span>
        </div>
      ))}
    </div>
  )
}

export default function RequestChart({ id, data, loading }) {
  const chartData = data.map((item) => ({
    ...item,
    time: item.time_bucket
      ? format(new Date(item.time_bucket), 'HH:mm')
      : '',
  }))

  return (
    <div className="card" id={id}>
      <div className="card-header">
        <span className="card-title">Requests Over Time (10 min)</span>
        {loading && <div className="loading-spinner" style={{ width: 18, height: 18, borderWidth: 2 }} />}
      </div>

      {chartData.length === 0 ? (
        <div className="empty-state" style={{ minHeight: 240 }}>
          <p>No data available yet</p>
          <p style={{ fontSize: '0.8rem', marginTop: '4px' }}>
            Start the simulator to generate log events
          </p>
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={280}>
          <AreaChart data={chartData} margin={{ top: 5, right: 10, left: -10, bottom: 5 }}>
            <defs>
              <linearGradient id="gradientRequests" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.3} />
                <stop offset="100%" stopColor="#3b82f6" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="gradientErrors" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#ef4444" stopOpacity={0.3} />
                <stop offset="100%" stopColor="#ef4444" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" />
            <XAxis
              dataKey="time"
              stroke="var(--text-muted)"
              fontSize={11}
              fontFamily="var(--font-mono)"
              tickLine={false}
            />
            <YAxis
              stroke="var(--text-muted)"
              fontSize={11}
              fontFamily="var(--font-mono)"
              tickLine={false}
              axisLine={false}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{
                fontSize: '0.75rem',
                fontFamily: 'var(--font-sans)',
              }}
            />
            <Area
              type="monotone"
              dataKey="total_requests"
              name="Total Requests"
              stroke="#3b82f6"
              strokeWidth={2}
              fill="url(#gradientRequests)"
              dot={false}
              activeDot={{ r: 4, fill: '#3b82f6' }}
            />
            <Area
              type="monotone"
              dataKey="error_count"
              name="Errors"
              stroke="#ef4444"
              strokeWidth={2}
              fill="url(#gradientErrors)"
              dot={false}
              activeDot={{ r: 4, fill: '#ef4444' }}
            />
          </AreaChart>
        </ResponsiveContainer>
      )}
    </div>
  )
}
