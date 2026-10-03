from src.analytics.cashflow_kpis import (
    calculate_fcf,
    calculate_fcf_conversion,
    classify_cfo_quality,
)


def test_fcf():
    assert calculate_fcf(
        100,
        40,
    ) == 60


def test_fcf_conversion():
    assert calculate_fcf_conversion(
        50,
        100,
    ) == 50


def test_cfo_quality():
    assert classify_cfo_quality(
        120,
        100,
    ) == "STRONG"
