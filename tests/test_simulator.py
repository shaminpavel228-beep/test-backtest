from scripts.simulator import run_simulation


def test_simulator_long_avg_close():
    # prices: open at 100 -> avg at 95 -> close at 100
    prices = [100.0, 95.0, 100.0]
    # signal to open long at first bar, others no new signals
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
    )

    # Expected: one trade, one win (closed with profit) — check final balance increased
    assert res.trades == 1
    assert res.wins == 1
    assert res.final_balance > 1000.0
    assert res.total_profit > 0


def test_simulator_prevent_open_on_insufficient_funds():
    # If current balance is tiny, position shouldn't open
    prices = [100.0]
    signals = ['long']
    res = run_simulation(prices, signals, initial_balance=1.0, risk_per_trade=1.0, leverage=1.0)
    assert res.trades == 0
    assert res.final_balance == 1.0
