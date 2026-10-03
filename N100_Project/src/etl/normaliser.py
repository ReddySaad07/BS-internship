from __future__ import annotations

import re
from typing import Any

import pandas as pd


def clean_column_name(value: Any) -> str:
    text = str(value).strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def normalise_columns(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    result.columns = [clean_column_name(c) for c in result.columns]
    return result


def normalise_company_id(value: Any) -> str | None:
    if pd.isna(value):
        return None

    text = str(value).strip().upper()

    if not text or text == "NAN":
        return None

    return text


def normalise_company_column(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    if "company_id" in result.columns:
        result["company_id"] = result["company_id"].map(
            normalise_company_id
        )

    return result


def normalise_year(value: Any) -> int | None:
    """
    Convert financial year labels into calendar years.

    Examples:
        'Mar 2014' -> 2014
        'Mar-14'   -> 2014
        'Dec 2012' -> 2012
        '2019'     -> 2019
        'TTM'      -> None

    TTM is deliberately returned as None because it is
    a trailing-twelve-month observation rather than a
    calendar-year observation.
    """

    if pd.isna(value):
        return None

    text = str(value).strip()

    if not text or text.upper() == "TTM":
        return None

    # Four-digit year anywhere in the value.
    match = re.search(r"(19|20)\d{2}", text)

    if match:
        return int(match.group(0))

    # Two-digit year such as Mar-13.
    match = re.search(r"(?:^|[-/ ])(\d{2})$", text)

    if match:
        two_digit_year = int(match.group(1))

        if two_digit_year <= 30:
            return 2000 + two_digit_year

        return 1900 + two_digit_year

    return None


def normalise_year_column(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    if "year" in result.columns:
        result["year"] = result["year"].map(normalise_year)

    return result


def normalise_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    result = normalise_columns(df)
    result = normalise_company_column(result)
    result = normalise_year_column(result)

    return result