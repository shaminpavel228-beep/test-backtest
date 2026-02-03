from typing import List, Optional
from dataclasses import dataclass, field

from scripts import pine_calc


@dataclass
class Position:
    is_long: bool
    active: bool = False
    avg_prices: List[float] = field(default_factory=list)
    avg_volumes: List[float] = field(default_factory=list)
    avg_count: int = 0
    total_volume: float = 0.0
    entry_price: Optional[float] = None
    stop_loss_price: Optional[float] = None
    take_profit_price: Optional[float] = None

    def open(self, entry_price: float, pos_vol: float, useSL: bool, useTP: bool, slPercent: float, tpPercent: float):
        if entry_price <= 0 or pos_vol <= 0:
            raise ValueError("entry_price and pos_vol must be > 0")
        self.active = True
        self.entry_price = entry_price
        self.avg_prices = [entry_price]
        self.avg_volumes = [pos_vol]
        self.avg_count = 0
        self.total_volume = pos_vol
        # initialize stops/tp based on entry; update_targets is used after averaging
        if useSL:
            self.stop_loss_price = (entry_price * (1 - slPercent / 100)) if self.is_long else (entry_price * (1 + slPercent / 100))
        else:
            self.stop_loss_price = None
        if useTP:
            self.take_profit_price = (entry_price * (1 + tpPercent / 100)) if self.is_long else (entry_price * (1 - tpPercent / 100))
        else:
            self.take_profit_price = None

    def update_targets(self, useSL: bool, useTP: bool, slPercent: float, tpPercent: float):
        """Recompute stop-loss and take-profit based on current average price."""
        ap = self.avg_price()
        if ap is None:
            return
        if useSL:
            self.stop_loss_price = (ap * (1 - slPercent / 100)) if self.is_long else (ap * (1 + slPercent / 100))
        else:
            self.stop_loss_price = None
        if useTP:
            self.take_profit_price = (ap * (1 + tpPercent / 100)) if self.is_long else (ap * (1 - tpPercent / 100))
        else:
            self.take_profit_price = None
    def avg_price(self) -> Optional[float]:
        return pine_calc.calculate_average_price(self.avg_prices, self.avg_volumes)

    def next_avg_price(self, avgDistancePercent: float) -> Optional[float]:
        ap = self.avg_price()
        if ap is None:
            return None
        if self.is_long:
            return ap * (1 - avgDistancePercent / 100.0)
        else:
            return ap * (1 + avgDistancePercent / 100.0)

    def should_average(self, close: float, avgDistancePercent: float) -> bool:
        nap = self.next_avg_price(avgDistancePercent)
        if nap is None:
            return False
        if self.is_long:
            return close <= nap
        else:
            return close >= nap

    def add_average(self, close: float, martingaleMultiplier: float):
        if not self.active:
            raise RuntimeError("position not active")
        if martingaleMultiplier <= 0:
            raise ValueError("martingaleMultiplier must be > 0")
        newVol = self.total_volume * martingaleMultiplier
        self.avg_count += 1
        self.avg_prices.append(close)
        self.avg_volumes.append(newVol)
        self.total_volume += newVol
        # after averaging, we might want to update stops/tp externally based on new avg
        return newVol

    def close(self, close_price: float, commission_rate: float):
        if not self.active:
            raise RuntimeError("position not active")
        ap = self.avg_price()
        if ap is None:
            raise RuntimeError("no average price")
        profit = pine_calc.calculate_pnl(ap, close_price, self.total_volume, self.is_long, commission_rate)
        commission = pine_calc.calculate_commission(self.total_volume, close_price, commission_rate)
        self.active = False
        self.avg_count = 0
        return profit, commission
