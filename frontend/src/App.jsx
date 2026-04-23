import { useState } from 'react';
import Sidebar from './components/Sidebar';
import ExecutiveSummary from './pages/ExecutiveSummary';
import RiskVelocityHeatmap from './pages/RiskVelocityHeatmap';
import AssetDeepDive from './pages/AssetDeepDive';
import ClusterAnalysis from './pages/ClusterAnalysis';
import ComparativeAnalytics from './pages/ComparativeAnalytics';
import BacktestResults from './pages/BacktestResults';
import Methodology from './pages/Methodology';

const PAGES = {
  summary: ExecutiveSummary,
  heatmap: RiskVelocityHeatmap,
  deepdive: AssetDeepDive,
  clusters: ClusterAnalysis,
  compare: ComparativeAnalytics,
  backtest: BacktestResults,
  methodology: Methodology,
};

export default function App() {
  const [page, setPage] = useState('summary');
  const PageComponent = PAGES[page] || ExecutiveSummary;

  return (
    <div className="app-layout">
      <Sidebar activePage={page} onNavigate={setPage} />
      <main className="main-content" key={page}>
        <PageComponent />
      </main>
    </div>
  );
}
