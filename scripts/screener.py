"""Simple screener to download OHLCV historical data using yfinance.
Provides functions for fetching and saving CSVs to `pine/data/` for later use in TradingView/Pine comparisons.
"""
from pathlib import Path
from typing import Optional

import pandas as pd
import yfinance as yf

DATA_DIR = Path('pine/data')
DATA_DIR.mkdir(parents=True, exist_ok=True)


def fetch_data(ticker: str, start: Optional[str] = None, end: Optional[str] = None, period: Optional[str] = None, interval: str = '1d') -> pd.DataFrame:
    """Download OHLCV data for `ticker`.

    Either provide `period` (e.g. '1mo', '1y') or `start`/`end` as 'YYYY-MM-DD'.
    Returns a DataFrame with columns ['Open','High','Low','Close','Adj Close','Volume'] and a DatetimeIndex.
    """
    if period is None and (start is None and end is None):
        raise ValueError('Either period or start/end must be provided')

    # yfinance API: yf.download
    df = yf.download(ticker, start=start, end=end, period=period, interval=interval, progress=False)
    if df.empty:
        raise RuntimeError(f'No data returned for {ticker} (period={period} start={start} end={end} interval={interval})')
    return df


def fetch_and_save(ticker: str, start: Optional[str] = None, end: Optional[str] = None, period: Optional[str] = None, interval: str = '1d') -> Path:
    """Fetch data and save to CSV under `pine/data/<ticker>.csv` (returns path)."""
    df = fetch_data(ticker, start=start, end=end, period=period, interval=interval)
    out = DATA_DIR / f"{ticker.replace('/','_')}.csv"
    df.to_csv(out)
    return out


if __name__ == '__main__':
    # small CLI example
    import argparse

    p = argparse.ArgumentParser(description='Fetch historical OHLCV via yfinance and save as CSV')
    p.add_argument('ticker')
    p.add_argument('--period', default='1mo')
    p.add_argument('--interval', default='1d')
    p.add_argument('--start', default=None)
    p.add_argument('--end', default=None)
    args = p.parse_args()

    path = fetch_and_save(args.ticker, start=args.start, end=args.end, period=args.period, interval=args.interval)
    print('Saved', path)
