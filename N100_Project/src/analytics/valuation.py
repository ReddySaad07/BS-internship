from pathlib import Path
import sqlite3
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "db" / "nifty100.db"
OUTPUT_DIR = ROOT / "output"


def safe(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return np.nan


def build_valuation():
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with sqlite3.connect(DB_PATH) as conn:
        ratios = pd.read_sql_query(
            "SELECT * FROM financial_ratios",
            conn,
        )

        market = pd.read_sql_query(
            "SELECT * FROM market_cap",
            conn,
        )

    if ratios.empty:
        raise RuntimeError(
            "No financial ratios available."
        )

    latest = (
        ratios.sort_values(
            ["company_id", "year"]
        )
        .drop_duplicates(
            "company_id",
            keep="last",
        )
    )

    market.columns = [
        str(c).strip().lower()
        for c in market.columns
    ]

    if "company_id" in market.columns:
        market["company_id"] = (
            market["company_id"]
            .astype(str)
            .str.strip()
            .str.upper()
        )

    market_value_column = next(
        (
            c for c in [
                "market_cap",
                "market_capitalisation",
                "market_capitalization",
            ]
            if c in market.columns
        ),
        None,
    )

    if market_value_column:
        market_latest = (
            market.sort_values(
                [
                    "company_id"
                ]
                + (
                    ["year"]
                    if "year" in market.columns
                    else []
                )
            )
            .drop_duplicates(
                "company_id",
                keep="last",
            )
            [
                [
                    "company_id",
                    market_value_column,
                ]
            ]
        )

        latest = latest.merge(
            market_latest,
            on="company_id",
            how="left",
        )

    else:
        latest["market_cap"] = np.nan

    if "market_cap" not in latest.columns:
        latest["market_cap"] = np.nan

    latest["market_cap"] = pd.to_numeric(
        latest["market_cap"],
        errors="coerce",
    )

    latest["pe_proxy"] = (
        latest["market_cap"]
        / pd.to_numeric(
            latest["net_profit_margin"],
            errors="coerce",
        )
    )

    latest["valuation_flag"] = np.select(
        [
            latest["debt_to_equity"] > 2,
            latest["roe"] < 0,
            latest["revenue_cagr_5y"] < 0,
        ],
        [
            "HIGH_LEVERAGE",
            "NEGATIVE_ROE",
            "NEGATIVE_REVENUE_GROWTH",
        ],
        default="NO_FLAG",
    )

    latest[
        [
            "company_id",
            "year",
            "market_cap",
            "pe_proxy",
            "valuation_flag",
        ]
    ].to_csv(
        OUTPUT_DIR / "valuation_flags.csv",
        index=False,
    )

    latest.to_excel(
        OUTPUT_DIR / "valuation_summary.xlsx",
        index=False,
    )

    print("Valuation outputs created.")


if __name__ == "__main__":
    build_valuation()
