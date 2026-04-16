export default function SectionHeader({ icon, text }) {
  return (
    <div className="section-header">
      <div className="section-header-icon">{icon}</div>
      <div className="section-header-text">{text}</div>
    </div>
  );
}
