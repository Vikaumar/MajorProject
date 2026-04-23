"""
╔══════════════════════════════════════════════════════════════╗
║  Temporal EVT-Clustering Framework                          ║
║  ──────────────────────────────────────────────────────────  ║
║  Quantifying the Velocity of Climate Transition Risk        ║
║  in Financial Markets                                       ║
║                                                             ║
║  Pipeline:  fetch → returns → rolling EVT → derivatives     ║
║             → cluster → validate → baselines → ablation     ║
║             → export → visualise                            ║
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
from clustering.optimization import run_clustering_optimization
from validation.backtesting import run_full_backtest
from baselines.models import run_all_baselines
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


# ──────────────────────────────────────────────────────────────
#  Ablation helper: cluster WITHOUT temporal derivatives
# ──────────────────────────────────────────────────────────────
def _build_feature_matrix_no_velocity(all_params: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Build a feature matrix using ONLY ξ and σ (no derivatives).
    This is the 'ablation' variant that strips out the novelty feature.
    """
    features = {}
    for ticker, params in all_params.items():
        row = params.dropna().iloc[-1] if not params.dropna().empty else params.iloc[-1]
        features[ticker] = {
            "xi":    row.get("xi", np.nan),
            "sigma": row.get("sigma", np.nan),
        }
    fm = pd.DataFrame(features).T
    fm.index.name = "Ticker"
    return fm


def _cluster_assets_ablation(features: pd.DataFrame,
                             n_clusters: int = None) -> pd.DataFrame:
    """K-Means on ξ & σ only (ablation — no velocity features)."""
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler

    n_clusters = n_clusters or config.N_CLUSTERS
    valid = features.dropna()
    if len(valid) < n_clusters:
        valid["cluster"] = 0
        return valid

    scaler = StandardScaler()
    X = scaler.fit_transform(valid[["xi", "sigma"]])

    km = KMeans(n_clusters=n_clusters, n_init=20, random_state=42)
    labels = km.fit_predict(X)

    valid = valid.copy()
    valid["cluster"] = labels

    # Re-label so 0 = lowest mean ξ → Safe
    cluster_mean_xi = valid.groupby("cluster")["xi"].mean().sort_values()
    label_map = {old: new for new, old in enumerate(cluster_mean_xi.index)}
    valid["cluster"] = valid["cluster"].map(label_map)
    valid["cluster_label"] = valid["cluster"].map(config.CLUSTER_LABELS)
    return valid


def _build_rolling_labels_ablation(all_params: dict[str, pd.DataFrame],
                                   step: int = 21) -> pd.DataFrame:
    """Rolling cluster labels using ONLY ξ & σ (ablation)."""
    # Build a fake all_derivs with just xi and sigma (no velocity)
    all_dates = None
    for df in all_params.values():
        if all_dates is None:
            all_dates = df.index
        else:
            all_dates = all_dates.intersection(df.index)

    all_dates = sorted(all_dates)
    snapshot_dates = all_dates[::step]

    records = []
    for d in snapshot_dates:
        features = {}
        for ticker, params in all_params.items():
            idx = params.index.get_indexer([pd.Timestamp(d)], method="nearest")
            row = params.iloc[idx[0]]
            features[ticker] = {
                "xi":    row.get("xi", np.nan),
                "sigma": row.get("sigma", np.nan),
            }
        fm = pd.DataFrame(features).T
        fm.index.name = "Ticker"
        cl = _cluster_assets_ablation(fm)
        row_dict = cl["cluster"].to_dict()
        row_dict["_date"] = d
        records.append(row_dict)

    labels_df = pd.DataFrame(records).set_index("_date")
    labels_df.index.name = "Date"
    return labels_df


