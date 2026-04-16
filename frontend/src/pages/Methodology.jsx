import { useEffect, useState } from 'react';
import { fetchJSON } from '../api';
import HeroHeader from '../components/HeroHeader';
import SectionHeader from '../components/SectionHeader';
import Loading from '../components/Loading';

const PIPELINE_STEPS = [
  { num: '1', title: 'Data Ingestion', desc: 'Historical price data collection via Yahoo Finance for fossil fuel, ESG, and benchmark assets' },
  { num: '2', title: 'EVT / GPD Fitting', desc: 'Rolling-window Peaks-Over-Threshold with Generalized Pareto Distribution parameter estimation' },
  { num: '3', title: 'Temporal Derivatives', desc: 'Savitzky-Golay smoothing and numerical differentiation of ξ(t) and σ(t) to obtain risk velocities' },
  { num: '4', title: 'Clustering & Detection', desc: 'K-Means clustering in parameter space with transition probability analysis and Risk Velocity Alert detection' },
];

export default function Methodology() {
  const [cfg, setCfg] = useState(null);

  useEffect(() => {
    fetchJSON('/api/config').then(setCfg).catch(() => {});
  }, []);

  if (!cfg) return <Loading />;

  const paramsData = [
    ['Rolling Window', cfg.rollingWindow, '~1 trading year for GPD fitting'],
    ['POT Quantile', cfg.potQuantile, '90th percentile threshold for exceedances'],
    ['Min Exceedances', cfg.minExceedances, 'Minimum data points for valid GPD fit'],
    ['Smoothing Window', cfg.smoothingWindow, 'Savitzky-Golay window (must be odd)'],
    ['Smoothing Poly', cfg.smoothingPoly, 'Polynomial order for smoothing filter'],
    ['N Clusters', cfg.nClusters, 'K-Means cluster count (Safe/Warning/Crash)'],
    ['RVI Weight ξ', cfg.velocityWeightXi, 'Weight of dξ/dt in RVI formula'],
    ['RVI Weight σ', cfg.velocityWeightSigma, 'Weight of dσ/dt in RVI formula'],
  ];

  return (
    <>
      <HeroHeader
        title="Methodology & Theoretical Framework"
        subtitle="Formal description of the Temporal EVT-Clustering approach to quantifying climate transition risk velocity"
      />

      {/* Pipeline Overview */}
      <SectionHeader icon="🔬" text="Research Pipeline Overview" />
      <div className="method-grid">
        {PIPELINE_STEPS.map((step) => (
          <div className="method-card" key={step.num}>
            <div className="method-step">{step.num}</div>
            <div className="method-title">{step.title}</div>
            <div className="method-desc">{step.desc}</div>
          </div>
        ))}
      </div>

      {/* Mathematical Formulations */}
      <SectionHeader icon="📐" text="Key Mathematical Formulations" />

      <div className="formula-block">
        GPD CDF: &nbsp; G<sub>ξ,σ</sub>(x) = 1 − (1 + ξx / σ)<sup>−1/ξ</sup>, &nbsp; x &gt; 0
      </div>

      <div className="split-row" style={{ marginTop: 16 }}>
        <div>
          <div className="info-panel">
            <h4>Risk Velocity Index (RVI)</h4>
            <p>
              The composite Risk Velocity Index combines the temporal derivatives of both GPD parameters
              using configurable weights to create a single measure of how rapidly an asset's tail-risk
              profile is evolving.
            </p>
          </div>
          <div className="formula-block">
            RVI(t) = w<sub>ξ</sub> |dξ/dt| + w<sub>σ</sub> |dσ/dt|
          </div>
          <div style={{ color: '#64748b', fontSize: 12, marginTop: 8, paddingLeft: 4 }}>
            Current weights: w<sub>ξ</sub> = {cfg.velocityWeightXi}, w<sub>σ</sub> = {cfg.velocityWeightSigma}
          </div>
        </div>
        <div>
          <div className="info-panel">
            <h4>Risk Velocity Alert Detection</h4>
            <p>
              An asset triggers a <b>Risk Velocity Alert</b> (Warning State) when its recent average RVI exceeds a
              critical threshold derived from the cross-sectional distribution of all asset RVI values,
              indicating abnormally rapid tail-risk evolution toward the Warning state.
            </p>
          </div>
          <div className="formula-block">
            Warning Alert: &nbsp; R̄VI<sub>recent</sub> &gt; μ<sub>RVI</sub> + 2σ<sub>RVI</sub>
          </div>
        </div>
      </div>

      {/* Configuration Parameters */}
      <SectionHeader icon="⚙️" text="Configuration Parameters" />
      <div className="table-wrapper" style={{ marginBottom: 24 }}>
        <table className="styled-table">
          <thead>
            <tr><th>Parameter</th><th>Value</th><th>Description</th></tr>
          </thead>
          <tbody>
            {paramsData.map(([name, val, desc]) => (
              <tr key={name}>
                <td style={{ fontWeight: 600, color: '#a855f7' }}>{name}</td>
                <td className="td-mono">{val}</td>
                <td style={{ color: '#64748b' }}>{desc}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Data Universe */}
      <SectionHeader icon="📊" text="Data Universe" />
      <div className="info-panel">
        <p style={{ lineHeight: 2 }}>
          <b>Date Range:</b> {cfg.startDate} → {cfg.endDate}<br />
          <b>Fossil Fuel ({cfg.fossilFuelTickers.length}):</b> {cfg.fossilFuelTickers.join(', ')}<br />
          <b>ESG / Clean Energy ({cfg.esgCleanTickers.length}):</b> {cfg.esgCleanTickers.join(', ')}<br />
          <b>Benchmark ({cfg.benchmarkTickers.length}):</b> {cfg.benchmarkTickers.join(', ')}<br />
          <b>Total Assets:</b> {cfg.allTickers.length}
        </p>
      </div>
    </>
  );
}
