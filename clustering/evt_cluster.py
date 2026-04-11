"""
Clustering Module
------------------
K-Means clustering on EVT parameter space (ξ, σ, dξ/dt, dσ/dt),
transition-matrix computation, and fast-mover detection.
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
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
    sorted so that cluster 0 has the lowest mean ξ (Low Risk).
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

    # Re-label clusters so that 0 = lowest mean ξ → Low Risk
    cluster_mean_xi = valid.groupby("cluster")["xi"].mean().sort_values()
    label_map = {old: new for new, old in enumerate(cluster_mean_xi.index)}
    valid["cluster"] = valid["cluster"].map(label_map)
    valid["cluster_label"] = valid["cluster"].map(config.CLUSTER_LABELS)

    return valid


def build_rolling_cluster_labels(all_derivs: dict[str, pd.DataFrame],
                                  n_clusters: int = None,
                                  step: int = 21) -> pd.DataFrame:
    """
    Cluster assets at multiple points in time to track migrations.

    Parameters
    ----------
    step : int — re-cluster every `step` trading days

    Returns
    -------
    pd.DataFrame — index = dates, columns = tickers, values = cluster labels
    """
    n_clusters = n_clusters or config.N_CLUSTERS

    # Determine common date range
    all_dates = None
    for df in all_derivs.values():
        if all_dates is None:
            all_dates = df.index
        else:
            all_dates = all_dates.intersection(df.index)

    all_dates = sorted(all_dates)
    snapshot_dates = all_dates[::step]

    records = []
    for d in snapshot_dates:
        d_str = str(d.date()) if hasattr(d, 'date') else str(d)
        fm = build_feature_matrix(all_derivs, snapshot_date=d_str)
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


def detect_fast_movers(all_derivs: dict[str, pd.DataFrame],
                        percentile: float = 80) -> pd.DataFrame:
    """
    Flag assets whose recent RVI exceeds a critical percentile.

    Returns
    -------
    pd.DataFrame with columns [ticker, recent_RVI, threshold, is_fast_mover]
    """
    recent_rvi = {}
    for ticker, df in all_derivs.items():
        tail = df["RVI"].dropna().tail(63)      # last quarter
        recent_rvi[ticker] = tail.mean()

    rvi_series = pd.Series(recent_rvi, name="recent_RVI")
    threshold  = np.percentile(rvi_series.dropna(), percentile)

    out = pd.DataFrame({
        "recent_RVI":   rvi_series,
        "threshold":    threshold,
        "is_fast_mover": rvi_series > threshold,
        "category":     [config.TICKER_CATEGORY.get(t, "Unknown")
                         for t in rvi_series.index]
    })
    out.index.name = "Ticker"
    return out.sort_values("recent_RVI", ascending=False)


# ── Quick self-test ──────────────────────────────────────────
if __name__ == "__main__":
    print("[cluster] Module loaded successfully. Run via main.py.")
