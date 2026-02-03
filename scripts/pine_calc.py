"""Python equivalents of key Pine helper functions used in the backtest.
These are intentionally small, deterministic, and mirror the Pine implementations in
`pine/src/parts/25_section_25.pine` so they can be unit-tested outside TradingView.
"""
from typing import List, Optional


def calculate_average_price(prices: List[float], volumes: List[float]) -> Optional[float]:
    total_value = 0.0
    total_vol = 0.0
    for p, v in zip(prices, volumes):
        if p is None:
            continue
        total_value += p * v
        total_vol += v
    return total_value / total_vol if total_vol > 0 else None


def calculate_position_volume(entry_price: float, current_balance: float, risk_per_trade: float, leverage: float) -> float:
    if entry_price <= 0:
        raise ValueError("entry_price must be > 0")
    if current_balance < 0 or risk_per_trade < 0 or leverage <= 0:
        raise ValueError("invalid parameters: balance/risk/leverage must be non-negative and leverage > 0")
    pos_vol = (current_balance * (risk_per_trade / 100.0)) / entry_price
    max_vol = (current_balance * leverage) / entry_price
    return min(pos_vol, max_vol)


def calculate_commission(trade_vol: float, price: float, commission_rate: float) -> float:
    if trade_vol < 0 or price < 0 or commission_rate < 0:
        raise ValueError("trade_vol, price and commission_rate must be non-negative")
    return (trade_vol * price) * (commission_rate / 100.0)


def calculate_liquidation_price(entry_price: float, is_long: bool, leverage: float, margin_type: str = "Cross") -> float:
    if entry_price <= 0 or leverage <= 0:
        raise ValueError("entry_price and leverage must be > 0")
    # mirror Pine logic: isolated uses 0.9 factor, cross uses 0.8
    if margin_type.lower().startswith('из') or margin_type.lower().startswith('iso') or margin_type.lower() == 'isolated':
        factor = 0.9
    else:
        factor = 0.8
    if is_long:
        return entry_price * (1 - (1 / leverage) * factor)
    else:
        return entry_price * (1 + (1 / leverage) * factor)


def check_sufficient_funds(trade_vol: float, price: float, current_balance: float, long_total_volume: float, short_total_volume: float, long_position_active: bool, long_entry_price: float, short_position_active: bool, short_entry_price: float, leverage: float) -> bool:
    required_margin = (trade_vol * price) / leverage
    used_margin = 0.0
    if long_position_active:
        used_margin += long_total_volume * (long_entry_price or 0.0)
    if short_position_active:
        used_margin += short_total_volume * (short_entry_price or 0.0)
    used_margin /= leverage
    free_margin = current_balance - used_margin
    return required_margin <= free_margin


def calculate_pnl(entry_price: float, exit_price: float, trade_vol: float, is_long: bool, commission_rate: float) -> float:
    if trade_vol < 0:
        raise ValueError("trade_vol must be non-negative")
    if is_long:
        profit = (exit_price - entry_price) * trade_vol
    else:
        profit = (entry_price - exit_price) * trade_vol
    commission_fee = calculate_commission(trade_vol, exit_price, commission_rate)
    return profit - commission_fee
