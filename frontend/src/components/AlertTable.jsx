import { format } from 'date-fns'
import { AlertTriangle, AlertCircle, Info } from 'lucide-react'

const severityConfig = {
  critical: { icon: AlertCircle, className: 'critical' },
  warning: { icon: AlertTriangle, className: 'warning' },
  info: { icon: Info, className: 'info' },
}

export default function AlertTable({ id, alerts }) {
  return (
    <div className="card" id={id}>
      <div className="card-header">
        <span className="card-title">Live Alerts</span>
        <span
          className="badge critical"
          style={{
            visibility: alerts.length > 0 ? 'visible' : 'hidden',
          }}
        >
          {alerts.length} active
        </span>
      </div>

      {alerts.length === 0 ? (
        <div className="empty-state" style={{ minHeight: 240 }}>
          <AlertTriangle size={32} />
          <p>No alerts detected</p>
          <p style={{ fontSize: '0.8rem', marginTop: '4px' }}>
            Alerts will appear when anomalies are detected
          </p>
        </div>
      ) : (
        <div style={{ maxHeight: 300, overflowY: 'auto' }}>
          <table className="alert-table">
            <thead>
              <tr>
                <th>Severity</th>
                <th>Type</th>
                <th>Message</th>
                <th>Time</th>
              </tr>
            </thead>
            <tbody>
              {alerts.slice(0, 20).map((alert, index) => {
                const config = severityConfig[alert.severity] || severityConfig.info
                const Icon = config.icon

                return (
                  <tr key={alert.id || index} className="animate-slide-in">
                    <td>
                      <span className={`badge ${config.className}`}>
                        <Icon size={12} />
                        {alert.severity}
                      </span>
                    </td>
                    <td>
                      <span className="mono" style={{ fontSize: '0.8rem' }}>
                        {alert.alert_type}
                      </span>
                    </td>
                    <td style={{ maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {alert.message}
                    </td>
                    <td className="mono" style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      {alert.created_at
                        ? format(new Date(alert.created_at), 'HH:mm:ss')
                        : '—'}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
