import { useEffect, useState } from 'react';
import { fetchJSON } from '../api';

const NAV_ITEMS = [
  { id: 'summary', icon: '🏠', label: 'Executive Summary' },
  { id: 'heatmap', icon: '🔥', label: 'Risk Velocity Heatmap' },
  { id: 'deepdive', icon: '🔍', label: 'Asset Deep Dive' },
  { id: 'clusters', icon: '🎯', label: 'Cluster Analysis' },
  { id: 'compare', icon: '📈', label: 'Comparative Analytics' },
  { id: 'backtest', icon: '🧪', label: 'Backtest Results' },
  { id: 'methodology', icon: '📚', label: 'Methodology & Theory' },
];

export default function Sidebar({ activePage, onNavigate }) {
  const [cfg, setCfg] = useState(null);

  useEffect(() => {
    fetchJSON('/api/config').then(setCfg).catch(() => {});
  }, []);

  const catGroups = cfg
    ? [
        { name: 'Fossil Fuel', cls: 'fossil', tickers: cfg.fossilFuelTickers },
        { name: 'ESG / Clean Energy', cls: 'esg', tickers: cfg.esgCleanTickers },
        { name: 'Benchmark', cls: 'benchmark', tickers: cfg.benchmarkTickers },
      ]
    : [];

  return (
    <aside className="sidebar">
      {/* Brand */}
      <div className="sidebar-brand">
        <span className="sidebar-brand-icon">🌍</span>
        <div className="sidebar-brand-title">Climate Risk Velocity</div>
        <div className="sidebar-brand-sub">Temporal EVT-Clustering Framework</div>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav">
        {NAV_ITEMS.map((item) => (
          <div
            key={item.id}
            className={`nav-item ${activePage === item.id ? 'active' : ''}`}
            onClick={() => onNavigate(item.id)}
          >
            <span className="nav-item-icon">{item.icon}</span>
            {item.label}
          </div>
        ))}
      </nav>

      <div className="sidebar-divider" />

      {/* Data Pipeline Status */}
      <div className="sidebar-section">
        <div className="sidebar-section-title">📡 Data Pipeline Status</div>
        <div className="sidebar-status">
          <span className="status-dot green" /> {cfg ? cfg.allTickers.length : '—'} assets loaded<br />
          <span className="status-dot green" /> Pipeline complete<br />
          <span className="status-dot green" /> {cfg ? `${cfg.startDate} → ${cfg.endDate}` : '—'}
        </div>
      </div>

      <div className="sidebar-divider" />

      {/* Asset Categories */}
      <div className="sidebar-section">
        <div className="sidebar-section-title">🏷️ Asset Categories</div>
        {catGroups.map((g) => (
          <div key={g.name} style={{ marginBottom: 10 }}>
            <span className={`cat-badge ${g.cls}`}>{g.name}</span>
            <div className="sidebar-tickers">{g.tickers.join(', ')}</div>
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className="sidebar-footer">
        Framework v2.0 · React + FastAPI<br />
        Climate Risk Analytics
      </div>
    </aside>
  );
}
