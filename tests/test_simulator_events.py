from scripts.simulator import run_simulation


def test_simulator_events_recorded():
    prices = [100.0, 95.0, 100.0]
    signals = ['long', None, None]

    res = run_simulation(
        prices,
        signals,
        initial_balance=1000.0,
        risk_per_trade=1.0,
        leverage=10.0,
        commission_rate=0.1,
        useSL=False,
        useTP=True,
        tpPercent=3.0,
        useAveraging=True,
        avgDistancePercent=5.0,
        martingaleMultiplier=2.0,
        maxAvgCount=1,
        record_events=True,
    )

    assert res.events is not None
    # expect at least open, avg, close
    types = [e['type'] for e in res.events]
    assert 'open' in types
    assert 'avg' in types
    assert 'close' in types
    # check close event contains profit key
    close_events = [e for e in res.events if e['type'] == 'close']
    assert close_events and 'profit' in close_events[0]
