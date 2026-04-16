import { useEffect, useState } from 'react';
import Plot from '../components/Plot';
import { fetchJSON } from '../api';
import { COLORS, chartLayout } from '../chartConfig';
import HeroHeader from '../components/HeroHeader';
import MetricCard from '../components/MetricCard';
import SectionHeader from '../components/SectionHeader';
import Loading from '../components/Loading';

export default function ExecutiveSummary() {
  const [overview, setOverview] = useState(null);
  const [alerts, setAlerts] = useState(null);
  const [clusters, setClusters] = useState(null);
  const [cfg, setCfg] = useState(null);

  useEffect(() => {
    fetchJSON('/api/overview').then(setOverview);
    fetchJSON('/api/alerts').then(setAlerts);
    fetchJSON('/api/clusters').then(setClusters);
    fetchJSON('/api/config').then(setCfg);
  }, []);

  if (!overview || !alerts || !clusters) return <Loading />;

  const warningAlerts = alerts.alerts.filter((a) => a.isWarningAlert);

  return (
    <>
      <HeroHeader
        title="Ecosystem Overview & Risk Intelligence"
        subtitle="Real-time monitoring of climate transition risk velocity across fossil fuel, ESG, and benchmark assets"
      />

      {/* Metric Cards */}
      <div className="metric-grid">
        <MetricCard icon="📡" label="Monitored Assets" value={overview.totalAssets} accent="#4f8df5" />
        <MetricCard icon="📅" label="Trading Days" value={overview.tradingDays.toLocaleString()} accent="#06b6d4" />
        <MetricCard icon="⚡" label="System Avg RVI" value={overview.avgRVI?.toFixed(6)} accent="#a855f7" />
        <MetricCard
          icon="🚨"
          label="Warning State Alerts"
          value={overview.warningAlerts}
          accent="#ef4444"
          isAlert={overview.warningAlerts > 0}
        />
      </div>

      {/* Warning Alerts */}
      <SectionHeader icon="🚨" text="Risk Velocity Alerts — Warning State Assets" />

      {warningAlerts.length > 0 ? (
        <div className="chart-container">
          <Plot
            data={warningAlerts.map((a) => ({
              type: 'bar',
              x: [a.ticker],
              y: [a.recentRVI],
              name: a.ticker,
              marker: { color: COLORS[a.category] || '#94a3b8', opacity: 0.9 },
              hovertemplate: `<b>${a.ticker}</b><br>Category: ${a.category}<br>RVI: %{y:.6f}<extra></extra>`,
              showlegend: false,
            }))}
            layout={chartLayout({
              height: 420,
              title: { text: 'Recent Risk Velocity Index (RVI) — Warning Alerts', font: { size: 16 } },
              xaxis: { ...chartLayout().xaxis, title: 'Asset Ticker' },
              yaxis: { ...chartLayout().yaxis, title: 'Recent Mean RVI' },
              bargap: 0.3,
              shapes: [
                {
                  type: 'line',
                  x0: 0, x1: 1, xref: 'paper',
                  y0: warningAlerts[0]?.threshold, y1: warningAlerts[0]?.threshold,
                  line: { color: '#eab308', width: 2, dash: 'dash' },
                },
              ],
              annotations: [
                {
                  x: 1, xref: 'paper', y: warningAlerts[0]?.threshold,
                  text: 'Critical Threshold', showarrow: false,
                  font: { color: '#eab308', size: 12 }, xanchor: 'right',
                },
              ],
            })}
            useResizeHandler
            style={{ width: '100%' }}
            config={{ displayModeBar: false }}
          />
        </div>
      ) : (
        <div className="info-panel success-panel">
          <div className="panel-icon">✅</div>
          <div className="panel-title">No warning alerts detected above the critical threshold</div>
          <div className="panel-desc">All assets are within normal risk velocity ranges</div>
        </div>
      )}

      {/* Category Comparison */}
      <SectionHeader icon="📊" text="Average Risk Velocity by Category" />
      <div className="chart-container">
        <Plot
          data={alerts.categoryAvg
            .sort((a, b) => a.avgRVI - b.avgRVI)
            .map((c) => ({
              type: 'bar',
              y: [c.category],
              x: [c.avgRVI],
              orientation: 'h',
              name: c.category,
              marker: { color: COLORS[c.category] || '#94a3b8', opacity: 0.85 },
              hovertemplate: `<b>${c.category}</b><br>Avg RVI: %{x:.6f}<extra></extra>`,
              showlegend: false,
            }))}
          layout={chartLayout({
            height: 300,
            title: { text: 'Category Risk Comparison', font: { size: 16 } },
            xaxis: { ...chartLayout().xaxis, title: 'Average Recent RVI' },
            yaxis: { ...chartLayout().yaxis, title: '' },
            bargap: 0.4,
          })}
          useResizeHandler
          style={{ width: '100%' }}
          config={{ displayModeBar: false }}
        />
      </div>

      {/* Cluster Distribution */}
      <SectionHeader icon="🎯" text="Current Risk Cluster Distribution" />
      <div className="split-row">
        <div className="chart-container">
          <Plot
            data={[
              {
                type: 'pie',
                labels: clusters.distribution.map((d) => d.label),
                values: clusters.distribution.map((d) => d.count),
                hole: 0.65,
                marker: {
                  colors: clusters.distribution.map((d) => COLORS[d.cluster] || '#94a3b8'),
                  line: { color: '#0a0f1e', width: 3 },
                },
                textinfo: 'label+percent',
                textfont: { size: 12, color: '#e2e8f0' },
                hovertemplate: '<b>%{label}</b><br>Assets: %{value}<br>Share: %{percent}<extra></extra>',
              },
            ]}
            layout={chartLayout({
              height: 350,
              title: { text: 'Cluster Composition', font: { size: 16 } },
              showlegend: false,
              annotations: [
                {
                  text: `<b>${clusters.assets.length}</b><br><span style="font-size:11px;color:#64748b">Assets</span>`,
                  x: 0.5, y: 0.5, font: { size: 24, color: '#e2e8f0' }, showarrow: false,
                },
              ],
            })}
            useResizeHandler
            style={{ width: '100%' }}
            config={{ displayModeBar: false }}
          />
        </div>

        {/* Top Risk Assets Table */}
        <div className="table-wrapper">
          <table className="styled-table">
            <thead>
              <tr><th>Ticker</th><th>Category</th><th>RVI</th><th>Risk Level</th></tr>
            </thead>
            <tbody>
              {clusters.assets
                .sort((a, b) => b.RVI - a.RVI)
                .slice(0, 8)
                .map((a) => {
                  const catCls = a.category === 'Fossil Fuel' ? 'fossil' : a.category === 'ESG / Clean Energy' ? 'esg' : 'benchmark';
                  return (
                    <tr key={a.ticker}>
                      <td className="td-bold">{a.ticker}</td>
                      <td><span className={`cat-badge ${catCls}`}>{a.category}</span></td>
                      <td className="td-mono">{a.RVI?.toFixed(6)}</td>
                      <td>{a.clusterLabel}</td>
                    </tr>
                  );
                })}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
