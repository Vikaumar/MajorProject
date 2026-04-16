"""
Data Acquisition Module
-----------------------
Downloads historical stock prices via yfinance and computes
negative log-returns (loss series) for EVT analysis.
"""

import pandas as pd
import numpy as np
import yfinance as yf
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config


def fetch_prices(tickers: list[str] = None,
                 start: str = None,
                 end: str = None) -> pd.DataFrame:
    """
    Download adjusted close prices for the given tickers.

    Returns
    -------
    pd.DataFrame  — columns = tickers, index = Date
    """
    tickers = tickers or config.ALL_TICKERS
    start   = start or config.START_DATE
    end     = end or config.END_DATE

    print(f"[data] Downloading prices for {len(tickers)} tickers "
          f"({start} → {end}) ...")

    raw = yf.download(tickers, start=start, end=end,
                      auto_adjust=True, progress=False)

    # yfinance may return MultiIndex columns; extract 'Close'
    if isinstance(raw.columns, pd.MultiIndex):
        prices = raw["Close"]
    else:
        prices = raw[["Close"]].rename(columns={"Close": tickers[0]})

    prices = prices.dropna(how="all")
    print(f"[data] Received {len(prices)} trading days, "
          f"{prices.shape[1]} tickers.")
    return prices


def compute_negative_log_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """
    Compute negative log-returns (i.e. losses).
    Positive values = losses, suitable for POT / GPD modelling.
    """
    log_ret = np.log(prices / prices.shift(1))
    neg_log_ret = -log_ret
    neg_log_ret = neg_log_ret.iloc[1:]          # drop first NaN row
    return neg_log_ret


def save_data(prices: pd.DataFrame,
              losses: pd.DataFrame) -> None:
    """Persist raw prices and loss series to CSV."""
    prices.to_csv(os.path.join(config.DATA_DIR, "prices.csv"))
    losses.to_csv(os.path.join(config.DATA_DIR, "negative_log_returns.csv"))
    print(f"[data] Saved CSVs to {config.DATA_DIR}")


# ── Quick self-test ──────────────────────────────────────────
if __name__ == "__main__":
    prices = fetch_prices()
    losses = compute_negative_log_returns(prices)
    save_data(prices, losses)
    print(losses.describe())