# ──────────────────────────────────────────────────────────────
#  Main pipeline
# ──────────────────────────────────────────────────────────────
def run_pipeline():
    """Execute the full research pipeline end-to-end."""

    print_banner()
    t0 = time.time()

    # ── Stage 1: Data Acquisition ────────────────────────────
    print("\n" + "─" * 60)
    print("  STAGE 1 / 9 — DATA ACQUISITION")
    print("─" * 60)
    prices = fetch_prices()
    losses = compute_negative_log_returns(prices)
    save_data(prices, losses)

    print(f"\n  Tickers:       {losses.columns.tolist()}")
    print(f"  Date range:    {losses.index[0].date()} → {losses.index[-1].date()}")
    print(f"  Trading days:  {len(losses)}")

    # ── Stage 2: Rolling EVT (GPD Fitting) ───────────────────
    print("\n" + "─" * 60)
    print("  STAGE 2 / 9 — ROLLING GPD FITTING (POT)")
    print("─" * 60)
    all_params = compute_all_rolling_params(losses)

    for ticker, df in all_params.items():
        df.to_csv(os.path.join(config.DATA_DIR, f"gpd_params_{ticker}.csv"))

    # ── Stage 3: Temporal Derivatives ────────────────────────
    print("\n" + "─" * 60)
    print("  STAGE 3 / 9 — TEMPORAL DERIVATIVES (VELOCITY & RVI)")
    print("─" * 60)
    all_derivs = compute_all_derivatives(all_params)

    for ticker, df in all_derivs.items():
        df.to_csv(os.path.join(config.DATA_DIR, f"derivatives_{ticker}.csv"))

    # ── Stage 4: Clustering & Transitions ────────────────────
    print("\n" + "─" * 60)
    print("  STAGE 4 / 9 — CLUSTERING & TRANSITION ANALYSIS")
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

    # ── Stage 5: Validation — Silhouette & Lead Time ─────────
    print("\n" + "─" * 60)
    print("  STAGE 5 / 9 — BASIC VALIDATION (SILHOUETTE & LEAD TIME)")
    print("─" * 60)

    sil_score = compute_silhouette(features, clustered["cluster"])
    print(f"\n  Silhouette Score: {sil_score:.4f}")
    if sil_score > 0.5:
        print("    → Strong cluster separation")
    elif sil_score > 0.25:
        print("    → Moderate cluster separation")
    else:
        print("    → Weak cluster separation — consider tuning parameters")

    lead_time_df = compute_lead_time(labels_df)
    print("\n  Lead Time (ΔT) — Warning → Crash:")
    for ticker, row in lead_time_df.iterrows():
        if row["lead_time_days"] is not None and not pd.isna(row["lead_time_days"]):
            print(f"    {ticker}: {int(row['lead_time_days'])} days")
        else:
            print(f"    {ticker}: No Warning→Crash transition observed")

    validation_summary = pd.DataFrame({
        "metric": ["silhouette_score", "n_clusters", "n_assets"],
        "value":  [sil_score, config.N_CLUSTERS, len(clustered)],
    })
    validation_summary.to_csv(os.path.join(config.DATA_DIR, "validation_summary.csv"), index=False)
    lead_time_df.to_csv(os.path.join(config.DATA_DIR, "lead_time.csv"))

    # ── Stage 6: Out-of-Sample Backtesting ─────────────────────
    print("\n" + "─" * 60)
    print("  STAGE 6 / 9 — OUT-OF-SAMPLE BACKTESTING")
    print("─" * 60)

    print(f"\n  Train period:      up to {config.TRAIN_END}")
    print(f"  Test  period:      {config.TEST_START} onward")
    print(f"  Backtest horizon:  {config.BACKTEST_HORIZON} trading days")
    backtest_results = run_full_backtest(labels_df, horizon=config.BACKTEST_HORIZON,
                                         test_start=config.TEST_START)
    print("\n  Signal-Quality Metrics (EVT-Clustering, TEST SET ONLY):")
    print(backtest_results.to_string())

    backtest_results.to_csv(os.path.join(config.DATA_DIR, "backtesting_results.csv"))

    # ── Stage 7: Baseline Comparisons ─────────────────────────
    print("\n" + "─" * 60)
    print("  STAGE 7 / 9 — BASELINE MODEL COMPARISONS")
    print("─" * 60)

    baseline_labels_all = run_all_baselines(losses)
    baseline_backtest_records = []

    for method, bl_labels in baseline_labels_all.items():
        print(f"\n  ── Backtesting {method} baseline ──")
        bl_backtest = run_full_backtest(bl_labels, horizon=config.BACKTEST_HORIZON,
                                         test_start=config.TEST_START)
        # Extract just the AGGREGATE row
        agg = bl_backtest.loc["AGGREGATE"]
        baseline_backtest_records.append({
            "Method":        method,
            "TP":            agg["TP"],
            "FP":            agg["FP"],
            "FN":            agg["FN"],
            "Precision":     agg["Precision"],
            "Recall":        agg["Recall"],
            "F1":            agg["F1"],
            "mean_lead_time": agg["mean_lead_time"],
        })

    # Add our framework's aggregate row
    our_agg = backtest_results.loc["AGGREGATE"]
    baseline_backtest_records.insert(0, {
        "Method":        "EVT-Clustering (Ours)",
        "TP":            our_agg["TP"],
        "FP":            our_agg["FP"],
        "FN":            our_agg["FN"],
        "Precision":     our_agg["Precision"],
        "Recall":        our_agg["Recall"],
        "F1":            our_agg["F1"],
        "mean_lead_time": our_agg["mean_lead_time"],
    })

    comparison_df = pd.DataFrame(baseline_backtest_records).set_index("Method")
    print("\n  ╔══ Baseline Comparison Summary ══╗")
    print(comparison_df.to_string())
    comparison_df.to_csv(os.path.join(config.DATA_DIR, "baseline_comparisons.csv"))

    # ── Stage 8: Clustering Optimisation ──────────────────────
    print("\n" + "─" * 60)
    print("  STAGE 8 / 9 — CLUSTERING OPTIMISATION (K SWEEP + GMM)")
    print("─" * 60)

    cluster_opt = run_clustering_optimization(features, k_range=config.K_RANGE)
    cluster_opt.to_csv(os.path.join(config.DATA_DIR, "clustering_optimization.csv"), index=False)

    # ── Stage 9: Ablation Study ───────────────────────────────
    print("\n" + "─" * 60)
    print("  STAGE 9 / 9 — ABLATION STUDY (EVT-only vs EVT+Velocity)")
    print("─" * 60)

    # Ablation: cluster using ONLY xi, sigma (no velocity features)
    print("\n  Running ablation (EVT-only, no temporal derivatives) …")
    ablation_labels = _build_rolling_labels_ablation(all_params)
    ablation_backtest = run_full_backtest(ablation_labels, horizon=config.BACKTEST_HORIZON,
                                           test_start=config.TEST_START)

    abl_agg = ablation_backtest.loc["AGGREGATE"]

    ablation_table = pd.DataFrame([
        {
            "Variant":        "EVT-only (ξ, σ)",
            "TP":             abl_agg["TP"],
            "FP":             abl_agg["FP"],
            "FN":             abl_agg["FN"],
            "Precision":      abl_agg["Precision"],
            "Recall":         abl_agg["Recall"],
            "F1":             abl_agg["F1"],
            "mean_lead_time": abl_agg["mean_lead_time"],
        },
        {
            "Variant":        "EVT + Velocity (ξ, σ, dξ/dt, dσ/dt, RVI)",
            "TP":             our_agg["TP"],
            "FP":             our_agg["FP"],
            "FN":             our_agg["FN"],
            "Precision":      our_agg["Precision"],
            "Recall":         our_agg["Recall"],
            "F1":             our_agg["F1"],
            "mean_lead_time": our_agg["mean_lead_time"],
        },
    ]).set_index("Variant")

    print("\n  ╔══ Ablation Study Results ══╗")
    print(ablation_table.to_string())
    ablation_table.to_csv(os.path.join(config.DATA_DIR, "ablation_study.csv"))

    # ── Visualisation ─────────────────────────────────────────
    print("\n" + "─" * 60)
    print("  GENERATING VISUALISATIONS")
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

    print("\n  New output files for the paper:")
    print("    • backtesting_results.csv     — TP/FP/FN/Precision/Recall/F1 per asset")
    print("    • baseline_comparisons.csv    — our method vs VaR/ES/Volatility")
    print("    • clustering_optimization.csv — K sweep with Silhouette/DB/CH for KMeans & GMM")
    print("    • ablation_study.csv          — EVT-only vs EVT+Velocity")

    return {
        "prices":              prices,
        "losses":              losses,
        "all_params":          all_params,
        "all_derivs":          all_derivs,
        "clustered":           clustered,
        "trans_matrix":        trans_matrix,
        "warning_alerts":      warning_alerts,
        "labels_df":           labels_df,
        "silhouette":          sil_score,
        "lead_time":           lead_time_df,
        "backtest_results":    backtest_results,
        "baseline_comparisons": comparison_df,
        "cluster_optimization": cluster_opt,
        "ablation_study":      ablation_table,
    }


# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    results = run_pipeline()
