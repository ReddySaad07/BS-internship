import numpy as np

from src.analytics.ratios import (
    safe_divide,
    percentage,
    calculate_debt_to_equity,
    calculate_net_debt,
)


def test_safe_divide():
    assert safe_divide(10, 2) == 5


def test_safe_divide_zero():
    assert np.isnan(
        safe_divide(10, 0)
    )


def test_percentage():
    assert percentage(10, 100) == 10


def test_debt_to_equity():
    assert calculate_debt_to_equity(
        50,
        100,
    ) == 0.5


def test_net_debt():
    assert calculate_net_debt(
        100,
        40,
    ) == 60
