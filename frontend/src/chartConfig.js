/* Shared Plotly layout settings — mirrors the Streamlit design */
export const CHART_LAYOUT = {
  paper_bgcolor: 'rgba(0,0,0,0)',
  plot_bgcolor: 'rgba(6,8,15,0.4)',
  font: { family: 'Inter, sans-serif', color: '#94a3b8', size: 12 },
  title: { font: { family: 'Inter, sans-serif', color: '#e2e8f0', size: 16 } },
  legend: {
    bgcolor: 'rgba(0,0,0,0)',
    bordercolor: 'rgba(100,116,139,0.15)',
    borderwidth: 1,
    font: { size: 11, color: '#94a3b8' },
  },
  margin: { l: 60, r: 30, t: 60, b: 50 },
  xaxis: { gridcolor: 'rgba(100,116,139,0.08)', zerolinecolor: 'rgba(100,116,139,0.1)' },
  yaxis: { gridcolor: 'rgba(100,116,139,0.08)', zerolinecolor: 'rgba(100,116,139,0.1)' },
  hoverlabel: { bgcolor: '#0f1d35', bordercolor: '#4f8df5', font: { size: 12, family: 'Inter' } },
};

export const COLORS = {
  'Fossil Fuel': '#ef4444',
  'ESG / Clean Energy': '#06b6d4',
  'Benchmark': '#eab308',
  0: '#06b6d4',
  1: '#eab308',
  2: '#ef4444',
};

export const PALETTE = ['#ef4444', '#06b6d4', '#eab308', '#a855f7', '#f97316', '#10b981', '#ec4899', '#6366f1'];

export function chartLayout(overrides = {}) {
  return { ...CHART_LAYOUT, ...overrides };
}
