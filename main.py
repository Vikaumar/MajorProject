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
    detect_warning_alerts,
    compute_silhouette,
    compute_lead_time,
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
    print("  STAGE 1 / 6 — DATA ACQUISITION")
    print("─" * 60)
    prices = fetch_prices()
    losses = compute_negative_log_returns(prices)
    save_data(prices, losses)

    print(f"\n  Tickers:       {losses.columns.tolist()}")
    print(f"  Date range:    {losses.index[0].date()} → {losses.index[-1].date()}")
    print(f"  Trading days:  {len(losses)}")

    # ── Stage 2: Rolling EVT (GPD Fitting) ───────────────────
    print("\n" + "─" * 60)
    print("  STAGE 2 / 6 — ROLLING GPD FITTING (POT)")
    print("─" * 60)
    all_params = compute_all_rolling_params(losses)

    # Save params
    for ticker, df in all_params.items():
        df.to_csv(os.path.join(config.DATA_DIR, f"gpd_params_{ticker}.csv"))

    # ── Stage 3: Temporal Derivatives ────────────────────────
    print("\n" + "─" * 60)
    print("  STAGE 3 / 6 — TEMPORAL DERIVATIVES (VELOCITY & RVI)")
    print("─" * 60)
    all_derivs = compute_all_derivatives(all_params)

    # Save derivatives
    for ticker, df in all_derivs.items():
        df.to_csv(os.path.join(config.DATA_DIR, f"derivatives_{ticker}.csv"))

    # ── Stage 4: Clustering & Transitions ────────────────────
    print("\n" + "─" * 60)
    print("  STAGE 4 / 6 — CLUSTERING & TRANSITION ANALYSIS")
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

    # Risk Velocity Alerts (Warning State)
    warning_alerts = detect_warning_alerts(all_derivs)
    print("\n  Risk Velocity Alerts (Warning State):")
    alerts = warning_alerts[warning_alerts["is_warning_alert"]]
    for ticker, row in alerts.iterrows():
        print(f"    ⚠  {ticker} ({row['category']}) — RVI = {row['recent_RVI']:.6f}")

    # Save
    clustered.to_csv(os.path.join(config.DATA_DIR, "cluster_assignments.csv"))
    trans_matrix.to_csv(os.path.join(config.DATA_DIR, "transition_matrix.csv"))
    warning_alerts.to_csv(os.path.join(config.DATA_DIR, "warning_alerts.csv"))
    labels_df.to_csv(os.path.join(config.DATA_DIR, "rolling_cluster_labels.csv"))

    # ── Stage 5: Validation & Benchmarking ────────────────────
    print("\n" + "─" * 60)
    print("  STAGE 5 / 6 — VALIDATION & BENCHMARKING")
    print("─" * 60)

    # Silhouette Score
    sil_score = compute_silhouette(features, clustered["cluster"])
    print(f"\n  Silhouette Score: {sil_score:.4f}")
    if sil_score > 0.5:
        print("    → Strong cluster separation")
    elif sil_score > 0.25:
        print("    → Moderate cluster separation")
    else:
        print("    → Weak cluster separation — consider tuning parameters")

    # Lead Time (ΔT)
    lead_time_df = compute_lead_time(labels_df)
    print("\n  Lead Time (ΔT) — Warning → Crash:")
    for ticker, row in lead_time_df.iterrows():
        if row["lead_time_days"] is not None and not pd.isna(row["lead_time_days"]):
            print(f"    {ticker}: {int(row['lead_time_days'])} days")
        else:
            print(f"    {ticker}: No Warning→Crash transition observed")

    # Save validation results
    validation_summary = pd.DataFrame({
        "metric": ["silhouette_score", "n_clusters", "n_assets"],
        "value":  [sil_score, config.N_CLUSTERS, len(clustered)],
    })
    validation_summary.to_csv(os.path.join(config.DATA_DIR, "validation_summary.csv"), index=False)
    lead_time_df.to_csv(os.path.join(config.DATA_DIR, "lead_time.csv"))

    # ── Stage 6: Visualisation ─────────────────────────────
    print("\n" + "─" * 60)
    print("  STAGE 6 / 6 — VISUALIZATION")
    print("─" * 60)
    generate_all_plots(all_params, all_derivs, clustered,
                       trans_matrix, warning_alerts)

    # ── Summary ────────────────────────────────────────────
    elapsed = time.time() - t0
    print("\n" + "═" * 60)
    print(f"  ✅  PIPELINE COMPLETE  ({elapsed:.1f}s)")
    print(f"  📁  Output directory: {config.OUTPUT_DIR}")
    print(f"  📊  Figures:          {config.FIGURES_DIR}")
    print(f"  📄  Data CSVs:        {config.DATA_DIR}")
    print("═" * 60)

    return {
        "prices":          prices,
        "losses":          losses,
        "all_params":      all_params,
        "all_derivs":      all_derivs,
        "clustered":       clustered,
        "trans_matrix":    trans_matrix,
        "warning_alerts":  warning_alerts,
        "labels_df":       labels_df,
        "silhouette":      sil_score,
        "lead_time":       lead_time_df,
    }


# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    results = run_pipeline()
