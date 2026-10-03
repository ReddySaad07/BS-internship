# N100_Project/src/analytics/build_ratios.py

from pathlib import Path
import sqlite3
import numpy as np
import pandas as pd

from .ratios import (
    calculate_net_profit_margin,
    calculate_operating_profit_margin,
    calculate_roe,
    calculate_roa,
    calculate_roce,
    calculate_debt_to_equity,
    calculate_leverage,
    calculate_interest_coverage,
    calculate_net_debt,
    calculate_asset_turnover,
)
from .cashflow_kpis import (
    calculate_fcf,
    calculate_fcf_conversion,
    calculate_cfo_conversion,
    classify_cfo_quality,
)
from .cagr import calculate_cagr


ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "db" / "nifty100.db"
OUTPUT_DIR = ROOT / "output"

FINANCIAL_RATIOS_CSV = OUTPUT_DIR / "financial_ratios.csv"
CAPITAL_ALLOCATION_CSV = OUTPUT_DIR / "capital_allocation.csv"
EDGE_LOG = OUTPUT_DIR / "ratio_edge_cases.log"


def read_table(conn, table_name):
    """Read an SQLite table into pandas."""
    try:
        return pd.read_sql_query(
            f"SELECT * FROM {table_name}",
            conn,
        )
    except Exception:
        return pd.DataFrame()


def first_existing(df, names):
    """Return the first available column from a list of candidates."""
    for name in names:
        if name in df.columns:
            return name
    return None


def numeric_series(df, candidates):
    """Return a numeric series using the first matching candidate."""
    column = first_existing(df, candidates)

    if column is None:
        return pd.Series(np.nan, index=df.index)

    return pd.to_numeric(df[column], errors="coerce")


def prepare_financials(conn):
    """Build a broad annual financial dataframe."""
    pl = read_table(conn, "profit_loss")
    bs = read_table(conn, "balance_sheet")
    cf = read_table(conn, "cash_flow")

    if pl.empty:
        return pd.DataFrame()

    # Normalize common column aliases.
    for df in (pl, bs, cf):
        if not df.empty:
            df.columns = [
                str(c).strip().lower().replace(" ", "_")
                for c in df.columns
            ]

    # Required identifiers.
    for df in (pl, bs, cf):
        if "company_id" in df.columns:
            df["company_id"] = (
                df["company_id"]
                .astype(str)
                .str.strip()
                .str.upper()
            )

        if "year" in df.columns:
            df["year"] = pd.to_numeric(
                df["year"],
                errors="coerce",
            )

    pl = pl.dropna(
        subset=["company_id", "year"]
    ).copy()

    pl["revenue"] = numeric_series(
        pl,
        [
            "revenue",
            "sales",
            "total_revenue",
            "net_sales",
        ],
    )

    pl["net_profit"] = numeric_series(
        pl,
        [
            "net_profit",
            "profit_after_tax",
            "pat",
            "net_income",
            "profit",
        ],
    )

    pl["operating_profit"] = numeric_series(
        pl,
        [
            "operating_profit",
            "ebit",
            "operating_income",
            "profit_before_interest_and_tax",
        ],
    )

    pl["interest_expense"] = numeric_series(
        pl,
        [
            "interest_expense",
            "interest",
            "finance_cost",
            "finance_costs",
        ],
    )

    if "interest_expense" not in pl:
        pl["interest_expense"] = np.nan

    # Avoid multiplying rows if source files contain duplicate company/year
    # records. Keep the first source record for each annual observation.
    pl = (
        pl.sort_values(["company_id", "year"])
        .drop_duplicates(
            subset=["company_id", "year"],
            keep="first",
        )
    )

    if not bs.empty and {"company_id", "year"}.issubset(bs.columns):
        bs = bs.drop_duplicates(
            subset=["company_id", "year"],
            keep="first",
        )

        bs["total_assets"] = numeric_series(
            bs,
            [
                "total_assets",
                "assets",
                "total_asset",
            ],
        )

        bs["equity"] = numeric_series(
            bs,
            [
                "equity",
                "shareholders_equity",
                "total_equity",
                "net_worth",
            ],
        )

        bs["total_debt"] = numeric_series(
            bs,
            [
                "total_debt",
                "debt",
                "borrowings",
                "total_borrowings",
                "gross_debt",
            ],
        )

        bs["cash"] = numeric_series(
            bs,
            [
                "cash",
                "cash_and_cash_equivalents",
                "cash_equivalents",
                "cash_bank_balance",
            ],
        )

        bs["current_liabilities"] = numeric_series(
            bs,
            [
                "current_liabilities",
                "total_current_liabilities",
            ],
        )

        bs["current_assets"] = numeric_series(
            bs,
            [
                "current_assets",
                "total_current_assets",
            ],
        )

        bs = bs[
            [
                "company_id",
                "year",
                "total_assets",
                "equity",
                "total_debt",
                "cash",
                "current_liabilities",
                "current_assets",
            ]
        ]

        pl = pl.merge(
            bs,
            on=["company_id", "year"],
            how="left",
        )

    else:
        for column in [
            "total_assets",
            "equity",
            "total_debt",
            "cash",
            "current_liabilities",
            "current_assets",
        ]:
            pl[column] = np.nan

    if not cf.empty and {"company_id", "year"}.issubset(cf.columns):
        cf = cf.drop_duplicates(
            subset=["company_id", "year"],
            keep="first",
        )

        cf["cfo"] = numeric_series(
            cf,
            [
                "cfo",
                "cash_from_operations",
                "cash_flow_from_operations",
                "operating_cash_flow",
                "net_cash_from_operating_activities",
            ],
        )

        cf["capex"] = numeric_series(
            cf,
            [
                "capex",
                "capital_expenditure",
                "capital_expenditures",
                "purchase_of_fixed_assets",
                "purchase_of_property_plant_and_equipment",
            ],
        )

        cf = cf[
            [
                "company_id",
                "year",
                "cfo",
                "capex",
            ]
        ]

        pl = pl.merge(
            cf,
            on=["company_id", "year"],
            how="left",
        )

    else:
        pl["cfo"] = np.nan
        pl["capex"] = np.nan

    return pl


