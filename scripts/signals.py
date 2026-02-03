from typing import List, Optional, Dict
import numpy as np
import pandas as pd


def rsi(series: pd.Series, length: int) -> pd.Series:
    # Wilder's RSI (RMA / EMA with alpha=1/length)
    delta = series.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    # Wilder's smoothing (RMA) via EMA with alpha=1/length
    avg_gain = gain.ewm(alpha=1.0/length, adjust=False, min_periods=length).mean()
    avg_loss = loss.ewm(alpha=1.0/length, adjust=False, min_periods=length).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def bollinger_bands(series: pd.Series, length: int, stddev: float) -> pd.DataFrame:
    basis = series.rolling(length, min_periods=length).mean()
    # population std (ddof=0) to match Pine ta.stdev behavior
    dev = series.rolling(length, min_periods=length).std(ddof=0)
    upper = basis + stddev * dev
    lower = basis - stddev * dev
    return pd.DataFrame({'basis': basis, 'upper': upper, 'lower': lower})


def generate_signals_from_series(
    close: List[float],
    useRSI: bool = True,
    rsiLength: int = 14,
    rsiLongLevel: int = 30,
    rsiShortLevel: int = 70,
    useBB: bool = True,
    bbLength: int = 20,
    bbStdDev: float = 2.0,
) -> List[Optional[str]]:
    """Replicate Pine logic for finalLongSignal/finalShortSignal.
    Returns a list of 'long' / 'short' / None per bar aligning with input close list.
    """
    s = pd.Series(close)
    rsi_series = rsi(s, rsiLength) if useRSI else pd.Series([np.nan]*len(s))
    bb = bollinger_bands(s, bbLength, bbStdDev) if useBB else pd.DataFrame({'upper': [np.nan]*len(s), 'lower': [np.nan]*len(s)})

    rsiLongSignal = (useRSI) & (rsi_series <= rsiLongLevel)
    rsiShortSignal = (useRSI) & (rsi_series >= rsiShortLevel)
    bbLongSignal = (useBB) & (s <= bb['lower'])
    bbShortSignal = (useBB) & (s >= bb['upper'])

    finalLong = pd.Series([False]*len(s))
    finalShort = pd.Series([False]*len(s))

    if useRSI and useBB:
        finalLong = rsiLongSignal & bbLongSignal
        finalShort = rsiShortSignal & bbShortSignal
    elif useRSI:
        finalLong = rsiLongSignal
        finalShort = rsiShortSignal
    elif useBB:
        finalLong = bbLongSignal
        finalShort = bbShortSignal

    signals: List[Optional[str]] = []
    for long, short in zip(finalLong.fillna(False), finalShort.fillna(False)):
        if long:
            signals.append('long')
        elif short:
            signals.append('short')
        else:
            signals.append(None)
    return signals
