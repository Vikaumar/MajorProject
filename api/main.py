"""
FastAPI Backend for Climate Risk Velocity Dashboard
Serves processed CSV data from the pipeline output.
"""

import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np

# Add project root to path so we can import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# ─── Data loading (cached at startup) ────────────────────────
_cache = {}

def _load_all():
    """Load all CSVs once at startup."""
    d = config.DATA_DIR
    try:
        _cache["clusters"] = pd.read_csv(os.path.join(d, "cluster_assignments.csv"), index_col=0)
        _cache["clusters"]["cluster"] = _cache["clusters"]["cluster"].astype(int)
        _cache["clusters"]["Category"] = [
            config.TICKER_CATEGORY.get(t, "Unknown") for t in _cache["clusters"].index
        ]

        _cache["warnings"] = pd.read_csv(os.path.join(d, "warning_alerts.csv"), index_col=0)
        _cache["trans_matrix"] = pd.read_csv(os.path.join(d, "transition_matrix.csv"), index_col=0)
        _cache["prices"] = pd.read_csv(os.path.join(d, "prices.csv"), index_col=0, parse_dates=True)

        derivs = {}
        for ticker in config.ALL_TICKERS:
            path = os.path.join(d, f"derivatives_{ticker}.csv")
            if os.path.exists(path):
                df = pd.read_csv(path, index_col=0)
                df.index = pd.to_datetime(df.index)
                derivs[ticker] = df
        _cache["derivs"] = derivs

        rl_path = os.path.join(d, "rolling_cluster_labels.csv")
        if os.path.exists(rl_path):
            _cache["rolling_labels"] = pd.read_csv(rl_path, index_col=0, parse_dates=True)
        else:
            _cache["rolling_labels"] = None

        print(f"[OK] Loaded {len(derivs)} derivative files from {d}")
    except Exception as e:
        print(f"[ERROR] Failed to load data: {e}")


@asynccontextmanager
async def lifespan(app):
    _load_all()
    yield

app = FastAPI(title="Climate Risk Velocity API", version="2.0", lifespan=lifespan)

# Allow CORS for the React frontend (any origin for simplicity)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Helper ──────────────────────────────────────────────────
def _safe(val):
    """Convert numpy types to Python native for JSON serialization."""
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return float(val) if not np.isnan(val) else None
    if isinstance(val, (np.bool_,)):
        return bool(val)
    return val


# ─── Config endpoint ─────────────────────────────────────────
@app.get("/api/config")
def get_config():
    """Return all configuration values the frontend needs."""
    return {
        "allTickers": config.ALL_TICKERS,
        "fossilFuelTickers": config.FOSSIL_FUEL_TICKERS,
        "esgCleanTickers": config.ESG_CLEAN_TICKERS,
        "benchmarkTickers": config.BENCHMARK_TICKERS,
        "tickerCategory": config.TICKER_CATEGORY,
        "clusterLabels": {str(k): v for k, v in config.CLUSTER_LABELS.items()},
        "startDate": config.START_DATE,
        "endDate": config.END_DATE,
        "rollingWindow": config.ROLLING_WINDOW,
        "potQuantile": config.POT_QUANTILE,
        "minExceedances": config.MIN_EXCEEDANCES,
        "smoothingWindow": config.SMOOTHING_WINDOW,
        "smoothingPoly": config.SMOOTHING_POLY,
        "nClusters": config.N_CLUSTERS,
        "velocityWeightXi": config.VELOCITY_WEIGHT_XI,
        "velocityWeightSigma": config.VELOCITY_WEIGHT_SIGMA,
    }


# ─── Overview endpoint ───────────────────────────────────────
@app.get("/api/overview")
def get_overview():
    clusters = _cache.get("clusters")
    warnings = _cache.get("warnings")
    prices = _cache.get("prices")
    if clusters is None:
        raise HTTPException(500, "Data not loaded")

    avg_rvi = _safe(clusters["RVI"].mean())
    max_rvi = _safe(clusters["RVI"].max())
    n_warnings = int(warnings["is_warning_alert"].sum()) if warnings is not None else 0
    n_crash = int((clusters["cluster"] == 2).sum())

    return {
        "totalAssets": len(config.ALL_TICKERS),
        "tradingDays": len(prices) if prices is not None else 0,
        "avgRVI": avg_rvi,
        "maxRVI": max_rvi,
        "warningAlerts": n_warnings,
        "crashCluster": n_crash,
    }


# ─── Alerts endpoint ─────────────────────────────────────────
@app.get("/api/alerts")
def get_alerts():
    warnings = _cache.get("warnings")
    if warnings is None:
        raise HTTPException(500, "Data not loaded")

    records = []
    for ticker, row in warnings.iterrows():
        records.append({
            "ticker": ticker,
            "category": row.get("category", "Unknown"),
            "recentRVI": _safe(row.get("recent_RVI", 0)),
            "threshold": _safe(row.get("threshold", 0)),
            "isWarningAlert": bool(row.get("is_warning_alert", False)),
        })

    # Category averages
    grouped = warnings.groupby("category")["recent_RVI"].mean()
    categoryAvg = [
        {"category": cat, "avgRVI": _safe(val)}
        for cat, val in grouped.items()
    ]

    return {"alerts": records, "categoryAvg": categoryAvg}


