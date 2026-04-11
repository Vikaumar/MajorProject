"""
╔══════════════════════════════════════════════════════════════╗
║  Temporal EVT-Clustering Framework                          ║
║  ──────────────────────────────────────────────────────────  ║
║  Quantifying the Velocity of Climate Transition Risk        ║
║  in Financial Markets                                       ║
║                                                             ║
║  Pipeline:  fetch → returns → rolling EVT → derivatives     ║
║             → cluster → export → visualise                  ║
╚══════════════════════════════════════════════════════════════╝
"""

import time
import pandas as pd
import numpy as np
import os
import sys

# ── Project imports ──────────────────────────────────────────
import config
from data.fetch_data import fetch_prices, compute_negative_log_returns, save_data
from evt.gpd_fit import compute_all_rolling_params
from derivatives.velocity import compute_all_derivatives
from clustering.evt_cluster import (
    build_feature_matrix,
    cluster_assets,
    build_rolling_cluster_labels,
    compute_transition_matrix,
    detect_fast_movers,
)
from visualization.plots import generate_all_plots


def print_banner():
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   TEMPORAL EVT-CLUSTERING FRAMEWORK                              ║
║   Quantifying the Velocity of Climate Transition Risk            ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)


def run_pipeline():
    """Execute the full research pipeline end-to-end."""

    print_banner()
    t0 = time.time()

    # ── Stage 1: Data Acquisition ────────────────────────────
    print("\n" + "─" * 60)
    print("  STAGE 1 / 5 — DATA ACQUISITION")
    print("─" * 60)
    prices = fetch_prices()
    losses = compute_negative_log_returns(prices)
    save_data(prices, losses)

    print(f"\n  Tickers:       {losses.columns.tolist()}")
    print(f"  Date range:    {losses.index[0].date()} → {losses.index[-1].date()}")
    print(f"  Trading days:  {len(losses)}")

    # ── Stage 2: Rolling EVT (GPD Fitting) ───────────────────
    print("\n" + "─" * 60)
    print("  STAGE 2 / 5 — ROLLING GPD FITTING (POT)")
    print("─" * 60)
    all_params = compute_all_rolling_params(losses)

    # Save params
    for ticker, df in all_params.items():
        df.to_csv(os.path.join(config.DATA_DIR, f"gpd_params_{ticker}.csv"))

    # ── Stage 3: Temporal Derivatives ────────────────────────
    print("\n" + "─" * 60)
    print("  STAGE 3 / 5 — TEMPORAL DERIVATIVES (VELOCITY & RVI)")
    print("─" * 60)
    all_derivs = compute_all_derivatives(all_params)

    # Save derivatives
    for ticker, df in all_derivs.items():
        df.to_csv(os.path.join(config.DATA_DIR, f"derivatives_{ticker}.csv"))

    # ── Stage 4: Clustering & Transitions ────────────────────
    print("\n" + "─" * 60)
    print("  STAGE 4 / 5 — CLUSTERING & TRANSITION ANALYSIS")
    print("─" * 60)

    # Snapshot clustering (latest data)
    features = build_feature_matrix(all_derivs)
    clustered = cluster_assets(features)
    print("\n  Cluster assignments (latest snapshot):")
    for cl_id in sorted(clustered["cluster"].unique()):
        members = clustered[clustered["cluster"] == cl_id].index.tolist()
        label = config.CLUSTER_LABELS.get(cl_id, f"Cluster {cl_id}")
        print(f"    {label}: {members}")

    # Rolling cluster labels → transition matrix
    labels_df = build_rolling_cluster_labels(all_derivs)
    trans_matrix = compute_transition_matrix(labels_df)
    print("\n  Transition Matrix (probability):")
    print(trans_matrix.to_string())

    # Fast movers
    fast_movers = detect_fast_movers(all_derivs)
    print("\n  Fast Movers (high RVI):")
    movers = fast_movers[fast_movers["is_fast_mover"]]
    for ticker, row in movers.iterrows():
        print(f"    ⚠  {ticker} ({row['category']}) — RVI = {row['recent_RVI']:.6f}")

    # Save
    clustered.to_csv(os.path.join(config.DATA_DIR, "cluster_assignments.csv"))
    trans_matrix.to_csv(os.path.join(config.DATA_DIR, "transition_matrix.csv"))
    fast_movers.to_csv(os.path.join(config.DATA_DIR, "fast_movers.csv"))
    labels_df.to_csv(os.path.join(config.DATA_DIR, "rolling_cluster_labels.csv"))

    # ── Stage 5: Visualisation ───────────────────────────────
    print("\n" + "─" * 60)
    print("  STAGE 5 / 5 — VISUALIZATION")
    print("─" * 60)
    generate_all_plots(all_params, all_derivs, clustered,
                       trans_matrix, fast_movers)

    # ── Summary ──────────────────────────────────────────────
    elapsed = time.time() - t0
    print("\n" + "═" * 60)
    print(f"  ✅  PIPELINE COMPLETE  ({elapsed:.1f}s)")
    print(f"  📁  Output directory: {config.OUTPUT_DIR}")
    print(f"  📊  Figures:          {config.FIGURES_DIR}")
    print(f"  📄  Data CSVs:        {config.DATA_DIR}")
    print("═" * 60)

    return {
        "prices":       prices,
        "losses":       losses,
        "all_params":   all_params,
        "all_derivs":   all_derivs,
        "clustered":    clustered,
        "trans_matrix": trans_matrix,
        "fast_movers":  fast_movers,
        "labels_df":    labels_df,
    }


# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    results = run_pipeline()
