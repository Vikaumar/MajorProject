"""
Clustering Module
------------------
K-Means clustering on EVT parameter space (ξ, σ, dξ/dt, dσ/dt),
transition-matrix computation, and Risk Velocity Alert detection.
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config


def build_feature_matrix(all_derivs: dict[str, pd.DataFrame],
                         snapshot_date: str = None) -> pd.DataFrame:
    """
    Build a feature matrix for clustering by taking the latest (or a
    specific date's) EVT parameters for each asset.

    Features: [xi, sigma, dxi_dt, dsigma_dt, RVI]

    Returns
    -------
    pd.DataFrame — index = tickers, columns = features
    """
    features = {}

    for ticker, df in all_derivs.items():
        if snapshot_date:
            # Find nearest date
            idx = df.index.get_indexer([pd.Timestamp(snapshot_date)],
                                        method="nearest")
            row = df.iloc[idx[0]]
        else:
            # Take the last valid row
            row = df.dropna().iloc[-1] if not df.dropna().empty else df.iloc[-1]

        features[ticker] = {
            "xi":        row.get("xi", np.nan),
            "sigma":     row.get("sigma", np.nan),
            "dxi_dt":    row.get("dxi_dt", np.nan),
            "dsigma_dt": row.get("dsigma_dt", np.nan),
            "RVI":       row.get("RVI", np.nan),
        }

    fm = pd.DataFrame(features).T
    fm.index.name = "Ticker"
    return fm


def cluster_assets(features: pd.DataFrame,
                   n_clusters: int = None) -> pd.DataFrame:
    """
    K-Means clustering on standardised EVT features.

    Returns the features DataFrame with an added 'cluster' column,
    sorted so that cluster 0 has the lowest mean ξ (Safe state).
    """
    n_clusters = n_clusters or config.N_CLUSTERS

    # Drop rows with all NaN
    valid = features.dropna()
    if len(valid) < n_clusters:
        print(f"[cluster] Warning: only {len(valid)} valid assets, "
              f"need at least {n_clusters}")
        valid["cluster"] = 0
        return valid

    scaler = StandardScaler()
    X = scaler.fit_transform(valid[["xi", "sigma", "dxi_dt", "dsigma_dt", "RVI"]])

    km = KMeans(n_clusters=n_clusters, n_init=20, random_state=42)
    labels = km.fit_predict(X)

    valid = valid.copy()
    valid["cluster"] = labels

    # Re-label clusters so that 0 = lowest mean ξ → Safe state
    cluster_mean_xi = valid.groupby("cluster")["xi"].mean().sort_values()
    label_map = {old: new for new, old in enumerate(cluster_mean_xi.index)}
    valid["cluster"] = valid["cluster"].map(label_map)
    valid["cluster_label"] = valid["cluster"].map(config.CLUSTER_LABELS)

    return valid


def cluster_assets_predict(features: pd.DataFrame,
                           fitted_scaler,
                           fitted_km,
                           label_map: dict,
                           feature_cols: list[str] = None) -> pd.DataFrame:
    """
    Predict-only clustering using a pre-fitted scaler and KMeans model.
    Used on TEST data to avoid data leakage.

    Parameters
    ----------
    features     : pd.DataFrame — feature matrix for one snapshot
    fitted_scaler: StandardScaler — fitted on train data
    fitted_km    : KMeans — fitted on train data
    label_map    : dict — maps raw KMeans labels → ordered labels (0=Safe)
    feature_cols : list — column names used during training

    Returns
    -------
    pd.DataFrame — features with 'cluster' and 'cluster_label' columns
    """
    feature_cols = feature_cols or ["xi", "sigma", "dxi_dt", "dsigma_dt", "RVI"]
    valid = features.dropna()

    if valid.empty:
        valid["cluster"] = 0
        valid["cluster_label"] = config.CLUSTER_LABELS.get(0, "Safe")
        return valid

    X = fitted_scaler.transform(valid[feature_cols])
    raw_labels = fitted_km.predict(X)

    valid = valid.copy()
    valid["cluster"] = [label_map.get(l, l) for l in raw_labels]
    valid["cluster_label"] = valid["cluster"].map(config.CLUSTER_LABELS)
    return valid


def build_rolling_cluster_labels(all_derivs: dict[str, pd.DataFrame],
                                  n_clusters: int = None,
                                  step: int = 21) -> pd.DataFrame:
    """
    Cluster assets at multiple points in time to track migrations.

    Implements a proper TRAIN / TEST temporal split:
      • Train snapshots (≤ config.TRAIN_END):  KMeans.fit_predict()
      • Test  snapshots (>  config.TRAIN_END):  KMeans.predict() only

    The scaler + KMeans fitted on the LAST train snapshot are reused
    for all test snapshots, preventing data leakage.

    Parameters
    ----------
    step : int — re-cluster every `step` trading days

    Returns
    -------
    pd.DataFrame — index = dates, columns = tickers, values = cluster labels
    """
    n_clusters = n_clusters or config.N_CLUSTERS
    train_end = pd.Timestamp(config.TRAIN_END)

    # Determine common date range
    all_dates = None
    for df in all_derivs.values():
        if all_dates is None:
            all_dates = df.index
        else:
            all_dates = all_dates.intersection(df.index)

    all_dates = sorted(all_dates)
    snapshot_dates = all_dates[::step]

    # Split into train and test snapshots
    train_snapshots = [d for d in snapshot_dates if pd.Timestamp(d) <= train_end]
    test_snapshots  = [d for d in snapshot_dates if pd.Timestamp(d) > train_end]

    print(f"\n  Train/Test Split:")
    print(f"    Train snapshots: {len(train_snapshots)}  (up to {config.TRAIN_END})")
    print(f"    Test  snapshots: {len(test_snapshots)}  (from {config.TEST_START})")

    # ── TRAIN phase: fit_predict at each train snapshot ──────
    records = []
    fitted_scaler = None
    fitted_km = None
    fitted_label_map = None

    for d in train_snapshots:
        d_str = str(d.date()) if hasattr(d, 'date') else str(d)
        fm = build_feature_matrix(all_derivs, snapshot_date=d_str)
        cl = cluster_assets(fm, n_clusters)
        row = cl["cluster"].to_dict()
        row["_date"] = d
        records.append(row)

    # Fit the final train-snapshot model (this is the one we keep)
    if train_snapshots:
        last_train_date = train_snapshots[-1]
        d_str = str(last_train_date.date()) if hasattr(last_train_date, 'date') else str(last_train_date)
        fm_train = build_feature_matrix(all_derivs, snapshot_date=d_str)
        valid_train = fm_train.dropna()

        feature_cols = ["xi", "sigma", "dxi_dt", "dsigma_dt", "RVI"]
        fitted_scaler = StandardScaler()
        X_train = fitted_scaler.fit_transform(valid_train[feature_cols])

        fitted_km = KMeans(n_clusters=n_clusters, n_init=20, random_state=42)
        raw_labels = fitted_km.fit_predict(X_train)

        # Build the label map: 0 = lowest mean ξ → Safe
        temp = valid_train.copy()
        temp["_raw"] = raw_labels
        cluster_mean_xi = temp.groupby("_raw")["xi"].mean().sort_values()
        fitted_label_map = {old: new for new, old in enumerate(cluster_mean_xi.index)}

        print(f"    Fitted model on last train snapshot: {d_str}")

    # ── TEST phase: predict-only at each test snapshot ────────
    for d in test_snapshots:
        d_str = str(d.date()) if hasattr(d, 'date') else str(d)
        fm = build_feature_matrix(all_derivs, snapshot_date=d_str)

        if fitted_scaler is not None and fitted_km is not None:
            cl = cluster_assets_predict(fm, fitted_scaler, fitted_km,
                                        fitted_label_map, feature_cols)
        else:
            # Fallback: if no train data, just fit_predict
            cl = cluster_assets(fm, n_clusters)

        row = cl["cluster"].to_dict()
        row["_date"] = d
        records.append(row)

    labels_df = pd.DataFrame(records).set_index("_date")
    labels_df.index.name = "Date"
    return labels_df


def compute_transition_matrix(labels_df: pd.DataFrame,
                               n_clusters: int = None) -> pd.DataFrame:
    """
    Compute a Markov-style transition matrix from consecutive
    cluster assignments.

    Returns
    -------
    pd.DataFrame — rows = 'from' cluster, cols = 'to' cluster,
                   values = transition probability
    """
    n_clusters = n_clusters or config.N_CLUSTERS
    trans = np.zeros((n_clusters, n_clusters))

    for col in labels_df.columns:
        seq = labels_df[col].dropna().astype(int).values
        for i in range(len(seq) - 1):
            fr, to = seq[i], seq[i + 1]
            if 0 <= fr < n_clusters and 0 <= to < n_clusters:
                trans[fr, to] += 1

    # Normalise rows to probabilities
    row_sums = trans.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1
    trans_prob = trans / row_sums

    labels = [config.CLUSTER_LABELS.get(i, f"Cluster {i}")
              for i in range(n_clusters)]
    return pd.DataFrame(trans_prob, index=labels, columns=labels)


def detect_warning_alerts(all_derivs: dict[str, pd.DataFrame],
                          percentile: float = 80) -> pd.DataFrame:
    """
    Flag assets whose recent RVI exceeds a critical percentile,
    indicating a Risk Velocity Alert (Warning State transition).

    Returns
    -------
    pd.DataFrame with columns [ticker, recent_RVI, threshold, is_warning_alert]
    """
    recent_rvi = {}
    for ticker, df in all_derivs.items():
        tail = df["RVI"].dropna().tail(63)      # last quarter
        recent_rvi[ticker] = tail.mean()

    rvi_series = pd.Series(recent_rvi, name="recent_RVI")
    threshold  = np.percentile(rvi_series.dropna(), percentile)

    out = pd.DataFrame({
        "recent_RVI":      rvi_series,
        "threshold":       threshold,
        "is_warning_alert": rvi_series > threshold,
        "category":        [config.TICKER_CATEGORY.get(t, "Unknown")
                            for t in rvi_series.index]
    })
    out.index.name = "Ticker"
    return out.sort_values("recent_RVI", ascending=False)


def compute_silhouette(features: pd.DataFrame, labels: pd.Series) -> float:
    """
    Compute Silhouette Score for the cluster assignments.

    Parameters
    ----------
    features : pd.DataFrame — the raw feature matrix (xi, sigma, dxi_dt, dsigma_dt, RVI)
    labels   : pd.Series — cluster labels for each asset

    Returns
    -------
    float — Silhouette Score in [-1, 1]. Higher is better.
    """
    valid = features.dropna()
    valid_labels = labels.loc[valid.index]

    if len(valid_labels.unique()) < 2:
        return 0.0   # silhouette undefined for < 2 clusters

    scaler = StandardScaler()
    X = scaler.fit_transform(valid[["xi", "sigma", "dxi_dt", "dsigma_dt", "RVI"]])
    return float(silhouette_score(X, valid_labels))


def compute_lead_time(rolling_labels: pd.DataFrame,
                      crash_cluster: int = None) -> pd.DataFrame:
    """
    Compute Lead Time (ΔT) — the number of time-steps between the
    first Warning-state entry and the subsequent Crash-state entry
    for each asset.

    Parameters
    ----------
    rolling_labels : pd.DataFrame — index = dates, columns = tickers,
                     values = cluster IDs
    crash_cluster  : int — the cluster ID representing Crash state
                     (defaults to config.VALIDATION_LEAD_TIME_CRASH_CLUSTER)

    Returns
    -------
    pd.DataFrame with columns [ticker, first_warning, first_crash, lead_time_days]
    """
    crash_cluster = crash_cluster or config.VALIDATION_LEAD_TIME_CRASH_CLUSTER
    warning_cluster = 1  # Warning state

    records = []
    for ticker in rolling_labels.columns:
        seq = rolling_labels[ticker].dropna().astype(int)
        dates = seq.index

        first_warning = None
        first_crash_after_warning = None

        for d, label in zip(dates, seq.values):
            if label == warning_cluster and first_warning is None:
                first_warning = d
            if label == crash_cluster and first_warning is not None:
                first_crash_after_warning = d
                break

        lead_days = None
        if first_warning is not None and first_crash_after_warning is not None:
            lead_days = (pd.Timestamp(first_crash_after_warning)
                         - pd.Timestamp(first_warning)).days

        records.append({
            "Ticker":          ticker,
            "first_warning":   first_warning,
            "first_crash":     first_crash_after_warning,
            "lead_time_days":  lead_days,
        })

    out = pd.DataFrame(records).set_index("Ticker")
    return out


# ── Quick self-test ──────────────────────────────────────────
if __name__ == "__main__":
    print("[cluster] Module loaded successfully. Run via main.py.")
