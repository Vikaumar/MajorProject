"""
Temporal Derivatives Module
----------------------------
Computes the velocity (first derivative) and acceleration (second
derivative) of EVT parameters ξ(t) and σ(t), plus a composite
Risk Velocity Index (RVI).
"""

import numpy as np
import pandas as pd
from scipy.signal import savgol_filter
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config


def _smooth(series: np.ndarray,
            window: int = None,
            polyorder: int = None) -> np.ndarray:
    """Apply Savitzky-Golay smoothing to reduce noise before differentiation."""
    window    = window or config.SMOOTHING_WINDOW
    polyorder = polyorder or config.SMOOTHING_POLY

    # Window must be odd and > polyorder
    if window % 2 == 0:
        window += 1
    if len(series) < window:
        return series  # too short to smooth

    return savgol_filter(series, window_length=window, polyorder=polyorder)


def compute_velocity(param_series: pd.Series,
                     smooth: bool = True) -> pd.Series:
    """
    First-order temporal derivative  dp/dt  via finite differences.

    Parameters
    ----------
    param_series : pd.Series — time-indexed ξ(t) or σ(t)
    smooth       : bool — apply Savitzky-Golay smoothing first

    Returns
    -------
    pd.Series — velocity (same index, first value = NaN)
    """
    vals = param_series.values.astype(float).copy()

    # Interpolate NaN gaps for derivative computation
    nans = np.isnan(vals)
    if nans.any() and not nans.all():
        x = np.arange(len(vals))
        vals[nans] = np.interp(x[nans], x[~nans], vals[~nans])

    if smooth:
        vals = _smooth(vals)

    # Central finite difference (numpy gradient)
    velocity = np.gradient(vals)

    result = pd.Series(velocity, index=param_series.index, name=f"d{param_series.name}/dt")
    return result


def compute_acceleration(velocity_series: pd.Series) -> pd.Series:
    """
    Second-order derivative  d²p/dt²  (derivative of velocity).
    """
    vals = velocity_series.values.astype(float).copy()

    nans = np.isnan(vals)
    if nans.any() and not nans.all():
        x = np.arange(len(vals))
        vals[nans] = np.interp(x[nans], x[~nans], vals[~nans])

    accel = np.gradient(vals)
    return pd.Series(accel, index=velocity_series.index,
                     name=f"d²/dt²")


def compute_risk_velocity_index(dxi: pd.Series,
                                 dsigma: pd.Series,
                                 w_xi: float = None,
                                 w_sigma: float = None) -> pd.Series:
    """
    Composite Risk Velocity Index (RVI):
        RVI(t) = w_ξ · |dξ/dt| + w_σ · |dσ/dt|

    Captures overall speed of tail-risk intensification.
    """
    w_xi    = w_xi or config.VELOCITY_WEIGHT_XI
    w_sigma = w_sigma or config.VELOCITY_WEIGHT_SIGMA

    rvi = w_xi * dxi.abs() + w_sigma * dsigma.abs()
    rvi.name = "RVI"
    return rvi


def compute_all_derivatives(all_params: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """
    For every ticker's rolling GPD parameter DataFrame, compute:
      - dξ/dt, dσ/dt  (velocity)
      - d²ξ/dt², d²σ/dt²  (acceleration)
      - RVI  (composite index)

    Returns
    -------
    dict — {ticker: DataFrame with columns
            [xi, sigma, dxi_dt, dsigma_dt, d2xi_dt2, d2sigma_dt2, RVI]}
    """
    all_derivs = {}

    for ticker, params in all_params.items():
        df = params[["xi", "sigma"]].copy()

        # Velocity
        df["dxi_dt"]    = compute_velocity(df["xi"])
        df["dsigma_dt"] = compute_velocity(df["sigma"])

        # Acceleration
        df["d2xi_dt2"]    = compute_acceleration(df["dxi_dt"])
        df["d2sigma_dt2"] = compute_acceleration(df["dsigma_dt"])

        # Risk Velocity Index
        df["RVI"] = compute_risk_velocity_index(df["dxi_dt"], df["dsigma_dt"])

        all_derivs[ticker] = df
        print(f"[derivatives] {ticker} — mean RVI = {df['RVI'].mean():.6f}")

    return all_derivs


# ── Quick self-test ──────────────────────────────────────────
if __name__ == "__main__":
    # Synthetic test
    idx = pd.date_range("2020-01-01", periods=200, freq="B")
    xi  = pd.Series(np.sin(np.linspace(0, 4*np.pi, 200)) * 0.3 + 0.1,
                    index=idx, name="xi")
    sig = pd.Series(np.cos(np.linspace(0, 4*np.pi, 200)) * 0.02 + 0.03,
                    index=idx, name="sigma")

    v_xi  = compute_velocity(xi)
    v_sig = compute_velocity(sig)
    rvi   = compute_risk_velocity_index(v_xi, v_sig)

    print("Velocity ξ:", v_xi.describe())
    print("RVI:", rvi.describe())
