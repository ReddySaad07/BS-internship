from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from src.etl.normaliser import normalise_dataframe
from src.etl.validator import (
    ValidationFailure,
    failures_to_dataframe,
    validate_dataframe,
)


ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
SUPPORTING = RAW / "supporting datasets"
DB_PATH = ROOT / "db" / "nifty100.db"
PROCESSED = ROOT / "data" / "processed"


# Main project datasets use the second Excel row as the header.
MAIN_DATASETS = {
    "companies": (
        RAW / "companies.xlsx",
        [
            "id",
            "company_logo",
            "company_name",
            "chart_link",
            "about_company",
            "website",
            "nse_profile",
            "bse_profile",
            "face_value",
            "book_value",
            "roce_percentage",
            "roe_percentage",
        ],
    ),
    "profit_loss": (
        RAW / "profitandloss.xlsx",
        [
            "id",
            "company_id",
            "year",
            "sales",
            "expenses",
            "operating_profit",
            "opm_percentage",
            "other_income",
            "interest",
            "depreciation",
            "profit_before_tax",
            "tax_percentage",
            "net_profit",
            "eps",
            "dividend_payout",
        ],
    ),
    "balance_sheet": (
        RAW / "balancesheet.xlsx",
        [
            "id",
            "company_id",
            "year",
            "equity_capital",
            "reserves",
            "borrowings",
            "other_liabilities",
            "total_liabilities",
            "fixed_assets",
            "cwip",
            "investments",
            "other_asset",
            "total_assets",
        ],
    ),
    "cash_flow": (
        RAW / "cashflow.xlsx",
        [
            "id",
            "company_id",
            "year",
            "operating_activity",
            "investing_activity",
            "financing_activity",
            "net_cash_flow",
        ],
    ),
    "documents": (
        RAW / "documents.xlsx",
        [
            "id",
            "company_id",
            "year",
            "annual_report",
        ],
    ),
    "pros_cons": (
        RAW / "prosandcons.xlsx",
        [
            "id",
            "company_id",
            "pros",
            "cons",
        ],
    ),
    "analysis": (
        RAW / "analysis.xlsx",
        [
            "id",
            "company_id",
            "compounded_sales_growth",
            "compounded_profit_growth",
            "stock_price_cagr",
            "roe",
        ],
    ),
}


# These five supporting datasets have their actual header on Excel row 1.
SUPPORTING_DATASETS = {
    "financial_ratios": (
        SUPPORTING / "financial_ratios.xlsx",
        [
            "id",
            "company_id",
            "year",
            "net_profit_margin_pct",
            "operating_profit_margin_pct",
            "return_on_equity_pct",
            "debt_to_equity",
            "interest_coverage",
            "asset_turnover",
            "free_cash_flow_cr",
            "capex_cr",
            "earnings_per_share",
            "book_value_per_share",
            "dividend_payout_ratio_pct",
            "total_debt_cr",
            "cash_from_operations_cr",
        ],
    ),
    "market_cap": (
        SUPPORTING / "market_cap.xlsx",
        [
            "id",
            "company_id",
            "year",
            "market_cap_crore",
            "enterprise_value_crore",
            "pe_ratio",
            "pb_ratio",
            "ev_ebitda",
            "dividend_yield_pct",
        ],
    ),
    "peer_groups": (
        SUPPORTING / "peer_groups.xlsx",
        [
            "id",
            "peer_group_name",
            "company_id",
            "is_benchmark",
        ],
    ),
    "sectors": (
        SUPPORTING / "sectors.xlsx",
        [
            "id",
            "company_id",
            "broad_sector",
            "sub_sector",
            "index_weight_pct",
            "market_cap_category",
        ],
    ),
    "stock_prices": (
        SUPPORTING / "stock_prices.xlsx",
        [
            "id",
            "company_id",
            "date",
            "open_price",
            "high_price",
            "low_price",
            "close_price",
            "volume",
            "adjusted_close",
        ],
    ),
}


def read_excel(path: Path, header_row: int) -> pd.DataFrame:
    """Read an Excel source using its source-specific header row."""
    return pd.read_excel(path, header=header_row)


