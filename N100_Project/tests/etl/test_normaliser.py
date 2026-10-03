import pandas as pd

from src.etl.normaliser import (
    clean_column_name,
    normalise_company_id,
    normalise_columns,
)


def test_clean_column_name():
    assert clean_column_name(
        "Net Profit Margin (%)"
    ) == "net_profit_margin"


def test_company_id():
    assert normalise_company_id(
        " tcs "
    ) == "TCS"


def test_normalise_columns():
    df = pd.DataFrame(
        columns=["Company ID", "Revenue"]
    )

    result = normalise_columns(df)

    assert "company_id" in result.columns
    assert "revenue" in result.columns