# ─── Clusters endpoint ───────────────────────────────────────
@app.get("/api/clusters")
def get_clusters():
    clusters = _cache.get("clusters")
    if clusters is None:
        raise HTTPException(500, "Data not loaded")

    records = []
    for ticker, row in clusters.iterrows():
        records.append({
            "ticker": ticker,
            "category": row.get("Category", "Unknown"),
            "cluster": int(row["cluster"]),
            "clusterLabel": row.get("cluster_label", ""),
            "xi": _safe(row.get("xi", 0)),
            "sigma": _safe(row.get("sigma", 0)),
            "dxiDt": _safe(row.get("dxi_dt", 0)),
            "dsigmaDt": _safe(row.get("dsigma_dt", 0)),
            "RVI": _safe(row.get("RVI", 0)),
        })

    # Distribution counts
    counts = clusters["cluster"].value_counts().sort_index()
    distribution = [
        {"cluster": int(k), "label": config.CLUSTER_LABELS.get(k, f"C{k}"), "count": int(v)}
        for k, v in counts.items()
    ]

    return {"assets": records, "distribution": distribution}


# ─── Transition matrix endpoint ──────────────────────────────
@app.get("/api/transitions")
def get_transitions():
    tm = _cache.get("trans_matrix")
    if tm is None:
        raise HTTPException(500, "Data not loaded")

    labels = list(tm.index)
    matrix = tm.values.tolist()
    links = []
    n = len(labels)
    for i in range(n):
        for j in range(n):
            v = tm.iloc[i, j]
            if v > 0.001:
                links.append({
                    "source": i,
                    "target": n + j,
                    "value": round(float(v) * 100, 1),
                })

    return {"labels": labels, "matrix": matrix, "links": links}


# ─── Heatmap endpoint ────────────────────────────────────────
@app.get("/api/heatmap/{param}")
def get_heatmap(param: str):
    if param not in ("dxi_dt", "dsigma_dt", "RVI"):
        raise HTTPException(400, f"Invalid param: {param}")

    derivs = _cache.get("derivs", {})
    frames = {}
    for t, df in derivs.items():
        if param in df.columns:
            s = df[param].copy()
            try:
                resampled = s.resample("ME").mean()
            except ValueError:
                resampled = s.resample("M").mean()
            frames[t] = resampled

    if not frames:
        raise HTTPException(404, "No data for this parameter")

    matrix = pd.DataFrame(frames).T
    matrix.columns = pd.to_datetime(matrix.columns)
    col_labels = [d.strftime("%Y-%m") if pd.notnull(d) else "N/A" for d in matrix.columns]

    # Sort by category
    cat_order = {"Fossil Fuel": 0, "ESG / Clean Energy": 1, "Benchmark": 2}
    sort_key = [cat_order.get(config.TICKER_CATEGORY.get(t, ""), 3) for t in matrix.index]
    matrix["_sort"] = sort_key
    matrix = matrix.sort_values("_sort").drop("_sort", axis=1)

    values = matrix.values.tolist()
    tickers = matrix.index.tolist()

    # Replace NaN with None for JSON
    clean_values = []
    for row in values:
        clean_values.append([None if (isinstance(v, float) and np.isnan(v)) else v for v in row])

    flat = matrix.values.flatten()
    flat = flat[~np.isnan(flat)]

    return {
        "tickers": tickers,
        "months": col_labels,
        "values": clean_values,
        "stats": {
            "min": float(np.min(flat)) if len(flat) > 0 else 0,
            "mean": float(np.mean(flat)) if len(flat) > 0 else 0,
            "max": float(np.max(flat)) if len(flat) > 0 else 0,
            "std": float(np.std(flat)) if len(flat) > 0 else 0,
        },
    }


# ─── Asset deep-dive endpoint ────────────────────────────────
@app.get("/api/asset/{ticker}")
def get_asset(ticker: str):
    derivs = _cache.get("derivs", {})
    clusters = _cache.get("clusters")

    if ticker not in derivs:
        raise HTTPException(404, f"No derivative data for {ticker}")

    df = derivs[ticker]
    cat = config.TICKER_CATEGORY.get(ticker, "Unknown")

    rvi_series = df["RVI"].dropna()
    p90 = float(np.nanpercentile(rvi_series, 90))

    # Build time series arrays
    dates = [d.strftime("%Y-%m-%d") for d in df.index]

    def col_to_list(col):
        return [None if (isinstance(v, float) and np.isnan(v)) else float(v) for v in df[col]]

    return {
        "ticker": ticker,
        "category": cat,
        "meanRVI": _safe(rvi_series.mean()),
        "maxRVI": _safe(rvi_series.max()),
        "p90RVI": p90,
        "dates": dates,
        "rvi": col_to_list("RVI"),
        "xi": col_to_list("xi"),
        "sigma": col_to_list("sigma"),
        "dxiDt": col_to_list("dxi_dt"),
        "dsigmaDt": col_to_list("dsigma_dt"),
    }


# ─── Multi-asset comparison endpoint ─────────────────────────
@app.get("/api/compare")
def compare_assets(tickers: str = "XOM,ICLN,SPY"):
    ticker_list = [t.strip() for t in tickers.split(",") if t.strip()]
    derivs = _cache.get("derivs", {})

    result = {}
    for t in ticker_list:
        if t in derivs:
            df = derivs[t]
            dates = [d.strftime("%Y-%m-%d") for d in df.index]
            rvi = [None if (isinstance(v, float) and np.isnan(v)) else float(v) for v in df["RVI"]]
            result[t] = {"dates": dates, "rvi": rvi}

    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
