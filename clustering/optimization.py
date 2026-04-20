"""
Clustering Optimisation Module
-------------------------------
Addresses reviewer point 3:  justify K = 3 with empirical evidence.

1.  Sweeps K ∈ {2, 3, 4, 5} and computes internal validity metrics:
      • Silhouette Score
      • Davies-Bouldin Index
      • Calinski-Harabasz Index

2.  Runs Gaussian Mixture Models (GMM) as an alternative to K-Means
    and reports the same metrics + BIC/AIC for model selection.
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    silhouette_score,
    davies_bouldin_score,
    calinski_harabasz_score,
)
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config

K_RANGE = [2, 3, 4, 5]


# ──────────────────────────────────────────────────────────────
#  Internal metrics helper
# ──────────────────────────────────────────────────────────────
def _compute_metrics(X: np.ndarray, labels: np.ndarray) -> dict:
    """Compute Silhouette, Davies-Bouldin, and Calinski-Harabasz."""
    n_unique = len(set(labels))
    if n_unique < 2 or n_unique >= len(X):
        return {
            "silhouette": np.nan,
            "davies_bouldin": np.nan,
            "calinski_harabasz": np.nan,
        }
    return {
        "silhouette":       float(silhouette_score(X, labels)),
        "davies_bouldin":   float(davies_bouldin_score(X, labels)),
        "calinski_harabasz": float(calinski_harabasz_score(X, labels)),
    }


# ──────────────────────────────────────────────────────────────
#  K-Means sweep
# ──────────────────────────────────────────────────────────────
def kmeans_k_sweep(features: pd.DataFrame,
                   k_range: list[int] = None) -> pd.DataFrame:
    """
    Fit K-Means for each K in *k_range* and return a comparison table.

    Parameters
    ----------
    features : pd.DataFrame — the EVT feature matrix (xi, sigma, dxi_dt, dsigma_dt, RVI)

    Returns
    -------
    pd.DataFrame with columns: K, silhouette, davies_bouldin, calinski_harabasz, inertia
    """
    k_range = k_range or K_RANGE

    valid = features.dropna()
    feature_cols = [c for c in ["xi", "sigma", "dxi_dt", "dsigma_dt", "RVI"] if c in valid.columns]
    scaler = StandardScaler()
    X = scaler.fit_transform(valid[feature_cols])

    records = []
    for k in k_range:
        if k >= len(X):
            print(f"[cluster-opt] Skipping K={k} (not enough samples)")
            continue
        km = KMeans(n_clusters=k, n_init=20, random_state=42)
        labels = km.fit_predict(X)
        metrics = _compute_metrics(X, labels)
        metrics["K"] = k
        metrics["inertia"] = float(km.inertia_)
        metrics["method"] = "KMeans"
        records.append(metrics)
        print(f"[cluster-opt] KMeans K={k}  Silhouette={metrics['silhouette']:.4f}  "
              f"DB={metrics['davies_bouldin']:.4f}  CH={metrics['calinski_harabasz']:.1f}")

    return pd.DataFrame(records)


# ──────────────────────────────────────────────────────────────
#  GMM sweep
# ──────────────────────────────────────────────────────────────
def gmm_k_sweep(features: pd.DataFrame,
                k_range: list[int] = None) -> pd.DataFrame:
    """
    Fit Gaussian Mixture Models for each K and return comparison table
    including BIC and AIC for model selection.
    """
    k_range = k_range or K_RANGE

    valid = features.dropna()
    feature_cols = [c for c in ["xi", "sigma", "dxi_dt", "dsigma_dt", "RVI"] if c in valid.columns]
    scaler = StandardScaler()
    X = scaler.fit_transform(valid[feature_cols])

    records = []
    for k in k_range:
        if k >= len(X):
            print(f"[cluster-opt] Skipping GMM K={k} (not enough samples)")
            continue
        gmm = GaussianMixture(n_components=k, n_init=10,
                              covariance_type="full", random_state=42)
        labels = gmm.fit_predict(X)
        metrics = _compute_metrics(X, labels)
        metrics["K"] = k
        metrics["BIC"] = float(gmm.bic(X))
        metrics["AIC"] = float(gmm.aic(X))
        metrics["method"] = "GMM"
        records.append(metrics)
        print(f"[cluster-opt] GMM    K={k}  Silhouette={metrics['silhouette']:.4f}  "
              f"BIC={metrics['BIC']:.1f}  AIC={metrics['AIC']:.1f}")

    return pd.DataFrame(records)


# ──────────────────────────────────────────────────────────────
#  Unified comparison
# ──────────────────────────────────────────────────────────────
def run_clustering_optimization(features: pd.DataFrame,
                                k_range: list[int] = None) -> pd.DataFrame:
    """
    Run both K-Means and GMM sweeps and concatenate into a single
    comparison table.

    Returns
    -------
    pd.DataFrame — columns: method, K, silhouette, davies_bouldin,
                   calinski_harabasz, inertia (KMeans only),
                   BIC/AIC (GMM only)
    """
    print("\n  ── Clustering Optimisation: K-Means ──")
    km_df = kmeans_k_sweep(features, k_range)

    print("\n  ── Clustering Optimisation: GMM ──")
    gmm_df = gmm_k_sweep(features, k_range)

    combined = pd.concat([km_df, gmm_df], ignore_index=True)

    # Identify best K per method
    for method in ["KMeans", "GMM"]:
        subset = combined[combined["method"] == method]
        if subset.empty:
            continue
        best_row = subset.loc[subset["silhouette"].idxmax()]
        print(f"\n  ★ Best {method}: K={int(best_row['K'])}  "
              f"(Silhouette={best_row['silhouette']:.4f})")

    return combined


# ── Quick self-test ──────────────────────────────────────────
if __name__ == "__main__":
    print("[cluster-opt] Module loaded. Run via main.py.")
