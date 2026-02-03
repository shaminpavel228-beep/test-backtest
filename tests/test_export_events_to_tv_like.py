import pandas as pd
from pathlib import Path
from scripts.export_events_to_tv_like import convert_events_to_trades

def test_convert_events_to_trades(tmp_path):
    # create fake price CSV
    price_csv = tmp_path / "PRICE.csv"
    # simple two-row price with dates
    price_df = pd.DataFrame({'Close':[100.0, 110.0]}, index=pd.to_datetime(['2025-01-01', '2025-01-02']))
    price_df.index.name = 'Date'
    price_df.to_csv(price_csv)

    # create events: open at bar 0, close at bar 1
    events_csv = tmp_path / "events.csv"
    events = pd.DataFrame([
        {'type':'open','side':'long','price':100.0,'volume':1.0,'bar':0},
        {'type':'close','side':'long','price':110.0,'volume':'','bar':1,'profit':10.0,'commission':0.1,'reason':'TP'},
    ])
    events.to_csv(events_csv, index=False)

    out = tmp_path / 'tv_trades.csv'
    convert_events_to_trades(str(events_csv), str(price_csv), str(out))

    assert out.exists()
    df = pd.read_csv(out)
    assert df.shape[0] == 1
    assert df.iloc[0]['Side'] == 'long'
    assert df.iloc[0]['Entry Price'] == 100.0
    assert df.iloc[0]['Exit Price'] == 110.0
