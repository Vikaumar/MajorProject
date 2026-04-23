import { useEffect, useState } from 'react';
import { fetchJSON } from '../api';
import HeroHeader from '../components/HeroHeader';
import SectionHeader from '../components/SectionHeader';
import Loading from '../components/Loading';

const PIPELINE_STEPS = [
  { num: '1', title: 'Data Ingestion', desc: 'Historical price data collection via Yahoo Finance for fossil fuel, ESG, and benchmark assets' },
  { num: '2', title: 'EVT / GPD Fitting', desc: 'Rolling-window Peaks-Over-Threshold with Generalized Pareto Distribution parameter estimation' },
  { num: '3', title: 'Temporal Derivatives', desc: 'Savitzky-Golay smoothing and numerical differentiation of \u03be(t) and \u03c3(t) to obtain risk velocities' },
  { num: '4', title: 'Train/Test Split & Clustering', desc: 'K-Means fitted on train period (\u22642018), then predict-only on test period (2019+) \u2014 prevents data leakage and overfitting' },
  { num: '5', title: 'Out-of-Sample Validation', desc: 'Precision, Recall, F1 and Lead Time computed exclusively on the unseen test set (2019\u20132025)' },
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
    ['RVI Weight \u03be', cfg.velocityWeightXi, 'Weight of d\u03be/dt in RVI formula'],
    ['RVI Weight \u03c3', cfg.velocityWeightSigma, 'Weight of d\u03c3/dt in RVI formula'],
    ['Train End', cfg.trainEnd || '2018-12-31', 'Last date for model training (KMeans.fit)'],
    ['Test Start', cfg.testStart || '2019-01-01', 'First date for out-of-sample evaluation (KMeans.predict)'],
    ['Backtest Horizon', cfg.backtestHorizon || 120, 'Trading days look-ahead for Warning\u2192Crash signal'],
  ];

  return (
    <>
      <HeroHeader
        title="Methodology & Theoretical Framework"
        subtitle="Formal description of the Temporal EVT-Clustering approach to quantifying climate transition risk velocity"
      />

      {/* Pipeline Overview */}
      <SectionHeader icon="\ud83d\udd2c" text="Research Pipeline Overview" />
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
      <SectionHeader icon="\ud83d\udcd0" text="Key Mathematical Formulations" />

      <div className="formula-block">
        GPD CDF: &nbsp; G<sub>\u03be,\u03c3</sub>(x) = 1 \u2212 (1 + \u03bex / \u03c3)<sup>\u22121/\u03be</sup>, &nbsp; x &gt; 0
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
            RVI(t) = w<sub>\u03be</sub> |d\u03be/dt| + w<sub>\u03c3</sub> |d\u03c3/dt|
          </div>
          <div style={{ color: '#64748b', fontSize: 12, marginTop: 8, paddingLeft: 4 }}>
            Current weights: w<sub>\u03be</sub> = {cfg.velocityWeightXi}, w<sub>\u03c3</sub> = {cfg.velocityWeightSigma}
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
            Warning Alert: &nbsp; R&#x0304;VI<sub>recent</sub> &gt; \u03bc<sub>RVI</sub> + 2\u03c3<sub>RVI</sub>
          </div>
        </div>
      </div>

      {/* Train/Test Split Explanation */}
      <SectionHeader icon="\ud83e\uddea" text="Out-of-Sample Evaluation Design" />
      <div className="info-panel" style={{ borderLeft: '3px solid #a855f7' }}>
        <h4>Temporal Train / Test Split</h4>
        <p style={{ lineHeight: 2 }}>
          To ensure the model is <b>not overfitting</b>, we implement a strict temporal split:<br />
          <b>Training Period:</b> {cfg.startDate} \u2192 {cfg.trainEnd || '2018-12-31'} \u2014 KMeans centroids and StandardScaler are <b>fitted</b> on this data.<br />
          <b>Testing Period:</b> {cfg.testStart || '2019-01-01'} \u2192 {cfg.endDate} \u2014 Model only <b>predicts</b> cluster labels (no re-fitting).<br />
          All reported metrics (Precision, Recall, F1-Score, Lead Time) are computed <b>exclusively</b> on the out-of-sample test set.
        </p>
      </div>

      {/* Configuration Parameters */}
      <SectionHeader icon="\u2699\ufe0f" text="Configuration Parameters" />
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
      <SectionHeader icon="\ud83d\udcca" text="Data Universe" />
      <div className="info-panel">
        <p style={{ lineHeight: 2 }}>
          <b>Full Date Range:</b> {cfg.startDate} \u2192 {cfg.endDate}<br />
          <b>Train Period:</b> {cfg.startDate} \u2192 {cfg.trainEnd || '2018-12-31'} (model fitting)<br />
          <b>Test Period:</b> {cfg.testStart || '2019-01-01'} \u2192 {cfg.endDate} (out-of-sample evaluation)<br />
          <b>Fossil Fuel ({cfg.fossilFuelTickers.length}):</b> {cfg.fossilFuelTickers.join(', ')}<br />
          <b>ESG / Clean Energy ({cfg.esgCleanTickers.length}):</b> {cfg.esgCleanTickers.join(', ')}<br />
          <b>Benchmark ({cfg.benchmarkTickers.length}):</b> {cfg.benchmarkTickers.join(', ')}<br />
          <b>Total Assets:</b> {cfg.allTickers.length}
        </p>
      </div>
    </>
  );
}
