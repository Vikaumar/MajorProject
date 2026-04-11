"""
Central configuration for the Temporal EVT-Clustering framework.
All tuneable parameters live here.
"""

import os
from datetime import datetime

# ──────────────────────────────────────────────
# Ticker Universe
# ──────────────────────────────────────────────
FOSSIL_FUEL_TICKERS = ["XOM", "CVX", "COP", "BP", "SHEL", "TTE", "EOG", "SLB"]
ESG_CLEAN_TICKERS   = ["ICLN", "TAN", "QCLN", "NEE", "ENPH", "FSLR", "BEP", "PLUG"]
BENCHMARK_TICKERS   = ["SPY"]

ALL_TICKERS = FOSSIL_FUEL_TICKERS + ESG_CLEAN_TICKERS + BENCHMARK_TICKERS

TICKER_CATEGORY = {}
for t in FOSSIL_FUEL_TICKERS:
    TICKER_CATEGORY[t] = "Fossil Fuel"
for t in ESG_CLEAN_TICKERS:
    TICKER_CATEGORY[t] = "ESG / Clean Energy"
for t in BENCHMARK_TICKERS:
    TICKER_CATEGORY[t] = "Benchmark"

# ──────────────────────────────────────────────
# Date Range
# ──────────────────────────────────────────────
START_DATE = "2018-01-01"
END_DATE   = "2025-12-31"

# ──────────────────────────────────────────────
# EVT / GPD Parameters
# ──────────────────────────────────────────────
ROLLING_WINDOW   = 252          # ~1 trading year
POT_QUANTILE     = 0.90         # 90th percentile threshold
MIN_EXCEEDANCES  = 15           # minimum exceedances for a valid GPD fit

# ──────────────────────────────────────────────
# Temporal Derivative Parameters
# ──────────────────────────────────────────────
SMOOTHING_WINDOW = 21           # Savitzky-Golay smoothing window (must be odd)
SMOOTHING_POLY   = 3            # polynomial order for Savitzky-Golay
VELOCITY_WEIGHT_XI    = 0.6     # weight of dξ/dt in the Risk Velocity Index
VELOCITY_WEIGHT_SIGMA = 0.4     # weight of dσ/dt in the Risk Velocity Index

# ──────────────────────────────────────────────
# Clustering Parameters
# ──────────────────────────────────────────────
N_CLUSTERS       = 3            # Low / Medium / High tail-risk
CLUSTER_LABELS   = {0: "Low Risk", 1: "Medium Risk", 2: "High Risk"}

# ──────────────────────────────────────────────
# Output Paths
# ──────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR   = os.path.join(PROJECT_ROOT, "output")
FIGURES_DIR  = os.path.join(OUTPUT_DIR, "figures")
DATA_DIR     = os.path.join(OUTPUT_DIR, "data")

for d in [OUTPUT_DIR, FIGURES_DIR, DATA_DIR]:
    os.makedirs(d, exist_ok=True)
