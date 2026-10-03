# N100_Project/src/analytics/cagr.py

import numpy as np
import pandas as pd


def calculate_cagr(start_value, end_value, years):
    """
    Calculate CAGR.

    Negative or zero starting values cannot produce a standard CAGR.
    In those cases a flag is returned so the pipeline does not crash.
    """
    try:
        start = float(start_value)
        end = float(end_value)
        years = int(years)
    except (TypeError, ValueError):
        return np.nan, "INVALID"

    if years <= 0:
        return np.nan, "INVALID"

    if pd.isna(start) or pd.isna(end):
        return np.nan, "MISSING"

    if start == 0:
        return np.nan, "ZERO_BASE"

    if start < 0:
        if end > 0:
            return np.nan, "TURNAROUND"
        return np.nan, "NEGATIVE_BASE"

    if end < 0:
        return np.nan, "NEGATIVE_END"

    try:
        value = ((end / start) ** (1.0 / years) - 1.0) * 100.0
        return float(value), "OK"
    except (ValueError, ZeroDivisionError, OverflowError):
        return np.nan, "INVALID"


def series_cagr(series, years):
    """Calculate CAGR from a chronological pandas Series."""
    series = series.dropna()

    if len(series) < 2:
        return np.nan, "MISSING"

    series = series.sort_index()

    if len(series) <= years:
        return np.nan, "INSUFFICIENT_HISTORY"

    start = series.iloc[-(years + 1)]
    end = series.iloc[-1]

    return calculate_cagr(start, end, years)


def add_cagr_columns(df, value_column, group_column="company_id"):
    """
    Add 3-year and 5-year CAGR columns to a dataframe.

    Rows are calculated independently by company and year.
    """
    df = df.copy()

    cagr_3 = []
    flag_3 = []
    cagr_5 = []
    flag_5 = []

    for _, group in df.groupby(group_column):
        group = group.sort_values("year")

        values = group[value_column].tolist()
        years = group["year"].tolist()

        result_3 = {}
        result_5 = {}

        for index, year in enumerate(years):
            if index >= 3:
                value, flag = calculate_cagr(
                    values[index - 3],
                    values[index],
                    3,
                )
            else:
                value, flag = np.nan, "INSUFFICIENT_HISTORY"

            result_3[year] = (value, flag)

            if index >= 5:
                value, flag = calculate_cagr(
                    values[index - 5],
                    values[index],
                    5,
                )
            else:
                value, flag = np.nan, "INSUFFICIENT_HISTORY"

            result_5[year] = (value, flag)

        for year in years:
            v3, f3 = result_3[year]
            v5, f5 = result_5[year]

            cagr_3.append((year, v3, f3))
            flag_3.append((year, f3))
            cagr_5.append((year, v5, f5))
            flag_5.append((year, f5))

    # The function is primarily provided as a reusable utility.
    # Build_ratios.py performs the final alignment explicitly.
    return df
