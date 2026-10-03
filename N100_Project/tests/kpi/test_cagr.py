from src.analytics.cagr import calculate_cagr


def test_cagr_positive():
    value, flag = calculate_cagr(
        100,
        121,
        2,
    )

    assert round(value, 2) == 10.0
    assert flag == "OK"


def test_cagr_negative_base():
    value, flag = calculate_cagr(
        -100,
        100,
        2,
    )

    assert flag == "TURNAROUND"


def test_cagr_zero_base():
    value, flag = calculate_cagr(
        0,
        100,
        2,
    )

    assert flag == "ZERO_BASE"