def add_cagrs(df):
    """Add 3-year and 5-year CAGR values by company."""
    df = df.copy()

    for value_column, prefix in [
        ("revenue", "revenue"),
        ("net_profit", "pat"),
        ("fcf", "fcf"),
    ]:
        df[f"{prefix}_cagr_3y"] = np.nan
        df[f"{prefix}_cagr_3y_flag"] = ""
        df[f"{prefix}_cagr_5y"] = np.nan
        df[f"{prefix}_cagr_5y_flag"] = ""

        for company_id, index in df.groupby(
            "company_id"
        ).groups.items():

            group = (
                df.loc[index]
                .sort_values("year")
            )

            years = group["year"].tolist()
            values = group[value_column].tolist()

            for position, row_index in enumerate(
                group.index
            ):
                if position >= 3:
                    value, flag = calculate_cagr(
                        values[position - 3],
                        values[position],
                        3,
                    )
                    df.loc[
                        row_index,
                        f"{prefix}_cagr_3y"
                    ] = value
                    df.loc[
                        row_index,
                        f"{prefix}_cagr_3y_flag"
                    ] = flag
                else:
                    df.loc[
                        row_index,
                        f"{prefix}_cagr_3y_flag"
                    ] = "INSUFFICIENT_HISTORY"

                if position >= 5:
                    value, flag = calculate_cagr(
                        values[position - 5],
                        values[position],
                        5,
                    )
                    df.loc[
                        row_index,
                        f"{prefix}_cagr_5y"
                    ] = value
                    df.loc[
                        row_index,
                        f"{prefix}_cagr_5y_flag"
                    ] = flag
                else:
                    df.loc[
                        row_index,
                        f"{prefix}_cagr_5y_flag"
                    ] = "INSUFFICIENT_HISTORY"

    return df


