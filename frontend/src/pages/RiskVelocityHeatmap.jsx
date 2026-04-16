import { useEffect, useState } from 'react';
import Plot from '../components/Plot';
import { fetchJSON } from '../api';
import { chartLayout } from '../chartConfig';
import HeroHeader from '../components/HeroHeader';
import MetricCard from '../components/MetricCard';
import SectionHeader from '../components/SectionHeader';
import Loading from '../components/Loading';

const PARAM_LABELS = {
  dxi_dt: 'dξ/dt (Shape Velocity)',
  dsigma_dt: 'dσ/dt (Scale Velocity)',
  RVI: 'Risk Velocity Index',
};

export default function RiskVelocityHeatmap() {
  const [param, setParam] = useState('RVI');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetchJSON(`/api/heatmap/${param}`)
      .then(setData)
      .finally(() => setLoading(false));
  }, [param]);

  return (
    <>
      <HeroHeader
        title="Risk Velocity Heatmap"
        subtitle="Temporal evolution of GPD parameter derivatives and composite Risk Velocity Index across all monitored assets"
      />

      {/* Parameter Selector */}
      <div className="control-bar">
        <div className="radio-group">
          {Object.entries(PARAM_LABELS).map(([key, label]) => (
            <button
              key={key}
              className={`radio-btn ${param === key ? 'active' : ''}`}
              onClick={() => setParam(key)}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {loading && <Loading />}

      {!loading && data && (
        <>
          <div className="chart-container">
            <Plot
              data={[
                {
                  type: 'heatmap',
                  z: data.values,
                  x: data.months,
                  y: data.tickers,
                  colorscale: param !== 'RVI' ? 'RdYlGn_r' : 'YlOrRd',
                  colorbar: { title: PARAM_LABELS[param], titlefont: { color: '#94a3b8' }, tickfont: { color: '#94a3b8' } },
                  hovertemplate: '<b>%{y}</b><br>Month: %{x}<br>Value: %{z:.6f}<extra></extra>',
                },
              ]}
              layout={chartLayout({
                height: 650,
                title: { text: `Monthly Average: ${PARAM_LABELS[param]}`, font: { size: 16 } },
                xaxis: { ...chartLayout().xaxis, tickangle: 45, tickfont: { size: 9 } },
                yaxis: { ...chartLayout().yaxis },
              })}
              useResizeHandler
              style={{ width: '100%' }}
              config={{ displayModeBar: false }}
            />
          </div>

          {/* Summary Statistics */}
          <SectionHeader icon="📋" text="Summary Statistics" />
          <div className="metric-grid">
            <MetricCard icon="📉" label="Minimum" value={data.stats.min.toFixed(6)} accent="#06b6d4" />
            <MetricCard icon="📊" label="Mean" value={data.stats.mean.toFixed(6)} accent="#a855f7" />
            <MetricCard icon="📈" label="Maximum" value={data.stats.max.toFixed(6)} accent="#ef4444" />
            <MetricCard icon="📐" label="Std Dev" value={data.stats.std.toFixed(6)} accent="#eab308" />
          </div>
        </>
      )}
    </>
  );
}
