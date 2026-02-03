import pytest
from scripts import pine_calc


def test_position_volume_zero_entry():
    with pytest.raises(ValueError):
        pine_calc.calculate_position_volume(0.0, 1000.0, 1.0, 10.0)


def test_position_volume_negative_params():
    with pytest.raises(ValueError):
        pine_calc.calculate_position_volume(100.0, -1.0, 1.0, 10.0)
    with pytest.raises(ValueError):
        pine_calc.calculate_position_volume(100.0, 1000.0, -1.0, 10.0)
    with pytest.raises(ValueError):
        pine_calc.calculate_position_volume(100.0, 1000.0, 1.0, 0.0)


def test_commission_negative():
    with pytest.raises(ValueError):
        pine_calc.calculate_commission(-0.1, 100.0, 0.1)
    with pytest.raises(ValueError):
        pine_calc.calculate_commission(0.1, -100.0, 0.1)
    with pytest.raises(ValueError):
        pine_calc.calculate_commission(0.1, 100.0, -0.1)


def test_liquidation_invalid_inputs():
    with pytest.raises(ValueError):
        pine_calc.calculate_liquidation_price(0.0, True, 10.0)
    with pytest.raises(ValueError):
        pine_calc.calculate_liquidation_price(100.0, True, 0.0)


def test_pnl_negative_tradevol():
    with pytest.raises(ValueError):
        pine_calc.calculate_pnl(100.0, 110.0, -1.0, True, 0.1)
