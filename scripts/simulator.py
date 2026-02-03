from dataclasses import dataclass
from typing import List, Optional

from scripts.trade_manager import Position
from scripts import pine_calc


@dataclass
class SimulationResult:
    final_balance: float
    total_profit: float
    total_commission: float
    wins: int
    losses: int
    trades: int


def run_simulation(
    prices: List[float],
    signals: List[Optional[str]],  # 'long' | 'short' | None
    initial_balance: float = 1000.0,
    risk_per_trade: float = 1.0,
    leverage: float = 10.0,
    commission_rate: float = 0.1,
    margin_type: str = 'Cross',
    useSL: bool = False,
    useTP: bool = False,
    slPercent: float = 1.0,
    tpPercent: float = 2.0,
    useAveraging: bool = True,
    avgDistancePercent: float = 5.0,
    martingaleMultiplier: float = 2.0,
    maxAvgCount: int = 3,
    min_notional: float = 1.0,
):
    assert len(prices) == len(signals)

    current_balance = initial_balance
    total_profit = 0.0
    total_commission = 0.0
    wins = 0
    losses = 0
    trades = 0

    long_pos = Position(is_long=True)
    short_pos = Position(is_long=False)

    longPositionActive = False
    shortPositionActive = False

    long_total_volume = 0.0
    short_total_volume = 0.0

    for i, close in enumerate(prices):
        sig = signals[i]

        # Open position if signal and no position active
        if sig == 'long' and not long_pos.active and not short_pos.active:
            pos_vol = pine_calc.calculate_position_volume(close, current_balance, risk_per_trade, leverage)
            if pos_vol > 0 and pos_vol * close >= min_notional and pine_calc.check_sufficient_funds(pos_vol, close, current_balance, long_total_volume, short_total_volume, long_pos.active, long_pos.entry_price or 0.0, short_pos.active, short_pos.entry_price or 0.0, leverage):
                long_pos.open(close, pos_vol, useSL, useTP, slPercent, tpPercent)
                long_total_volume = long_pos.total_volume
                trades += 1
            else:
                # not enough notional or funds to open
                pass
        elif sig == 'short' and not short_pos.active and not long_pos.active:
            pos_vol = pine_calc.calculate_position_volume(close, current_balance, risk_per_trade, leverage)
            if pos_vol > 0 and pine_calc.check_sufficient_funds(pos_vol, close, current_balance, long_total_volume, short_total_volume, long_pos.active, long_pos.entry_price or 0.0, short_pos.active, short_pos.entry_price or 0.0, leverage):
                short_pos.open(close, pos_vol, useSL, useTP, slPercent, tpPercent)
                short_total_volume = short_pos.total_volume
                trades += 1
            else:
                # not enough notional or funds to open
                pass
        # Averaging
        if long_pos.active and useAveraging and long_pos.avg_count < maxAvgCount:
            if long_pos.should_average(close, avgDistancePercent):
                newVol = long_pos.total_volume * martingaleMultiplier
                if pine_calc.check_sufficient_funds(newVol, close, current_balance, long_total_volume, short_total_volume, long_pos.active, long_pos.entry_price or 0.0, short_pos.active, short_pos.entry_price or 0.0, leverage):
                    long_pos.add_average(close, martingaleMultiplier)
                    # update TP/SL after averaging to match Pine behaviour
                    long_pos.update_targets(useSL, useTP, slPercent, tpPercent)
                    long_total_volume = long_pos.total_volume

        if short_pos.active and useAveraging and short_pos.avg_count < maxAvgCount:
            if short_pos.should_average(close, avgDistancePercent):
                newVol = short_pos.total_volume * martingaleMultiplier
                if pine_calc.check_sufficient_funds(newVol, close, current_balance, long_total_volume, short_total_volume, long_pos.active, long_pos.entry_price or 0.0, short_pos.active, short_pos.entry_price or 0.0, leverage):
                    short_pos.add_average(close, martingaleMultiplier)
                    # update TP/SL after averaging to match Pine behaviour
                    short_pos.update_targets(useSL, useTP, slPercent, tpPercent)
                    short_total_volume = short_pos.total_volume

        # Closing logic for long
        if long_pos.active:
            ap = long_pos.avg_price()
            if ap is not None:
                should_close = False
                close_reason = ''
                if useTP and close >= long_pos.take_profit_price:
                    should_close = True
                    close_reason = 'TP'
                elif useSL and close <= long_pos.stop_loss_price:
                    should_close = True
                    close_reason = 'SL'
                elif not useSL:
                    liqPrice = pine_calc.calculate_liquidation_price(ap, True, leverage, margin_type)
                    if close <= liqPrice:
                        should_close = True
                        close_reason = 'LIQ'
                if should_close:
                    profit, commission = long_pos.close(close, commission_rate)
                    current_balance += profit
                    total_profit += profit
                    total_commission += commission
                    if profit >= 0:
                        wins += 1
                    else:
                        losses += 1

        # Closing logic for short
        if short_pos.active:
            ap = short_pos.avg_price()
            if ap is not None:
                should_close = False
                close_reason = ''
                if useTP and close <= short_pos.take_profit_price:
                    should_close = True
                    close_reason = 'TP'
                elif useSL and close >= short_pos.stop_loss_price:
                    should_close = True
                    close_reason = 'SL'
                elif not useSL:
                    liqPrice = pine_calc.calculate_liquidation_price(ap, False, leverage, margin_type)
                    if close >= liqPrice:
                        should_close = True
                        close_reason = 'LIQ'
                if should_close:
                    profit, commission = short_pos.close(close, commission_rate)
                    current_balance += profit
                    total_profit += profit
                    total_commission += commission
                    if profit >= 0:
                        wins += 1
                    else:
                        losses += 1

    return SimulationResult(
        final_balance=current_balance,
        total_profit=total_profit,
        total_commission=total_commission,
        wins=wins,
        losses=losses,
        trades=trades,
    )
