import { format } from 'date-fns'

export default function LogTable({ id, data }) {
  return (
    <div className="card" id={id}>
      <div className="card-header">
        <span className="card-title">Time-Bucket Summary</span>
      </div>

      {data.length === 0 ? (
        <div className="empty-state" style={{ minHeight: 120 }}>
          <p>No log data available</p>
        </div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table className="alert-table">
            <thead>
              <tr>
                <th>Time Bucket</th>
                <th>Total</th>
                <th>Errors</th>
                <th>404s</th>
                <th>5xx</th>
                <th>Avg Response (ms)</th>
              </tr>
            </thead>
            <tbody>
              {data.map((row, index) => {
                const hasErrors = row.server_error_count > 0
                return (
                  <tr
                    key={index}
                    style={{
                      background: hasErrors ? 'var(--accent-red-glow)' : undefined,
                    }}
                  >
                    <td className="mono" style={{ fontSize: '0.8rem' }}>
                      {row.time_bucket
                        ? format(new Date(row.time_bucket), 'HH:mm')
                        : '—'}
                    </td>
                    <td className="mono" style={{ fontWeight: 600 }}>
                      {row.total_requests}
                    </td>
                    <td className="mono" style={{
                      color: row.error_count > 0 ? 'var(--accent-red)' : 'var(--text-secondary)',
                      fontWeight: row.error_count > 0 ? 600 : 400,
                    }}>
                      {row.error_count}
                    </td>
                    <td className="mono" style={{
                      color: row.not_found_count > 0 ? 'var(--accent-amber)' : 'var(--text-secondary)',
                    }}>
                      {row.not_found_count}
                    </td>
                    <td className="mono" style={{
                      color: row.server_error_count > 0 ? 'var(--accent-red)' : 'var(--text-secondary)',
                      fontWeight: row.server_error_count > 0 ? 700 : 400,
                    }}>
                      {row.server_error_count}
                    </td>
                    <td className="mono" style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      {row.avg_response_time != null
                        ? `${Number(row.avg_response_time).toFixed(1)}`
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
