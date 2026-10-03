from pathlib import Path
import sqlite3
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "db" / "nifty100.db"
OUTPUT_DIR = ROOT / "output"


def generate_portfolio_summary():
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query(
            "SELECT * FROM financial_ratios",
            conn,
        )

    if df.empty:
        raise RuntimeError(
            "No financial ratio data available."
        )

    latest = (
        df.sort_values(
            ["company_id", "year"]
        )
        .drop_duplicates(
            "company_id",
            keep="last",
        )
    )

    metrics = [
        "roe",
        "roce",
        "roa",
        "net_profit_margin",
        "operating_profit_margin",
        "debt_to_equity",
        "revenue_cagr_5y",
        "fcf_cagr_5y",
        "fcf_conversion_pct",
    ]

    records = []

    for metric in metrics:

        if metric not in latest.columns:
            continue

        values = pd.to_numeric(
            latest[metric],
            errors="coerce",
        )

        records.append({
            "metric": metric,
            "companies": int(values.notna().sum()),
            "mean": values.mean(),
            "median": values.median(),
            "minimum": values.min(),
            "maximum": values.max(),
        })

    summary = pd.DataFrame(records)

    summary.to_csv(
        OUTPUT_DIR / "portfolio_stats.csv",
        index=False,
    )

    print("Portfolio statistics created.")


if __name__ == "__main__":
    generate_portfolio_summary()
