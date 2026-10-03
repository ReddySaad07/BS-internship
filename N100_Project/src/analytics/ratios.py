# N100_Project/src/analytics/ratios.py

import numpy as np
import pandas as pd


def safe_divide(numerator, denominator):
    """Safely divide two numeric values."""
    try:
        numerator = float(numerator)
        denominator = float(denominator)
    except (TypeError, ValueError):
        return np.nan

    if pd.isna(numerator) or pd.isna(denominator):
        return np.nan

    if denominator == 0:
        return np.nan

    return numerator / denominator


def percentage(numerator, denominator):
    """Return numerator / denominator as a percentage."""
    value = safe_divide(numerator, denominator)

    if pd.isna(value):
        return np.nan

    return value * 100.0


def calculate_net_profit_margin(net_profit, revenue):
    return percentage(net_profit, revenue)


def calculate_operating_profit_margin(operating_profit, revenue):
    return percentage(operating_profit, revenue)


def calculate_roe(net_profit, equity):
    return percentage(net_profit, equity)


def calculate_roa(net_profit, total_assets):
    return percentage(net_profit, total_assets)


def calculate_roce(operating_profit, capital_employed):
    return percentage(operating_profit, capital_employed)


def calculate_debt_to_equity(debt, equity):
    return safe_divide(debt, equity)


def calculate_leverage(total_assets, equity):
    return safe_divide(total_assets, equity)


def calculate_interest_coverage(operating_profit, interest_expense):
    """
    Interest coverage.

    Zero interest expense is treated as Debt Free rather than infinity.
    """
    try:
        interest = float(interest_expense)
    except (TypeError, ValueError):
        return np.nan, "INVALID"

    if pd.isna(interest):
        return np.nan, "MISSING"

    if interest == 0:
        return np.nan, "DEBT_FREE"

    result = safe_divide(operating_profit, interest)

    if pd.isna(result):
        return np.nan, "INVALID"

    return result, "OK"


def calculate_net_debt(total_debt, cash):
    try:
        debt = float(total_debt)
        cash = float(cash)
    except (TypeError, ValueError):
        return np.nan

    if pd.isna(debt) or pd.isna(cash):
        return np.nan

    return debt - cash


def calculate_asset_turnover(revenue, total_assets):
    return safe_divide(revenue, total_assets)


def calculate_fcf(cfo, capex):
    """
    Free cash flow = CFO - CapEx.

    CapEx is normalized to a positive investment amount before subtraction.
    """
    if pd.isna(cfo) or pd.isna(capex):
        return np.nan

    try:
        return float(cfo) - abs(float(capex))
    except (TypeError, ValueError):
        return np.nan


def calculate_fcf_conversion(fcf, net_profit):
    return percentage(fcf, net_profit)


def calculate_cfo_quality(cfo, net_profit):
    return safe_divide(cfo, net_profit)
