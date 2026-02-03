import pandas as pd
import numpy as np
from scripts.signals import rsi, bollinger_bands, generate_signals_from_series


def test_rsi_basic():
    s = pd.Series([1,2,3,4,3,2,1,2,3,4,5,6,7,8,9])
    r = rsi(s, length=5)
    # RSI should be NaN at the beginning and have finite values later
    assert r.isna().sum() >= 1
    assert r.dropna().shape[0] > 0


def test_bollinger_basic():
    s = pd.Series(np.arange(1.0, 101.0))
    bb = bollinger_bands(s, length=20, stddev=2.0)
    assert 'upper' in bb.columns and 'lower' in bb.columns
    assert bb['upper'].isna().sum() >= 1


def test_generate_signals_simple():
    # craft a series where price is clearly below lower band and RSI low
    s = [100.0]*30 + [50.0]*25 + [100.0]*10
    signals = generate_signals_from_series(s, useRSI=True, rsiLength=14, rsiLongLevel=40, rsiShortLevel=60, useBB=True, bbLength=20, bbStdDev=2.0)
    # After the drop, expect at least one 'long' signal
    assert 'long' in signals
