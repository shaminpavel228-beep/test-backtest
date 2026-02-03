from scripts.simulator import run_simulation_from_prices


def test_run_simulation_from_prices_basic():
    prices = [100.0]*30 + [50.0]*25 + [100.0]*10
    res = run_simulation_from_prices(prices, record_events=True, useAveraging=True)
    assert res.trades >= 1
    assert res.events is not None
    # Expect at least one 'open' and one 'close' event
    types = [e['type'] for e in res.events]
    assert 'open' in types
    assert 'close' in types
