import math
from scripts import pine_calc


def test_calculate_average_price_basic():
    prices = [100.0, 110.0]
    vols = [1.0, 1.0]
    assert pine_calc.calculate_average_price(prices, vols) == 105.0


def test_calculate_average_price_with_none():
    prices = [100.0, None, 120.0]
    vols = [1.0, 2.0, 1.0]
    # ignore None price (effectively [100*1 + 120*1] / (1+1) = 110)
    assert pine_calc.calculate_average_price(prices, vols) == 110.0


def test_calculate_position_volume_and_limits():
    entry_price = 100.0
    current_balance = 1000.0
    risk_per_trade = 1.0
    leverage = 10.0
    pos_vol = pine_calc.calculate_position_volume(entry_price, current_balance, risk_per_trade, leverage)
    assert math.isclose(pos_vol, 0.1)


def test_calculate_commission():
    assert math.isclose(pine_calc.calculate_commission(0.1, 100.0, 0.1), 0.01)


def test_calculate_liquidation_price():
    entry = 100.0
    long_liq = pine_calc.calculate_liquidation_price(entry, True, 10.0, margin_type='Isolated')
    short_liq = pine_calc.calculate_liquidation_price(entry, False, 10.0, margin_type='Isolated')
    assert long_liq < entry
    assert short_liq > entry


def test_check_sufficient_funds():
    # current no used positions
    assert pine_calc.check_sufficient_funds(0.1, 100.0, 1000.0, 0, 0, False, 0, False, 0, 10.0)
    # with used margin so only small free margin
    ok = pine_calc.check_sufficient_funds(10.0, 100.0, 1000.0, 0.0, 0.0, False, 0.0, False, 0.0, 100.0)
    assert ok is True


def test_calculate_pnl_with_commission():
    import math
    pnl = pine_calc.calculate_pnl(100.0, 110.0, 1.0, True, 0.1)
    # profit = 10, commission = 1*110*(0.1/100) = 0.11 -> result = 9.89
    assert math.isclose(pnl, 9.89, rel_tol=1e-6)
