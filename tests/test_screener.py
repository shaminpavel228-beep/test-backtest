import pandas as pd
import pytest
from unittest.mock import patch

from scripts import screener


def make_sample_df():
    idx = pd.date_range('2023-01-01', periods=3, freq='D')
    df = pd.DataFrame({
        'Open': [100, 101, 102],
        'High': [101, 102, 103],
        'Low': [99, 100, 101],
        'Close': [100.5, 101.5, 102.5],
        'Adj Close': [100.5, 101.5, 102.5],
        'Volume': [1000, 1100, 1200],
    }, index=idx)
    return df


def test_fetch_data_raises_without_period_or_dates():
    with pytest.raises(ValueError):
        screener.fetch_data('AAPL')


@patch('scripts.screener.yf.download')
def test_fetch_data_and_save(mock_download, tmp_path):
    sample = make_sample_df()
    mock_download.return_value = sample

    path = screener.fetch_and_save('AAPL', period='1d')
    assert path.exists()
    df2 = pd.read_csv(path, index_col=0, parse_dates=True)
    assert df2.shape[0] == 3
    assert 'Close' in df2.columns
