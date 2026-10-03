# N100_Project/src/analytics/capital_allocation.py

import numpy as np


def classify_capital_allocation(
    capex=None,
    dividends=None,
    buybacks=None,
    debt_change=None,
    cash_change=None,
):
    """
    Classify broad capital-allocation behavior using available signals.

    This intentionally returns descriptive patterns rather than an
    investment recommendation.
    """
    values = {
        "capex": capex,
        "dividends": dividends,
        "buybacks": buybacks,
        "debt_change": debt_change,
        "cash_change": cash_change,
    }

    numeric = {}

    for key, value in values.items():
        try:
            numeric[key] = float(value)
        except (TypeError, ValueError):
            numeric[key] = np.nan

    capex = numeric["capex"]
    dividends = numeric["dividends"]
    buybacks = numeric["buybacks"]
    debt_change = numeric["debt_change"]
    cash_change = numeric["cash_change"]

    if not np.isnan(capex) and capex > 0:
        if not np.isnan(debt_change) and debt_change > 0:
            return "REINVESTMENT_WITH_DEBT"

        if not np.isnan(cash_change) and cash_change < 0:
            return "REINVESTMENT_FROM_CASH"

        return "REINVESTMENT"

    if not np.isnan(dividends) and dividends > 0:
        if not np.isnan(buybacks) and buybacks > 0:
            return "SHAREHOLDER_DISTRIBUTION"

        return "DIVIDEND_DISTRIBUTION"

    if not np.isnan(buybacks) and buybacks > 0:
        return "BUYBACK"

    if not np.isnan(debt_change) and debt_change < 0:
        return "DEBT_REDUCTION"

    if not np.isnan(cash_change) and cash_change > 0:
        return "CASH_BUILD"

    return "MIXED_OR_INSUFFICIENT_DATA"
