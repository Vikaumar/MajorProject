"""
Backtesting & Signal-Quality Module
-------------------------------------
Runs the warning→crash signal evaluation across the ENTIRE rolling
cluster-label history.  Produces classification metrics (TP, FP, FN,
Precision, Recall, F1) and descriptive lead-time statistics.

Design choices (approved by user):
  • Backtest horizon  = 21 trading days  (≈ 1 calendar month)
  • A True Positive   = Warning flag followed by a Crash within the horizon
  • A False Positive   = Warning flag with NO Crash in the horizon
  • A False Negative   = Crash that was NOT preceded by a Warning in the horizon
"""

import numpy as np
import pandas as pd
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config


# ── configurable defaults ────────────────────────────────────
DEFAULT_HORIZON = 21        # trading days to look-ahead for crash
WARNING_CLUSTER = 1         # cluster id for Warning state
CRASH_CLUSTER   = config.VALIDATION_LEAD_TIME_CRASH_CLUSTER   # 2


# ──────────────────────────────────────────────────────────────
#  Core helpers
# ──────────────────────────────────────────────────────────────
def _extract_events(label_seq: pd.Series,
                    cluster_id: int) -> list[pd.Timestamp]:
    """Return sorted list of dates where *label_seq* first enters
    *cluster_id* (i.e. transition edges, not every occurrence)."""
    events = []
    prev = None
    for date, lbl in label_seq.items():
        if pd.isna(lbl):
            prev = None
            continue
        lbl = int(lbl)
        if lbl == cluster_id and prev != cluster_id:
            events.append(date)
        prev = lbl
    return events


def _has_crash_within(crash_dates: list[pd.Timestamp],
                      after: pd.Timestamp,
                      horizon_days: int) -> tuple[bool, pd.Timestamp | None]:
    """Check if any crash date falls within [after, after + horizon]."""
    cutoff = after + pd.Timedelta(days=horizon_days)
    for cd in crash_dates:
        if after < cd <= cutoff:
            return True, cd
    return False, None


def _has_warning_before(warning_dates: list[pd.Timestamp],
                        before: pd.Timestamp,
                        horizon_days: int) -> bool:
    """Check if any warning date falls within [before - horizon, before)."""
    cutoff = before - pd.Timedelta(days=horizon_days)
    for wd in warning_dates:
        if cutoff <= wd < before:
            return True
    return False


# ──────────────────────────────────────────────────────────────
#  Per-asset backtest
# ──────────────────────────────────────────────────────────────
def backtest_asset(label_seq: pd.Series,
                   horizon: int = DEFAULT_HORIZON) -> dict:
    """
    Evaluate the warning-signal quality for a single asset's
    rolling cluster-label sequence.

    Returns
    -------
    dict with keys: ticker, TP, FP, FN, lead_times (list of days)
    """
    warnings = _extract_events(label_seq, WARNING_CLUSTER)
    crashes  = _extract_events(label_seq, CRASH_CLUSTER)

    tp, fp = 0, 0
    lead_times = []

    for w_date in warnings:
        hit, crash_date = _has_crash_within(crashes, w_date, horizon)
        if hit:
            tp += 1
            lead_times.append((crash_date - w_date).days)
        else:
            fp += 1

    # False negatives: crashes not preceded by any warning
    fn = 0
    for c_date in crashes:
        if not _has_warning_before(warnings, c_date, horizon):
            fn += 1

    return {
        "ticker":      label_seq.name,
        "TP":          tp,
        "FP":          fp,
        "FN":          fn,
        "lead_times":  lead_times,
    }


# ──────────────────────────────────────────────────────────────
#  Full-dataset backtest
# ──────────────────────────────────────────────────────────────
def run_full_backtest(rolling_labels: pd.DataFrame,
                      horizon: int = DEFAULT_HORIZON) -> pd.DataFrame:
    """
    Run backtest_asset for every ticker column in *rolling_labels*.

    Returns
    -------
    pd.DataFrame — one row per ticker with columns:
        Ticker, TP, FP, FN, Precision, Recall, F1,
        mean_lead_time, std_lead_time, n_warnings, n_crashes
    """
    records = []
    for ticker in rolling_labels.columns:
        seq = rolling_labels[ticker].dropna()
        if seq.empty:
            continue

        res = backtest_asset(seq, horizon)

        tp, fp, fn = res["TP"], res["FP"], res["FN"]
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1        = (2 * precision * recall / (precision + recall)
                     if (precision + recall) > 0 else 0.0)

        lt = res["lead_times"]
        mean_lt = float(np.mean(lt)) if lt else np.nan
        std_lt  = float(np.std(lt))  if lt else np.nan

        warnings_count = len(_extract_events(seq, WARNING_CLUSTER))
        crashes_count  = len(_extract_events(seq, CRASH_CLUSTER))

        records.append({
            "Ticker":          ticker,
            "TP":              tp,
            "FP":              fp,
            "FN":              fn,
            "Precision":       round(precision, 4),
            "Recall":          round(recall, 4),
            "F1":              round(f1, 4),
            "mean_lead_time":  round(mean_lt, 1) if not np.isnan(mean_lt) else None,
            "std_lead_time":   round(std_lt, 1)  if not np.isnan(std_lt)  else None,
            "n_warnings":      warnings_count,
            "n_crashes":       crashes_count,
        })

    df = pd.DataFrame(records).set_index("Ticker")

    # Aggregate row
    totals = df[["TP", "FP", "FN"]].sum()
    tp_t, fp_t, fn_t = totals["TP"], totals["FP"], totals["FN"]
    p = tp_t / (tp_t + fp_t) if (tp_t + fp_t) > 0 else 0.0
    r = tp_t / (tp_t + fn_t) if (tp_t + fn_t) > 0 else 0.0
    f = 2 * p * r / (p + r) if (p + r) > 0 else 0.0

    all_lts = []
    for ticker in rolling_labels.columns:
        seq = rolling_labels[ticker].dropna()
        if seq.empty:
            continue
        res = backtest_asset(seq, horizon)
        all_lts.extend(res["lead_times"])

    agg = pd.DataFrame([{
        "Ticker":          "AGGREGATE",
        "TP":              int(tp_t),
        "FP":              int(fp_t),
        "FN":              int(fn_t),
        "Precision":       round(p, 4),
        "Recall":          round(r, 4),
        "F1":              round(f, 4),
        "mean_lead_time":  round(float(np.mean(all_lts)), 1) if all_lts else None,
        "std_lead_time":   round(float(np.std(all_lts)), 1)  if all_lts else None,
        "n_warnings":      int(df["n_warnings"].sum()),
        "n_crashes":       int(df["n_crashes"].sum()),
    }]).set_index("Ticker")

    return pd.concat([df, agg])


# ── Quick self-test ──────────────────────────────────────────
if __name__ == "__main__":
    print("[backtesting] Module loaded. Run via main.py.")
