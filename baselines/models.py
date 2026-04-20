"""
Baseline Risk-Signal Models
-----------------------------
Implements standard industry risk measures (VaR, ES, Volatility)
that generate warning/crash signals so we can compare our
EVT-Clustering framework against conventional approaches.

Baseline signals are derived from the same loss (negative log-return)
series used by the main framework, ensuring a fair comparison.

Design choice: Historical Simulation (non-parametric) VaR / ES,
since it makes no distributional assumption and is harder to beat.
"""

import numpy as np
import pandas as pd
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config


# ── Parameters ────────────────────────────────────────────────
VAR_WINDOW       = 252     # 1-year rolling window (same as EVT)
VAR_CONFIDENCE   = 0.95    # 95th percentile
ES_CONFIDENCE    = 0.95
VOL_WINDOW       = 63      # ~1 quarter for volatility baseline
VOL_MULTIPLIER   = 2.0     # flag when vol > 2× long-run average


# ──────────────────────────────────────────────────────────────
#  Rolling Historical VaR
# ──────────────────────────────────────────────────────────────
def rolling_var(loss_series: pd.Series,
                window: int = VAR_WINDOW,
                confidence: float = VAR_CONFIDENCE) -> pd.Series:
    """
    Rolling Historical-Simulation Value-at-Risk.

    VaR_α = quantile(losses, α)  over the trailing window.
    A higher VaR means the tail is getting heavier.
    """
    return loss_series.rolling(window, min_periods=int(window * 0.5)).quantile(confidence)


# ──────────────────────────────────────────────────────────────
#  Rolling Historical ES (CVaR)
# ──────────────────────────────────────────────────────────────
def rolling_es(loss_series: pd.Series,
               window: int = VAR_WINDOW,
               confidence: float = ES_CONFIDENCE) -> pd.Series:
    """
    Rolling Expected Shortfall = mean of losses beyond VaR.
    """
    def _es(chunk):
        if chunk.isna().all():
            return np.nan
        var = np.quantile(chunk.dropna(), confidence)
        tail = chunk[chunk >= var]
        return tail.mean() if len(tail) > 0 else var

    return loss_series.rolling(window, min_periods=int(window * 0.5)).apply(_es, raw=False)


# ──────────────────────────────────────────────────────────────
#  Rolling Volatility
# ──────────────────────────────────────────────────────────────
def rolling_volatility(loss_series: pd.Series,
                       window: int = VOL_WINDOW) -> pd.Series:
    """Annualised rolling standard deviation of losses."""
    return loss_series.rolling(window, min_periods=int(window * 0.5)).std() * np.sqrt(252)


# ──────────────────────────────────────────────────────────────
#  Generate baseline warning/crash signals
# ──────────────────────────────────────────────────────────────
def _percentile_thresholds(series: pd.Series,
                           warn_pct: float = 75,
                           crash_pct: float = 90):
    """Compute the warning and crash percentile thresholds."""
    clean = series.dropna()
    if clean.empty:
        return np.nan, np.nan
    return np.percentile(clean, warn_pct), np.percentile(clean, crash_pct)


def generate_baseline_labels(loss_series: pd.Series,
                             method: str = "VaR") -> pd.Series:
    """
    Produce a cluster-like label sequence (0=Safe, 1=Warning, 2=Crash)
    using a traditional risk measure.

    Parameters
    ----------
    method : str — one of  'VaR', 'ES', 'Volatility'

    Returns
    -------
    pd.Series — integer labels aligned with the loss_series index
    """
    if method == "VaR":
        metric = rolling_var(loss_series)
    elif method == "ES":
        metric = rolling_es(loss_series)
    elif method == "Volatility":
        metric = rolling_volatility(loss_series)
    else:
        raise ValueError(f"Unknown baseline method: {method}")

    warn_thresh, crash_thresh = _percentile_thresholds(metric)

    labels = pd.Series(0, index=metric.index, name=loss_series.name, dtype=int)
    labels[metric >= warn_thresh]  = 1   # Warning
    labels[metric >= crash_thresh] = 2   # Crash
    labels[metric.isna()] = np.nan

    return labels


def generate_all_baseline_labels(losses: pd.DataFrame,
                                 method: str = "VaR") -> pd.DataFrame:
    """
    Run `generate_baseline_labels` for every asset.

    Returns
    -------
    pd.DataFrame — same shape as rolling_cluster_labels
                   (index = dates, columns = tickers, values = 0/1/2)
    """
    frames = {}
    for ticker in losses.columns:
        frames[ticker] = generate_baseline_labels(losses[ticker], method)

    df = pd.DataFrame(frames)
    df.index.name = "Date"
    return df.dropna(how="all")


# ──────────────────────────────────────────────────────────────
#  Convenience: run all three baselines at once
# ──────────────────────────────────────────────────────────────
def run_all_baselines(losses: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """
    Returns
    -------
    dict — {"VaR": labels_df, "ES": labels_df, "Volatility": labels_df}
    """
    results = {}
    for method in ["VaR", "ES", "Volatility"]:
        print(f"[baselines] Generating {method} signals …")
        results[method] = generate_all_baseline_labels(losses, method)
    return results


# ── Quick self-test ──────────────────────────────────────────
if __name__ == "__main__":
    print("[baselines] Module loaded. Run via main.py.")
