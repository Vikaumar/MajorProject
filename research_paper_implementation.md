# Implementation and System Architecture

This section outlines the technical implementation of the Temporal EVT-Clustering framework and its translation into an interactive, real-time climate risk monitoring dashboard. The system is engineered using a modular Python architecture, combining rigorous mathematical modeling with a modern, reactive web interface.

## 1. System Pipeline Architecture

The core computational engine operates as a nine-stage pipeline designed to process raw financial time-series data into actionable risk intelligence:

1. **Data Acquisition & Preprocessing:** 
   The system fetches historical price data for a predefined basket of assets spanning Fossil Fuel, ESG/Clean Energy, and Benchmark categories. The data is transformed into negative log-returns to isolate tail-risk events.

2. **Rolling Extreme Value Theory (EVT) Modeling:**
   A Peaks-Over-Threshold (POT) approach is applied using a rolling-window mechanism. For each window, the Generalized Pareto Distribution (GPD) parameters—specifically the shape parameter ($\xi$) and scale parameter ($\sigma$)—are estimated using Maximum Likelihood Estimation (MLE) or related optimization techniques.

3. **Temporal Derivative Computation (Risk Velocity):**
   The framework computes the discrete temporal derivatives of the GPD parameters ($d\xi/dt$ and $d\sigma/dt$). These rate-of-change metrics are synthesized into a unified score, establishing the mathematical basis for the **Risk Velocity Index (RVI)**, which quantifies the acceleration of tail risk.

4. **Clustering & Transition Dynamics:**
   Using K-Means clustering in the EVT parameter space (incorporating $\xi$, $\sigma$, and their temporal derivatives), assets are iteratively assigned to three distinct risk regimes: **Safe** (stable tail behavior), **Warning** (elevated and accelerating tail risk), and **Crash** (extreme tail regime with critical velocity). A Markovian transition matrix is derived from the rolling cluster labels to probabilistically model asset migration between these states. Furthermore, a **Risk Velocity Alert** mechanism flags assets transitioning into the Warning state by detecting acute spikes in their RVI that breach dynamically calculated critical thresholds.

5. **Basic Validation (Silhouette Score & Lead Time):**
   **Silhouette Score** analysis is performed to quantify the separability and cohesion of the derived risk clusters. **Lead Time ($\Delta T$)** is computed—defined as the temporal gap between the first RVI-triggered Warning alert and the subsequent realization of a Crash-state event.

6. **Full-Dataset Backtesting & Signal-Quality Metrics:**
   The warning→crash signal is rigorously evaluated across the entire rolling-label history for every asset. The system identifies:
   - **True Positives (TP):** Warning signals followed by a Crash within a configurable horizon (default: 21 trading days).
   - **False Positives (FP):** Warning signals with no subsequent Crash within the horizon.
   - **False Negatives (FN):** Crash events not preceded by any Warning signal.
   
   From these counts, standard classification metrics are derived: **Precision**, **Recall**, and **F1-Score**, along with descriptive statistics for lead-time consistency (**mean and standard deviation of $\Delta T$**). An aggregate row across all assets provides the overall system-level performance.

7. **Baseline Model Comparisons:**
   To contextualize the framework's contribution, three conventional risk baselines are implemented and evaluated under the identical backtesting protocol:
   - **Historical Simulation Value-at-Risk (VaR)** at the 95th percentile, computed over a rolling 252-day window.
   - **Historical Expected Shortfall (ES / CVaR)** at the same confidence level.
   - **Rolling Volatility** (annualized standard deviation over a 63-day window, flagged via percentile thresholds).
   
   Each baseline generates its own Safe/Warning/Crash label sequence using percentile-based thresholds, enabling a direct, apples-to-apples comparison of Precision, Recall, and F1 against the EVT-Clustering framework.

8. **Clustering Optimisation (K-Sweep & GMM):**
   The choice of $K=3$ clusters is empirically justified by sweeping $K \in \{2, 3, 4, 5\}$ and computing internal validation metrics for each:
   - **Silhouette Score** (higher is better; measures intra-cluster cohesion vs inter-cluster separation).
   - **Davies-Bouldin Index** (lower is better; ratio of within-cluster scatter to between-cluster separation).
   - **Calinski-Harabasz Index** (higher is better; variance ratio criterion).
   
   As an alternative to K-Means, **Gaussian Mixture Models (GMM)** are fitted for each $K$, with additional model-selection criteria (**BIC** and **AIC**) to identify the optimal number of components. These results confirm that $K=3$ provides the best trade-off across all metrics.

