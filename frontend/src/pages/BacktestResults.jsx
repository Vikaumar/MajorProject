import { useEffect, useState } from 'react';
import Plot from '../components/Plot';
import { fetchJSON } from '../api';
import { PALETTE, chartLayout } from '../chartConfig';
import HeroHeader from '../components/HeroHeader';
import SectionHeader from '../components/SectionHeader';
import MetricCard from '../components/MetricCard';
import Loading from '../components/Loading';

const METHOD_COLORS = {
  'EVT-Clustering (Ours)': '#a855f7',
  'VaR': '#ef4444',
  'ES': '#f97316',
  'Volatility': '#06b6d4',
};

export default function BacktestResults() {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetchJSON('/api/backtesting').then(setData).catch(() => {});
  }, []);

  if (!data) return <Loading />;

  const { trainEnd, testStart, backtestHorizon, assetResults, aggregate, baselines, ablation } = data;

  return (
    <>
      <HeroHeader
        title="Out-of-Sample Backtesting Results"
        subtitle={`Model trained on data up to ${trainEnd}, evaluated exclusively on the unseen test period (${testStart} onward)`}
      />

      {/* Aggregate Metrics */}
      {aggregate && (
        <div className="metric-grid">
          <MetricCard icon="🎯" label="Precision" value={aggregate.Precision?.toFixed(4)} accent="#22c55e" />
          <MetricCard icon="📡" label="Recall" value={aggregate.Recall?.toFixed(4)} accent="#3b82f6" />
          <MetricCard icon="⚡" label="F1-Score" value={aggregate.F1?.toFixed(4)} accent="#a855f7" />
          <MetricCard icon="⏱️" label="Avg Lead Time" value={`${aggregate.mean_lead_time} days`} accent="#f59e0b" />
        </div>
      )}

      {/* Train/Test Info Banner */}
      <div className="info-panel" style={{ borderLeft: '3px solid #a855f7', marginBottom: 24 }}>
        <p style={{ lineHeight: 1.8, margin: 0 }}>
          <b>Train Period:</b> up to {trainEnd} (KMeans.fit) &nbsp;|&nbsp;
          <b>Test Period:</b> {testStart} onward (KMeans.predict only) &nbsp;|&nbsp;
          <b>Backtest Horizon:</b> {backtestHorizon} trading days
        </p>
      </div>

      {/* Baseline Comparison Chart */}
      <SectionHeader icon="📊" text="Framework vs Baseline Comparisons (Test Set Only)" />
      {baselines.length > 0 && (
        <div className="chart-container">
          <Plot
            data={['Precision', 'Recall', 'F1'].map((metric, i) => ({
              type: 'bar',
              name: metric,
              x: baselines.map((b) => b.name),
              y: baselines.map((b) => b[metric]),
              marker: { color: [PALETTE[0], PALETTE[1], PALETTE[2]][i], opacity: 0.85 },
              hovertemplate: `<b>%{x}</b><br>${metric}: %{y:.4f}<extra></extra>`,
            }))}
            layout={chartLayout({
              height: 420,
              title: { text: 'Out-of-Sample Signal Quality: EVT-Clustering vs Baselines', font: { size: 16 } },
              xaxis: { ...chartLayout().xaxis, title: 'Method' },
              yaxis: { ...chartLayout().yaxis, title: 'Score', range: [0, 1] },
              barmode: 'group',
              bargap: 0.2,
              bargroupgap: 0.1,
            })}
            useResizeHandler
            style={{ width: '100%' }}
            config={{ displayModeBar: false }}
          />
        </div>
      )}

      {/* Baseline Table */}
      {baselines.length > 0 && (
        <div className="table-wrapper" style={{ marginBottom: 24 }}>
          <table className="styled-table">
            <thead>
              <tr><th>Method</th><th>TP</th><th>FP</th><th>FN</th><th>Precision</th><th>Recall</th><th>F1</th><th>Lead Time (days)</th></tr>
            </thead>
            <tbody>
              {baselines.map((b) => (
                <tr key={b.name} style={b.name === 'EVT-Clustering (Ours)' ? { background: 'rgba(168,85,247,0.1)' } : {}}>
                  <td style={{ fontWeight: b.name === 'EVT-Clustering (Ours)' ? 700 : 400, color: METHOD_COLORS[b.name] || '#e2e8f0' }}>
                    {b.name}
                  </td>
                  <td className="td-mono">{b.TP}</td>
                  <td className="td-mono">{b.FP}</td>
                  <td className="td-mono">{b.FN}</td>
                  <td className="td-mono">{b.Precision?.toFixed(4)}</td>
                  <td className="td-mono">{b.Recall?.toFixed(4)}</td>
                  <td className="td-mono" style={{ fontWeight: 600 }}>{b.F1?.toFixed(4)}</td>
                  <td className="td-mono">{b.mean_lead_time}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Lead Time Comparison */}
      {baselines.length > 0 && (
        <>
          <SectionHeader icon="⏱️" text="Lead Time Comparison (Days Before Crash)" />
          <div className="chart-container">
            <Plot
              data={[{
                type: 'bar',
                x: baselines.map((b) => b.name),
                y: baselines.map((b) => b.mean_lead_time || 0),
                marker: {
                  color: baselines.map((b) => METHOD_COLORS[b.name] || '#64748b'),
                  opacity: 0.85,
                },
                hovertemplate: '<b>%{x}</b><br>Lead Time: %{y:.1f} days<extra></extra>',
              }]}
              layout={chartLayout({
                height: 380,
                title: { text: 'Average Warning Lead Time (Test Set)', font: { size: 16 } },
                xaxis: { ...chartLayout().xaxis, title: 'Method' },
                yaxis: { ...chartLayout().yaxis, title: 'Lead Time (trading days)' },
                bargap: 0.3,
              })}
              useResizeHandler
              style={{ width: '100%' }}
              config={{ displayModeBar: false }}
            />
          </div>
        </>
      )}

      {/* Ablation Study */}
      {ablation.length > 0 && (
        <>
          <SectionHeader icon="🧪" text="Ablation Study — Velocity Features Impact (Test Set)" />
          <div className="split-row">
            <div className="chart-container">
              <Plot
                data={['Precision', 'Recall', 'F1'].map((metric, i) => ({
                  type: 'bar',
                  name: metric,
                  x: ablation.map((a) => a.name.length > 25 ? a.name.slice(0, 25) + '...' : a.name),
                  y: ablation.map((a) => a[metric]),
                  marker: { color: [PALETTE[0], PALETTE[1], PALETTE[2]][i], opacity: 0.85 },
                }))}
                layout={chartLayout({
                  height: 380,
                  title: { text: 'EVT-only vs EVT+Velocity', font: { size: 16 } },
                  xaxis: { ...chartLayout().xaxis },
                  yaxis: { ...chartLayout().yaxis, title: 'Score', range: [0, 1] },
                  barmode: 'group',
                  bargap: 0.2,
                })}
                useResizeHandler
                style={{ width: '100%' }}
                config={{ displayModeBar: false }}
              />
            </div>
            <div className="table-wrapper">
              <table className="styled-table">
                <thead>
                  <tr><th>Variant</th><th>Precision</th><th>Recall</th><th>F1</th><th>Lead Time</th></tr>
                </thead>
                <tbody>
                  {ablation.map((a) => (
                    <tr key={a.name}>
                      <td style={{ fontWeight: 600, color: '#a855f7', maxWidth: 220, wordBreak: 'break-word' }}>{a.name}</td>
                      <td className="td-mono">{a.Precision?.toFixed(4)}</td>
                      <td className="td-mono">{a.Recall?.toFixed(4)}</td>
                      <td className="td-mono" style={{ fontWeight: 600 }}>{a.F1?.toFixed(4)}</td>
                      <td className="td-mono">{a.mean_lead_time}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}

      {/* Per-Asset Results */}
      <SectionHeader icon="📋" text="Per-Asset Backtest Results (Test Set Only)" />
      {assetResults.length > 0 && (
        <>
          <div className="chart-container">
            <Plot
              data={[
                {
                  type: 'bar', name: 'F1-Score',
                  x: assetResults.map((a) => a.ticker),
                  y: assetResults.map((a) => a.F1),
                  marker: { color: '#a855f7', opacity: 0.85 },
                },
                {
                  type: 'bar', name: 'Precision',
                  x: assetResults.map((a) => a.ticker),
                  y: assetResults.map((a) => a.Precision),
                  marker: { color: '#22c55e', opacity: 0.7 },
                },
                {
                  type: 'bar', name: 'Recall',
                  x: assetResults.map((a) => a.ticker),
                  y: assetResults.map((a) => a.Recall),
                  marker: { color: '#3b82f6', opacity: 0.7 },
                },
              ]}
              layout={chartLayout({
                height: 420,
                title: { text: 'Per-Asset Signal Quality (Out-of-Sample)', font: { size: 16 } },
                xaxis: { ...chartLayout().xaxis, title: 'Asset' },
                yaxis: { ...chartLayout().yaxis, title: 'Score', range: [0, 1] },
                barmode: 'group',
                bargap: 0.15,
              })}
              useResizeHandler
              style={{ width: '100%' }}
              config={{ displayModeBar: false }}
            />
          </div>

          <div className="table-wrapper">
            <table className="styled-table">
              <thead>
                <tr><th>Ticker</th><th>TP</th><th>FP</th><th>FN</th><th>Precision</th><th>Recall</th><th>F1</th><th>Lead Time</th><th>Warnings</th><th>Crashes</th></tr>
              </thead>
              <tbody>
                {assetResults.map((a) => (
                  <tr key={a.ticker}>
                    <td className="td-bold">{a.ticker}</td>
                    <td className="td-mono">{a.TP}</td>
                    <td className="td-mono">{a.FP}</td>
                    <td className="td-mono">{a.FN}</td>
                    <td className="td-mono">{a.Precision?.toFixed(4)}</td>
                    <td className="td-mono">{a.Recall?.toFixed(4)}</td>
                    <td className="td-mono" style={{ fontWeight: 600 }}>{a.F1?.toFixed(4)}</td>
                    <td className="td-mono">{a.mean_lead_time ?? '—'}</td>
                    <td className="td-mono">{a.n_warnings}</td>
                    <td className="td-mono">{a.n_crashes}</td>
                  </tr>
                ))}
                {aggregate && (
                  <tr style={{ background: 'rgba(168,85,247,0.1)', fontWeight: 700 }}>
                    <td style={{ color: '#a855f7' }}>AGGREGATE</td>
                    <td className="td-mono">{aggregate.TP}</td>
                    <td className="td-mono">{aggregate.FP}</td>
                    <td className="td-mono">{aggregate.FN}</td>
                    <td className="td-mono">{aggregate.Precision?.toFixed(4)}</td>
                    <td className="td-mono">{aggregate.Recall?.toFixed(4)}</td>
                    <td className="td-mono">{aggregate.F1?.toFixed(4)}</td>
                    <td className="td-mono">{aggregate.mean_lead_time ?? '—'}</td>
                    <td className="td-mono">{aggregate.n_warnings}</td>
                    <td className="td-mono">{aggregate.n_crashes}</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </>
      )}
    </>
  );
}
