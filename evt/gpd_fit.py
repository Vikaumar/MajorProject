"""
EVT Engine — Generalized Pareto Distribution (GPD) Fitting
-----------------------------------------------------------
Implements the Peaks-Over-Threshold (POT) method with rolling
windows to extract time-varying shape (ξ) and scale (σ) parameters.
"""

import numpy as np
import pandas as pd
from scipy.stats import genpareto
from scipy.optimize import minimize
import warnings
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config


def select_threshold(losses: np.ndarray, quantile: float = None) -> float:
    """
    Select the POT threshold as a given quantile of the loss series.
    """
    quantile = quantile or config.POT_QUANTILE
    return np.quantile(losses[~np.isnan(losses)], quantile)


def fit_gpd(exceedances: np.ndarray) -> dict:
    """
    Fit a Generalized Pareto Distribution to exceedances above threshold.

    Uses scipy.stats.genpareto MLE fitting.

    Returns
    -------
    dict with keys: 'xi' (shape), 'sigma' (scale), 'n_exceed', 'success'
    """
    if len(exceedances) < config.MIN_EXCEEDANCES:
        return {"xi": np.nan, "sigma": np.nan,
                "n_exceed": len(exceedances), "success": False}

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # genpareto.fit returns (c, loc, scale) where c = shape (ξ)
            c, loc, scale = genpareto.fit(exceedances, floc=0)

        # Sanity: reject extreme / implausible fits
        if abs(c) > 5 or scale <= 0:
            return {"xi": np.nan, "sigma": np.nan,
                    "n_exceed": len(exceedances), "success": False}

        return {"xi": c, "sigma": scale,
                "n_exceed": len(exceedances), "success": True}
    except Exception:
        return {"xi": np.nan, "sigma": np.nan,
                "n_exceed": len(exceedances), "success": False}


def rolling_gpd_params(loss_series: pd.Series,
                       window: int = None,
                       quantile: float = None) -> pd.DataFrame:
    """
    Slide a window across the loss series, fit GPD at each step.

    Parameters
    ----------
    loss_series : pd.Series — single-asset negative log-returns
    window      : int — rolling window size (default from config)
    quantile    : float — POT quantile (default from config)

    Returns
    -------
    pd.DataFrame indexed by date with columns:
        ['xi', 'sigma', 'threshold', 'n_exceedances', 'fit_success']
    """
    window   = window or config.ROLLING_WINDOW
    quantile = quantile or config.POT_QUANTILE

    results = []
    dates   = []

    arr = loss_series.values
    idx = loss_series.index

    for end in range(window, len(arr) + 1):
        start = end - window
        chunk = arr[start:end]
        chunk_clean = chunk[~np.isnan(chunk)]

        if len(chunk_clean) < window * 0.5:
            results.append({"xi": np.nan, "sigma": np.nan,
                            "threshold": np.nan, "n_exceedances": 0,
                            "fit_success": False})
            dates.append(idx[end - 1])
            continue

        threshold = select_threshold(chunk_clean, quantile)
        exceedances = chunk_clean[chunk_clean > threshold] - threshold

        fit = fit_gpd(exceedances)
        results.append({
            "xi":            fit["xi"],
            "sigma":         fit["sigma"],
            "threshold":     threshold,
            "n_exceedances": fit["n_exceed"],
            "fit_success":   fit["success"]
        })
        dates.append(idx[end - 1])

    df = pd.DataFrame(results, index=dates)
    df.index.name = "Date"
    return df


def compute_all_rolling_params(losses: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """
    Run rolling GPD for every asset in the losses DataFrame.

    Returns
    -------
    dict  — {ticker: DataFrame of rolling params}
    """
    all_params = {}
    tickers = losses.columns.tolist()

    for i, ticker in enumerate(tickers):
        print(f"[evt] Fitting rolling GPD for {ticker} "
              f"({i+1}/{len(tickers)}) ...")
        params = rolling_gpd_params(losses[ticker])

        # Success rate
        success_rate = params["fit_success"].mean() * 100
        print(f"       → {success_rate:.1f}% successful fits, "
              f"{len(params)} windows")

        all_params[ticker] = params

    return all_params


# ── Quick self-test ──────────────────────────────────────────
if __name__ == "__main__":
    from data.fetch_data import fetch_prices, compute_negative_log_returns

    prices = fetch_prices(["XOM", "ICLN"], start="2020-01-01", end="2024-12-31")
    losses = compute_negative_log_returns(prices)
    params = compute_all_rolling_params(losses)

    for t, df in params.items():
        print(f"\n{t}:")
        print(df[["xi", "sigma"]].describe())