def build_ratios():
    """Build the financial_ratios table from annual financial statements."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    edge_cases = []

    with sqlite3.connect(DB_PATH) as conn:
        df = prepare_financials(conn)

        if df.empty:
            raise RuntimeError(
                "No profit_loss data available. "
                "Run the ETL before building ratios."
            )

        # Core ratios.
        df["net_profit_margin"] = [
            calculate_net_profit_margin(a, b)
            for a, b in zip(
                df["net_profit"],
                df["revenue"],
            )
        ]

        df["operating_profit_margin"] = [
            calculate_operating_profit_margin(a, b)
            for a, b in zip(
                df["operating_profit"],
                df["revenue"],
            )
        ]

        df["roe"] = [
            calculate_roe(a, b)
            for a, b in zip(
                df["net_profit"],
                df["equity"],
            )
        ]

        df["roa"] = [
            calculate_roa(a, b)
            for a, b in zip(
                df["net_profit"],
                df["total_assets"],
            )
        ]

        capital_employed = (
            df["total_assets"]
            - df["current_liabilities"]
        )

        df["roce"] = [
            calculate_roce(a, b)
            for a, b in zip(
                df["operating_profit"],
                capital_employed,
            )
        ]

        df["debt_to_equity"] = [
            calculate_debt_to_equity(a, b)
            for a, b in zip(
                df["total_debt"],
                df["equity"],
            )
        ]

        df["leverage"] = [
            calculate_leverage(a, b)
            for a, b in zip(
                df["total_assets"],
                df["equity"],
            )
        ]

        interest_results = [
            calculate_interest_coverage(a, b)
            for a, b in zip(
                df["operating_profit"],
                df["interest_expense"],
            )
        ]

        df["interest_coverage"] = [
            value for value, _ in interest_results
        ]

        df["interest_coverage_flag"] = [
            flag for _, flag in interest_results
        ]

        df["net_debt"] = [
            calculate_net_debt(a, b)
            for a, b in zip(
                df["total_debt"],
                df["cash"],
            )
        ]

        df["asset_turnover"] = [
            calculate_asset_turnover(a, b)
            for a, b in zip(
                df["revenue"],
                df["total_assets"],
            )
        ]

        # Cash-flow metrics.
        df["fcf"] = [
            calculate_fcf(a, b)
            for a, b in zip(
                df["cfo"],
                df["capex"],
            )
        ]

        df["fcf_conversion_pct"] = [
            calculate_fcf_conversion(a, b)
            for a, b in zip(
                df["fcf"],
                df["net_profit"],
            )
        ]

        df["cfo_conversion_pct"] = [
            calculate_cfo_conversion(a, b)
            for a, b in zip(
                df["cfo"],
                df["revenue"],
            )
        ]

        df["cfo_quality"] = [
            classify_cfo_quality(a, b)
            for a, b in zip(
                df["cfo"],
                df["net_profit"],
            )
        ]

        # CAGR metrics.
        df = add_cagrs(df)

        # Record important edge cases instead of hiding them.
        for _, row in df.iterrows():

            if row["interest_coverage_flag"] == "DEBT_FREE":
                edge_cases.append(
                    f'{row["company_id"]} '
                    f'{int(row["year"])}: '
                    "interest expense is zero -> Debt Free"
                )

            if row["revenue_cagr_5y_flag"] == "TURNAROUND":
                edge_cases.append(
                    f'{row["company_id"]} '
                    f'{int(row["year"])}: '
                    "negative revenue CAGR base -> TURNAROUND"
                )

            if row["pat_cagr_5y_flag"] == "TURNAROUND":
                edge_cases.append(
                    f'{row["company_id"]} '
                    f'{int(row["year"])}: '
                    "negative PAT CAGR base -> TURNAROUND"
                )

        # Store the required financial ratio fields.
        ratio_columns = [
            "company_id",
            "year",
            "net_profit_margin",
            "operating_profit_margin",
            "roe",
            "roce",
            "roa",
            "debt_to_equity",
            "leverage",
            "interest_coverage",
            "interest_coverage_flag",
            "net_debt",
            "asset_turnover",
            "revenue_cagr_3y",
            "revenue_cagr_3y_flag",
            "revenue_cagr_5y",
            "revenue_cagr_5y_flag",
            "pat_cagr_3y",
            "pat_cagr_3y_flag",
            "pat_cagr_5y",
            "pat_cagr_5y_flag",
            "fcf_cagr_3y",
            "fcf_cagr_3y_flag",
            "fcf_cagr_5y",
            "fcf_cagr_5y_flag",
            "cfo",
            "capex",
            "fcf",
            "fcf_conversion_pct",
            "cfo_conversion_pct",
            "cfo_quality",
        ]

        output = df[
            [c for c in ratio_columns if c in df.columns]
        ].copy()

        # Match the SQLite schema.
        target_columns = [
            row[1]
            for row in conn.execute(
                "PRAGMA table_info(financial_ratios)"
            ).fetchall()
        ]

        for column in target_columns:
            if column not in output.columns:
                output[column] = None

        output = output[target_columns]

        conn.execute("DELETE FROM financial_ratios")

        output.to_sql(
            "financial_ratios",
            conn,
            if_exists="append",
            index=False,
        )

        conn.commit()

        output.to_csv(
            FINANCIAL_RATIOS_CSV,
            index=False,
        )

    EDGE_LOG.write_text(
        "\n".join(edge_cases)
        if edge_cases
        else "No recorded edge cases.",
        encoding="utf-8",
    )

    print(
        f"financial_ratios built successfully: "
        f"{len(output)} rows"
    )
    print(f"CSV: {FINANCIAL_RATIOS_CSV}")
    print(f"Edge log: {EDGE_LOG}")


if __name__ == "__main__":
    build_ratios()
