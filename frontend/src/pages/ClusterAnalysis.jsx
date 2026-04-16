import { useEffect, useState } from 'react';
import Plot from '../components/Plot';
import { fetchJSON } from '../api';
import { COLORS, chartLayout } from '../chartConfig';
import HeroHeader from '../components/HeroHeader';
import SectionHeader from '../components/SectionHeader';
import Loading from '../components/Loading';

export default function ClusterAnalysis() {
  const [clusters, setClusters] = useState(null);
  const [transitions, setTransitions] = useState(null);
  const [tab, setTab] = useState('scatter');

  useEffect(() => {
    fetchJSON('/api/clusters').then(setClusters);
    fetchJSON('/api/transitions').then(setTransitions);
  }, []);

  if (!clusters || !transitions) return <Loading />;

  const clusterColorMap = { Safe: COLORS[0], Warning: COLORS[1], Crash: COLORS[2] };

  // ── Sankey data ──
  const labelsFrom = transitions.labels.map((l) => `${l} (t)`);
  const labelsTo = transitions.labels.map((l) => `${l} (t+1)`);
  const allLabels = [...labelsFrom, ...labelsTo];

  const nodeColors = [COLORS[0], COLORS[1], COLORS[2], COLORS[0], COLORS[1], COLORS[2]];
  const linkColors = transitions.links.map((lnk) => {
    const c = nodeColors[lnk.source % 3];
    const r = parseInt(c.slice(1, 3), 16);
    const g = parseInt(c.slice(3, 5), 16);
    const b = parseInt(c.slice(5, 7), 16);
    return `rgba(${r},${g},${b},0.35)`;
  });

  return (
    <>
      <HeroHeader
        title="Cluster Analysis & Migration Flows"
        subtitle="K-Means clustering in EVT parameter space with temporal transition probability analysis"
      />

      {/* Tabs */}
      <div className="tabs-bar">
        <button className={`tab-btn ${tab === 'scatter' ? 'active' : ''}`} onClick={() => setTab('scatter')}>
          🎯 EVT Parameter Space
        </button>
        <button className={`tab-btn ${tab === 'sankey' ? 'active' : ''}`} onClick={() => setTab('sankey')}>
          🔄 Transition Sankey
        </button>
      </div>

      {tab === 'scatter' && (
        <>
          <SectionHeader icon="🎯" text="EVT Cluster Scatter with Velocity Bubbles" />
          <div className="info-panel">
            <p>
              Assets are plotted in the (ξ, σ) parameter space. <b>Bubble size</b> represents Risk Velocity Index magnitude.
              <b> Color</b> indicates K-Means cluster assignment (Safe / Warning / Crash).
            </p>
          </div>
          <div className="chart-container">
            <Plot
              data={['Safe', 'Warning', 'Crash'].map((label) => {
                const group = clusters.assets.filter((a) => a.clusterLabel === label);
                return {
                  type: 'scatter',
                  mode: 'markers',
                  x: group.map((a) => a.xi),
                  y: group.map((a) => a.sigma),
                  text: group.map((a) => a.ticker),
                  name: label,
                  marker: {
                    size: group.map((a) => Math.max(a.RVI * 3000 + 8, 8)),
                    color: clusterColorMap[label],
                    opacity: 0.85,
                    line: { width: 1.5, color: 'rgba(255,255,255,0.4)' },
                  },
                  hovertemplate: group.map(
                    (a) =>
                      `<b>${a.ticker}</b><br>Category: ${a.category}<br>ξ: ${a.xi?.toFixed(4)}<br>σ: ${a.sigma?.toFixed(4)}<br>RVI: ${a.RVI?.toFixed(6)}<extra></extra>`
                  ),
                };
              })}
              layout={chartLayout({
                height: 600,
                title: { text: 'Asset Clustering in EVT Parameter Space', font: { size: 16 } },
                xaxis: { ...chartLayout().xaxis, title: 'Shape Parameter (ξ)' },
                yaxis: { ...chartLayout().yaxis, title: 'Scale Parameter (σ)' },
              })}
              useResizeHandler
              style={{ width: '100%' }}
              config={{ displayModeBar: false }}
            />
          </div>
        </>
      )}

      {tab === 'sankey' && (
        <>
          <SectionHeader icon="🔄" text="Cluster Transition Probabilities" />
          <div className="info-panel">
            <p>
              Sankey diagram showing the probability of assets migrating between risk clusters across consecutive time windows.
              Flow width is proportional to transition probability (%).
            </p>
          </div>
          <div className="chart-container">
            <Plot
              data={[
                {
                  type: 'sankey',
                  orientation: 'h',
                  node: {
                    pad: 25,
                    thickness: 30,
                    label: allLabels,
                    color: nodeColors.slice(0, allLabels.length),
                    line: { color: 'rgba(255,255,255,0.15)', width: 1 },
                  },
                  link: {
                    source: transitions.links.map((l) => l.source),
                    target: transitions.links.map((l) => l.target),
                    value: transitions.links.map((l) => l.value),
                    color: linkColors,
                    label: transitions.links.map((l) => `${l.value}%`),
                  },
                },
              ]}
              layout={chartLayout({
                height: 550,
                title: { text: 'Cluster Migration Flow (Transition Probabilities)', font: { size: 16 } },
              })}
              useResizeHandler
              style={{ width: '100%' }}
              config={{ displayModeBar: false }}
            />
          </div>
        </>
      )}
    </>
  );
}
