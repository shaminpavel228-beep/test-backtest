from scripts.trade_manager import Position


def test_open_and_avg_long():
    p = Position(is_long=True)
    p.open(entry_price=100.0, pos_vol=1.0, useSL=True, useTP=True, slPercent=1.0, tpPercent=2.0)
    assert p.active
    assert p.total_volume == 1.0
    assert p.avg_price() == 100.0

    # simulate price drop to next averaging level (distance 5%)
    avg_dist = 5.0
    next_level = p.next_avg_price(avg_dist)
    assert next_level == 95.0

    # price falls and triggers averaging
    close = 95.0
    assert p.should_average(close, avg_dist)

    newVol = p.add_average(close, martingaleMultiplier=2.0)
    # newVol should be total_volume_before * 2 = 1*2 = 2
    assert newVol == 2.0
    assert p.total_volume == 3.0
    # new average = (100*1 + 95*2)/3 = (100 + 190)/3 = 290/3
    assert abs(p.avg_price() - (290.0/3.0)) < 1e-9


def test_close_position_and_profit():
    p = Position(is_long=True)
    p.open(entry_price=100.0, pos_vol=1.0, useSL=False, useTP=False, slPercent=0.0, tpPercent=0.0)
    # add one average
    p.add_average(90.0, 1.0)
    # avg price = (100*1 + 90*1)/2 = 95
    profit, commission = p.close(100.0, commission_rate=0.1)
    # profit = (100 - 95)*2 = 10, commission = 2*100*0.001=0.2 -> result 10 - 0.2 = 9.8
    assert abs(profit - 9.8) < 1e-9
    assert abs(commission - 0.2) < 1e-9
    assert not p.active


def test_short_avg_and_next_level():
    p = Position(is_long=False)
    p.open(entry_price=200.0, pos_vol=2.0, useSL=True, useTP=False, slPercent=1.0, tpPercent=0.0)
    # for short, next avg price is higher
    nap = p.next_avg_price(5.0)
    assert nap == 210.0
    assert p.should_average(210.0, 5.0)
