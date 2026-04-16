export default function MetricCard({ icon, label, value, accent = '#4f8df5', delta, isAlert = false }) {
  const alertCls = isAlert ? 'alert-card' : '';
  return (
    <div className={`glass-card ${alertCls}`} style={{ '--card-accent': accent }}>
      <span className="card-icon">{icon}</span>
      <div className="card-label">{label}</div>
      <div className="card-value">{value}</div>
      {delta && (
        <div className={`card-delta ${delta.includes('↑') ? 'up' : 'down'}`}>{delta}</div>
      )}
    </div>
  );
}
