export default function StatCard({ id, icon, label, value, color = 'blue' }) {
  return (
    <div className="stat-card" id={id}>
      <div className={`stat-icon ${color}`}>
        {icon}
      </div>
      <div>
        <div className="stat-value">{value}</div>
        <div className="stat-label">{label}</div>
      </div>
    </div>
  )
}
