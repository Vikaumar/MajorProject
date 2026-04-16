import { useEffect, useState } from 'react';
import Plot from '../components/Plot';
import { fetchJSON } from '../api';
import { COLORS, PALETTE, chartLayout } from '../chartConfig';
import HeroHeader from '../components/HeroHeader';
import SectionHeader from '../components/SectionHeader';
import Loading from '../components/Loading';

export default function ComparativeAnalytics() {
  const [clusters, setClusters] = useState(null);
  const [cfg, setCfg] = useState(null);
  const [selectedTickers, setSelectedTickers] = useState(['XOM', 'ICLN', 'SPY']);
  const [compareData, setCompareData] = useState(null);

  useEffect(() => {
    fetchJSON('/api/clusters').then(setClusters);
    fetchJSON('/api/config').then(setCfg);
  }, []);

  useEffect(() => {
    if (selectedTickers.length > 0) {
      fetchJSON(`/api/compare?tickers=${selectedTickers.join(',')}`).then(setCompareData);
    }
  }, [selectedTickers]);

  if (!clusters || !cfg) return <Loading />;

  const ranked = [...clusters.assets].sort((a, b) => b.RVI - a.RVI);

  function toggleTicker(t) {
    setSelectedTickers((prev) =>
      prev.includes(t) ? prev.filter((x) => x !== t) : [...prev, t]
    );
  }

  return (
    <>
      <HeroHeader
        title="Comparative Analytics"
        subtitle="Head-to-head analysis of fossil fuel vs. ESG / clean energy assets across risk velocity dimensions"
      />

      {/* Ranking Table */}
      <SectionHeader icon="🏆" text="Asset Risk Velocity Ranking" />
      <div className="table-wrapper" style={{ marginBottom: 24 }}>
        <table className="styled-table">
          <thead>
            <tr><th>#</th><th>Ticker</th><th>Category</th><th>RVI</th><th>ξ</th><th>σ</th><th>Risk Level</th></tr>
          </thead>
          <tbody>
            {ranked.map((a, idx) => {
              const catCls = a.category === 'Fossil Fuel' ? 'fossil' : a.category === 'ESG / Clean Energy' ? 'esg' : 'benchmark';
              const medal = idx === 0 ? '🥇' : idx === 1 ? '🥈' : idx === 2 ? '🥉' : idx + 1;
              return (
                <tr key={a.ticker}>
                  <td className="td-center">{medal}</td>
                  <td className="td-bold">{a.ticker}</td>
                  <td><span className={`cat-badge ${catCls}`}>{a.category}</span></td>
                  <td className="td-mono">{a.RVI?.toFixed(6)}</td>
                  <td className="td-mono">{a.xi?.toFixed(4)}</td>
                  <td className="td-mono">{a.sigma?.toFixed(4)}</td>
                  <td>{a.clusterLabel}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Multi-Asset RVI Overlay */}
      <SectionHeader icon="📈" text="Multi-Asset RVI Time Series" />
      <div className="control-bar">
        <div className="multi-select-wrap">
          {cfg.allTickers.map((t) => (
            <button
              key={t}
              className={`chip ${selectedTickers.includes(t) ? 'selected' : ''}`}
              onClick={() => toggleTicker(t)}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      {compareData && Object.keys(compareData).length > 0 && (
        <div className="chart-container">
          <Plot
            data={Object.entries(compareData).map(([ticker, d], i) => ({
              type: 'scatter',
              mode: 'lines',
              x: d.dates,
              y: d.rvi,
              name: ticker,
              line: { color: PALETTE[i % PALETTE.length], width: 2 },
              hovertemplate: `<b>${ticker}</b><br>%{x}<br>RVI: %{y:.6f}<extra></extra>`,
            }))}
            layout={chartLayout({
              height: 450,
              title: { text: 'RVI Comparison Across Selected Assets', font: { size: 16 } },
              yaxis: { ...chartLayout().yaxis, title: 'Risk Velocity Index' },
              xaxis: { ...chartLayout().xaxis, title: 'Date' },
            })}
            useResizeHandler
            style={{ width: '100%' }}
            config={{ displayModeBar: false }}
          />
        </div>
      )}

      {/* Fossil Fuel vs ESG Scatter */}
      <SectionHeader icon="⚔️" text="Fossil Fuel vs ESG — Risk-Velocity Scatter" />
      <div className="chart-container">
        <Plot
          data={clusters.assets.map((a) => ({
            type: 'scatter',
            mode: 'markers+text',
            x: [a.dxiDt],
            y: [a.dsigmaDt],
            text: [a.ticker],
            textposition: 'top center',
            textfont: { color: '#94a3b8', size: 10 },
            marker: {
              size: Math.max(a.RVI * 8000 + 10, 10),
              color: COLORS[a.category] || '#94a3b8',
              opacity: 0.8,
              line: { width: 1, color: 'rgba(255,255,255,0.3)' },
            },
            name: a.category,
            showlegend: false,
            hovertemplate: `<b>${a.ticker}</b><br>dξ/dt: ${a.dxiDt?.toFixed(6)}<br>dσ/dt: ${a.dsigmaDt?.toFixed(6)}<br>RVI: ${a.RVI?.toFixed(6)}<extra></extra>`,
          }))}
          layout={chartLayout({
            height: 500,
            title: { text: 'Assets in Velocity Space (dξ/dt vs dσ/dt)', font: { size: 16 } },
            xaxis: { ...chartLayout().xaxis, title: 'dξ/dt (Shape Velocity)' },
            yaxis: { ...chartLayout().yaxis, title: 'dσ/dt (Scale Velocity)' },
            shapes: [
              { type: 'line', x0: 0, x1: 1, xref: 'paper', y0: 0, y1: 0, line: { color: 'rgba(100,116,139,0.2)', width: 1 } },
              { type: 'line', y0: 0, y1: 1, yref: 'paper', x0: 0, x1: 0, line: { color: 'rgba(100,116,139,0.2)', width: 1 } },
            ],
          })}
          useResizeHandler
          style={{ width: '100%' }}
          config={{ displayModeBar: false }}
        />
      </div>
    </>
  );
}
