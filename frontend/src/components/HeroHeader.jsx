export default function HeroHeader({ title, subtitle }) {
  return (
    <div className="hero-header">
      <div className="hero-title">{title}</div>
      <div className="hero-subtitle">{subtitle}</div>
    </div>
  );
}