def prepare_dataframe(
    df: pd.DataFrame,
    table_name: str,
    expected_columns: list[str],
) -> pd.DataFrame:
    """Normalise and safely coerce a source dataframe."""

    df = normalise_dataframe(df)

    # Keep only the expected source columns.
    missing = [c for c in expected_columns if c not in df.columns]

    if missing:
        raise ValueError(
            f"{table_name}: missing columns after normalisation: {missing}\n"
            f"Actual columns: {list(df.columns)}"
        )

    df = df[expected_columns].copy()

    # IDs are deliberately treated as text.
    # This avoids SQLite datatype mismatch for source IDs.
    if "id" in df.columns:
        df["id"] = df["id"].astype("string")

    if "company_id" in df.columns:
        df["company_id"] = df["company_id"].astype("string")

    # Numeric columns.
    numeric_exclusions = {
        "id",
        "company_id",
        "peer_group_name",
        "is_benchmark",
        "broad_sector",
        "sub_sector",
        "market_cap_category",
        "date",
        "annual_report",
        "pros",
        "cons",
        "company_logo",
        "company_name",
        "chart_link",
        "about_company",
        "website",
        "nse_profile",
        "bse_profile",
    }

    for column in df.columns:
        if column not in numeric_exclusions:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    # Years are integers when available.
    if "year" in df.columns:
        df["year"] = pd.to_numeric(
            df["year"],
            errors="coerce",
        ).astype("Int64")

    # Remove completely blank records.
    df = df.dropna(how="all")

    return df


def create_database() -> None:
    """Create a fresh SQLite database from schema.sql."""

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    schema_path = ROOT / "db" / "schema.sql"

    if not schema_path.exists():
        raise FileNotFoundError(
            f"Schema file not found: {schema_path}"
        )

    # Start from a clean database for a reproducible ETL.
    if DB_PATH.exists():
        DB_PATH.unlink()

    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("PRAGMA foreign_keys = ON")

        schema = schema_path.read_text(
            encoding="utf-8"
        )

        connection.executescript(schema)


def load_dataset(
    connection: sqlite3.Connection,
    table_name: str,
    path: Path,
    required_columns: list[str],
    header_row: int,
) -> tuple[int, list[ValidationFailure]]:

    if not path.exists():
        raise FileNotFoundError(
            f"Missing source file: {path}"
        )

    df = read_excel(path, header_row)

    df = prepare_dataframe(
        df,
        table_name,
        required_columns,
    )

    failures = validate_dataframe(
        df,
        required_columns=required_columns,
        dataset_name=table_name,
    )

    # Write exactly into the already-created SQLite table.
    df.to_sql(
        table_name,
        connection,
        if_exists="append",
        index=False,
    )

    return len(df), failures


def run_loader() -> None:
    """Load all 12 Excel datasets into SQLite."""

    PROCESSED.mkdir(
        parents=True,
        exist_ok=True,
    )

    create_database()

    audit_rows = []
    all_failures: list[ValidationFailure] = []

    with sqlite3.connect(DB_PATH) as connection:

        connection.execute(
            "PRAGMA foreign_keys = ON"
        )

        # Main datasets: header=1.
        for table_name, (
            path,
            required_columns,
        ) in MAIN_DATASETS.items():

            count, failures = load_dataset(
                connection,
                table_name,
                path,
                required_columns,
                header_row=1,
            )

            audit_rows.append(
                {
                    "table_name": table_name,
                    "source_file": str(
                        path.relative_to(ROOT)
                    ),
                    "rows_loaded": count,
                    "validation_failures": len(
                        failures
                    ),
                }
            )

            all_failures.extend(failures)

            print(
                f"Loaded {table_name}: {count} rows"
            )

        # Supporting datasets: header=0.
        for table_name, (
            path,
            required_columns,
        ) in SUPPORTING_DATASETS.items():

            count, failures = load_dataset(
                connection,
                table_name,
                path,
                required_columns,
                header_row=0,
            )

            audit_rows.append(
                {
                    "table_name": table_name,
                    "source_file": str(
                        path.relative_to(ROOT)
                    ),
                    "rows_loaded": count,
                    "validation_failures": len(
                        failures
                    ),
                }
            )

            all_failures.extend(failures)

            print(
                f"Loaded {table_name}: {count} rows"
            )

        # SQLite foreign-key integrity.
        fk_rows = connection.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

        audit_rows.append(
            {
                "table_name": "DATABASE",
                "source_file": str(
                    DB_PATH.relative_to(ROOT)
                ),
                "rows_loaded": None,
                "validation_failures": len(
                    fk_rows
                ),
            }
        )

        connection.commit()

    pd.DataFrame(audit_rows).to_csv(
        PROCESSED / "load_audit.csv",
        index=False,
    )

    failures_df = failures_to_dataframe(
        all_failures
    )

    failures_df.to_csv(
        PROCESSED / "validation_failures.csv",
        index=False,
    )

    print()
    print("=" * 60)
    print("SPRINT 1 ETL COMPLETE")
    print("=" * 60)
    print(f"Database: {DB_PATH}")
    print(
        f"Load audit: "
        f"{PROCESSED / 'load_audit.csv'}"
    )
    print(
        f"Validation failures: "
        f"{len(failures_df)}"
    )


if __name__ == "__main__":
    run_loader()