import { useEffect, useState } from 'react';
import Plot from '../components/Plot';
import { fetchJSON } from '../api';
import { COLORS, chartLayout } from '../chartConfig';
import HeroHeader from '../components/HeroHeader';
import MetricCard from '../components/MetricCard';
import SectionHeader from '../components/SectionHeader';
import Loading from '../components/Loading';

export default function AssetDeepDive() {
  const [tickers, setTickers] = useState([]);
  const [selected, setSelected] = useState('');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchJSON('/api/config').then((cfg) => {
      setTickers(cfg.allTickers);
      setSelected(cfg.allTickers[0] || '');
    });
  }, []);

  useEffect(() => {
    if (!selected) return;
    setLoading(true);
    fetchJSON(`/api/asset/${selected}`)
      .then(setData)
      .finally(() => setLoading(false));
  }, [selected]);

  const catCls = data?.category === 'Fossil Fuel' ? 'fossil' : data?.category === 'ESG / Clean Energy' ? 'esg' : 'benchmark';
  const cColor = data ? (COLORS[data.category] || '#94a3b8') : '#94a3b8';

  function hexToRgba(hex, alpha) {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return `rgba(${r},${g},${b},${alpha})`;
  }

  return (
    <>
      <HeroHeader
        title="Asset Deep Dive"
        subtitle="Comprehensive risk velocity analysis for individual assets with GPD parameter evolution"
      />

      {/* Asset Selector */}
      <div className="control-bar">
        <select className="select-input" value={selected} onChange={(e) => setSelected(e.target.value)}>
          {tickers.map((t) => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>
      </div>

      {loading && <Loading />}

      {!loading && data && (
        <>
          {/* Asset Info Cards */}
          <div className="metric-grid">
            <div className="glass-card" style={{ '--card-accent': cColor }}>
              <div className="card-label">Category</div>
              <span className={`cat-badge ${catCls}`} style={{ fontSize: 14, padding: '5px 14px' }}>{data.category}</span>
            </div>
            <MetricCard icon="⚡" label="Mean RVI" value={data.meanRVI?.toFixed(6)} accent={cColor} />
            <MetricCard icon="🔺" label="Max RVI" value={data.maxRVI?.toFixed(6)} accent="#ef4444" />
            <MetricCard icon="📊" label="90th Pctl" value={data.p90RVI?.toFixed(6)} accent="#eab308" />
          </div>

          {/* RVI Time Series */}
          <SectionHeader icon="📈" text={`${selected} — Risk Velocity Index Over Time`} />
          <div className="chart-container">
            <Plot
              data={[
                {
                  type: 'scatter',
                  mode: 'lines',
                  x: data.dates,
                  y: data.rvi,
                  name: 'RVI',
                  line: { color: cColor, width: 2 },
                  fill: 'tozeroy',
                  fillcolor: hexToRgba(cColor, 0.15),
                  hovertemplate: '<b>%{x}</b><br>RVI: %{y:.6f}<extra></extra>',
                },
              ]}
              layout={chartLayout({
                height: 400,
                title: { text: `Cumulative Risk Velocity Index — ${selected}`, font: { size: 16 } },
                yaxis: { ...chartLayout().yaxis, title: 'RVI' },
                shapes: [
                  {
                    type: 'line', x0: data.dates[0], x1: data.dates[data.dates.length - 1],
                    y0: data.p90RVI, y1: data.p90RVI,
                    line: { color: '#eab308', width: 1.5, dash: 'dash' },
                  },
                ],
                annotations: [
                  {
                    x: data.dates[data.dates.length - 1], y: data.p90RVI,
                    text: '90th Percentile', showarrow: false,
                    font: { color: '#eab308', size: 11 }, xanchor: 'right', yshift: 10,
                  },
                ],
              })}
              useResizeHandler
              style={{ width: '100%' }}
              config={{ displayModeBar: false }}
            />
          </div>

          {/* GPD Parameters */}
          <SectionHeader icon="🔬" text="GPD Parameter Evolution" />
          <div className="split-row">
            <div className="chart-container">
              <Plot
                data={[
                  {
                    type: 'scatter', mode: 'lines', x: data.dates, y: data.xi,
                    name: 'ξ(t)', line: { color: '#a855f7', width: 1.8 },
                    hovertemplate: '<b>%{x}</b><br>ξ: %{y:.6f}<extra></extra>',
                  },
                ]}
                layout={chartLayout({
                  height: 320,
                  title: { text: 'Shape Parameter ξ(t)', font: { size: 14 } },
                  yaxis: { ...chartLayout().yaxis, title: 'ξ (shape)' },
                })}
                useResizeHandler style={{ width: '100%' }} config={{ displayModeBar: false }}
              />
            </div>
            <div className="chart-container">
              <Plot
                data={[
                  {
                    type: 'scatter', mode: 'lines', x: data.dates, y: data.sigma,
                    name: 'σ(t)', line: { color: '#06b6d4', width: 1.8 },
                    hovertemplate: '<b>%{x}</b><br>σ: %{y:.6f}<extra></extra>',
                  },
                ]}
                layout={chartLayout({
                  height: 320,
                  title: { text: 'Scale Parameter σ(t)', font: { size: 14 } },
                  yaxis: { ...chartLayout().yaxis, title: 'σ (scale)' },
                })}
                useResizeHandler style={{ width: '100%' }} config={{ displayModeBar: false }}
              />
            </div>
          </div>

          {/* Velocity Derivatives */}
          <SectionHeader icon="🏎️" text="Parameter Velocity (Derivatives)" />
          <div className="split-row">
            <div className="chart-container">
              <Plot
                data={[
                  {
                    type: 'scatter', mode: 'lines', x: data.dates, y: data.dxiDt,
                    name: 'dξ/dt', line: { color: '#f97316', width: 1.5 },
                    fill: 'tozeroy', fillcolor: 'rgba(249,115,22,0.08)',
                  },
                ]}
                layout={chartLayout({
                  height: 280,
                  title: { text: 'dξ/dt — Shape Velocity', font: { size: 14 } },
                  yaxis: { ...chartLayout().yaxis, title: 'dξ/dt' },
                  shapes: [{ type: 'line', x0: 0, x1: 1, xref: 'paper', y0: 0, y1: 0, line: { color: 'rgba(100,116,139,0.3)', width: 1 } }],
                })}
                useResizeHandler style={{ width: '100%' }} config={{ displayModeBar: false }}
              />
            </div>
            <div className="chart-container">
              <Plot
                data={[
                  {
                    type: 'scatter', mode: 'lines', x: data.dates, y: data.dsigmaDt,
                    name: 'dσ/dt', line: { color: '#10b981', width: 1.5 },
                    fill: 'tozeroy', fillcolor: 'rgba(16,185,129,0.08)',
                  },
                ]}
                layout={chartLayout({
                  height: 280,
                  title: { text: 'dσ/dt — Scale Velocity', font: { size: 14 } },
                  yaxis: { ...chartLayout().yaxis, title: 'dσ/dt' },
                  shapes: [{ type: 'line', x0: 0, x1: 1, xref: 'paper', y0: 0, y1: 0, line: { color: 'rgba(100,116,139,0.3)', width: 1 } }],
                })}
                useResizeHandler style={{ width: '100%' }} config={{ displayModeBar: false }}
              />
            </div>
          </div>
        </>
      )}
    </>
  );
}
