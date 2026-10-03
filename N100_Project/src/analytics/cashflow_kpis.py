# N100_Project/src/analytics/cashflow_kpis.py

import numpy as np
import pandas as pd


def calculate_fcf(cfo, capex):
    """Calculate free cash flow as CFO minus absolute CapEx."""
    try:
        cfo = float(cfo)
        capex = float(capex)
    except (TypeError, ValueError):
        return np.nan

    if pd.isna(cfo) or pd.isna(capex):
        return np.nan

    return cfo - abs(capex)


def calculate_fcf_conversion(fcf, net_profit):
    """FCF as a percentage of net profit."""
    try:
        fcf = float(fcf)
        net_profit = float(net_profit)
    except (TypeError, ValueError):
        return np.nan

    if pd.isna(fcf) or pd.isna(net_profit) or net_profit == 0:
        return np.nan

    return (fcf / net_profit) * 100.0


def calculate_cfo_conversion(cfo, revenue):
    """CFO as a percentage of revenue."""
    try:
        cfo = float(cfo)
        revenue = float(revenue)
    except (TypeError, ValueError):
        return np.nan

    if pd.isna(cfo) or pd.isna(revenue) or revenue == 0:
        return np.nan

    return (cfo / revenue) * 100.0


def classify_cfo_quality(cfo, net_profit):
    """
    Simple CFO quality classification.

    CFO >= PAT is considered supportive.
    """
    try:
        cfo = float(cfo)
        pat = float(net_profit)
    except (TypeError, ValueError):
        return "INSUFFICIENT_DATA"

    if pd.isna(cfo) or pd.isna(pat):
        return "INSUFFICIENT_DATA"

    if pat == 0:
        return "PAT_ZERO"

    ratio = cfo / pat

    if ratio >= 1:
        return "STRONG"
    if ratio >= 0.75:
        return "HEALTHY"
    if ratio >= 0.5:
        return "MODERATE"

    return "WEAK"


def add_cashflow_kpis(df):
    """Add cash-flow KPI columns to a dataframe."""
    df = df.copy()

    df["fcf"] = df.apply(
        lambda r: calculate_fcf(
            r.get("cfo"),
            r.get("capex"),
        ),
        axis=1,
    )

    df["fcf_conversion_pct"] = df.apply(
        lambda r: calculate_fcf_conversion(
            r.get("fcf"),
            r.get("net_profit"),
        ),
        axis=1,
    )

    df["cfo_conversion_pct"] = df.apply(
        lambda r: calculate_cfo_conversion(
            r.get("cfo"),
            r.get("revenue"),
        ),
        axis=1,
    )

    df["cfo_quality"] = df.apply(
        lambda r: classify_cfo_quality(
            r.get("cfo"),
            r.get("net_profit"),
        ),
        axis=1,
    )

    return df