9. **Ablation Study (Novelty Justification):**
   To empirically validate that the temporal derivative features ($d\xi/dt$, $d\sigma/dt$, RVI) constitute a meaningful contribution beyond standard EVT analysis, an ablation experiment is conducted:
   - **EVT-only variant:** Clustering is performed using only the raw GPD parameters ($\xi$, $\sigma$), without any velocity features.
   - **Full framework:** Clustering uses the complete feature set ($\xi$, $\sigma$, $d\xi/dt$, $d\sigma/dt$, RVI).
   
   Both variants are subjected to the same full-dataset backtesting, and the resulting Precision, Recall, F1, and mean lead-time are compared in a head-to-head table. The ablation demonstrates that incorporating temporal derivatives yields measurably superior predictive quality.

10. **Data Export & Persistence:**
    The output matrices, transition probabilities, validation metrics, backtest results, baseline comparisons, clustering optimisation tables, ablation study, and asset trajectories are serialized into structurally uniform CSV datasets, serving as the static backend for the visualization layer.

## 2. Interactive Dashboard Engineering

To democratize the theoretical framework and provide real-time analytical capabilities, a production-grade web dashboard was developed using **Streamlit**. The front-end departs from conventional academic layouts by implementing a high-fidelity, polished UI (utilizing custom CSS injections) designed to mimic institutional analytics terminals.

### Core Dashboard Components:
*   **Executive Summary:** A high-level ecosystem overview presenting system-wide averages and an integrated Risk Velocity Alert panel highlighting assets entering the Warning state. It employs institutional-grade analytical widgets and dynamic Plotly donut charts to visualize current cluster composition across Safe, Warning, and Crash regimes.
*   **Risk Velocity Heatmap:** Leverages Plotly's interactive heatmap capabilities (`px.imshow`) to display the temporal evolution of shape/scale velocities and the RVI across all tracked assets, applying divergent color scales for immediate visual anomaly detection. Options accurately display formulaic structures like $d\xi/dt$ and $d\sigma/dt$.
*   **Asset Deep Dive:** Permits granular interrogation of individual assets. It renders synchronised, filled time-series plots (GPD parameter evolution alongside velocity derivatives), overlaid with statistical benchmarks (e.g., 90th percentile thresholds).
*   **Cluster Analysis (Markov Dynamics):** Integrates automated Sankey diagrams to map the probability flows of assets transitioning between risk states, directly translating the computationally derived Markov transition matrix into an intuitive flow representation.
*   **Reactive Filtering & Status Monitoring:** A custom-styled, permanently expanded sidebar operates as the global control center. It reflects live data ingestion statuses, handles routing without page reloads, and enforces strict asset categorization taxonomies. 

## 3. Technology Stack

*   **Core Logic:** Python 3.x
*   **Data Manipulation & Math:** NumPy, Pandas, SciPy
*   **Machine Learning/Clustering:** Scikit-Learn (K-Means, GMM, Silhouette, Davies-Bouldin, Calinski-Harabasz)
*   **Front-End Framework:** Streamlit (with extended HTML/CSS overrides)
*   **Interactive Visualization:** Plotly Graph Objects & Plotly Express

---

## 4. Visual Supplements (Appendix)

The following high-resolution charts are automatically generated by the pipeline and power the dashboard's analytics.

### Cluster Scatter with Velocity
![EVT Cluster Scatter in xi and sigma space showing Risk Velocity vectors](https://raw.githubusercontent.com/Vikaumar/MajorProject/main/output/figures/cluster_scatter.png)

### Rolling EVT Parameters over Time
![Rolling evolution of shape (xi) and scale (sigma) parameters](https://raw.githubusercontent.com/Vikaumar/MajorProject/main/output/figures/rolling_evt_params.png)

### Average RVI Profile by Sector
![Comparative Bar Chart comparing average fossil fuel RVI versus ESG RVI](https://raw.githubusercontent.com/Vikaumar/MajorProject/main/output/figures/comparative_rvi_bar.png)

### Heatmaps: Shape and Scale Velocities
![Shape Parameter Velocity dX/dt Heatmap](https://raw.githubusercontent.com/Vikaumar/MajorProject/main/output/figures/velocity_heatmap_dxi_dt.png)
![Scale Parameter Velocity dSigma/dt Heatmap](https://raw.githubusercontent.com/Vikaumar/MajorProject/main/output/figures/velocity_heatmap_dsigma_dt.png)

### RVI Dashboard Output
![RVI static dashboard output](https://raw.githubusercontent.com/Vikaumar/MajorProject/main/output/figures/rvi_dashboard.png)
