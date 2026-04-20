<div align="center">
  
# 🌍 Climate Risk Velocity Dashboard
### Temporal EVT-Clustering Framework for Financial Markets

[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)

[**Live Dashboard (Vercel)**](https://major-project-gules-kappa.vercel.app/) • [**Live API (Render)**](https://climate-risk-backend-igou.onrender.com/docs)

___
</div>

## 📌 Project Overview
This project presents a novel **Temporal Extreme Value Theory (EVT) and Clustering framework** designed to quantify the *velocity* of climate transition risk in financial markets. 

Unlike traditional risk measures that provide static snapshots of extreme losses (like VaR or Expected Shortfall), this framework evaluates how the fundamental shape and scale of tail risk distributions are accelerating over time across different asset classes (Fossil Fuels, ESG/Clean Energy, and Benchmarks).

The research pipeline integrates mathematical risk modeling with a full-stack, institutional-grade analytical dashboard.

---

## 🚀 Key Innovations

1. **Rolling EVT Parameters:** Applying the Peaks-Over-Threshold (POT) approach over a 252-day rolling window to extract time-varying Generalised Pareto Distribution (GPD) parameters — shape ($\xi$) and scale ($\sigma$).
2. **Temporal Derivatives (Risk Velocity):** Computing the first and second derivatives of the parameters ($d\xi/dt$, $d\sigma/dt$) to mathematically capture the speed and acceleration of tail risk.
3. **Composite Risk Velocity Index (RVI):** Synthesising parameter velocities into a unified early-warning signal.
4. **Dynamic Clustering (K-Means):** Mapping assets into mathematically justified, distinct risk regimes (Safe, Warning, Crash) based on real-time tail behavior.

---

## 📊 Empirical Validation & Performance

Following rigorous academic review, the framework has been successfully benchmarked against industry standards on a dataset of 17 assets spanning from 2018 to 2025:

*   **Baseline Superiority:** Achieved an **F1-Score of 0.73**, outperforming Historical VaR (0.48), Expected Shortfall (0.44), and Rolling Volatility (0.58).
*   **High Precision Signaling:** Cut False Alarms in half compared to traditional VaR via a 120-trading-day look-ahead backtest framework.
*   **Ablation Verified Novelty:** Demonstrated that incorporating temporal derivatives (the velocity features) significantly improves predictive accuracy compared to an EVT-only approach.
*   **Optimized Architecture:** Validated the $K=3$ architecture empirically using Silhouette Scores, Davies-Bouldin index, and Gaussian Mixture Models (GMM) benchmarking.

---

## 🛠️ System Architecture

The project is built on a split architecture ensuring decoupling of intensive calculations and the interactive user interface.

### 1. The Pipeline Core (`/main.py`)
A comprehensive 9-stage Python engine that handles data ingestion (via `yfinance`), mathematical transformations, parameter fitting, derivatives calculation, unsupervised clustering, transition probabilities, backtesting, and validation metrics exporting.

### 2. The Backend API (`/api/`)
A highly concurrent **FastAPI** server that caches the pipeline's computational CSV outputs and serves them via RESTful JSON endpoints.
* Hosted on **Render** (Free Tier).

### 3. The Frontend Interface (`/frontend/`)
A responsive **React + Vite** single-page application (SPA). Features dynamic routing, institutional dark-mode aesthetics (glassmorphism), and interactive Plotly-based visualizations including RVI heatmaps and Markov Transition Sankey diagrams.
* Hosted on **Vercel** (Edge Network).

---

## ⚙️ Running Locally

1. **Clone the repository**
   ```bash
   git clone https://github.com/Vikaumar/MajorProject.git
   cd MajorProject
   ```

2. **Run the Computational Pipeline** (Generates data & backend metrics)
   ```bash
   pip install -r requirements.txt
   python main.py
   ```

3. **Start the FastAPI Backend**
   ```bash
   pip install -r api/requirements.txt
   uvicorn api.main:app --reload --port 8000
   ```

4. **Start the React Frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

---

*This project is built for the intersection of quantitative finance and climate-risk management. For technical details, refer to `research_paper_implementation.md`.*
