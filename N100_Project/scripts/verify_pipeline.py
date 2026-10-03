from pathlib import Path
import sqlite3
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "db" / "nifty100.db"


def check_table(conn, table):
    row = conn.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type='table' AND name=?
        """,
        (table,),
    ).fetchone()

    return row is not None


def main():
    print("=" * 70)
    print("N100 PIPELINE VERIFICATION")
    print("=" * 70)

    if not DB_PATH.exists():
        print("Database: NOT CREATED")
        print()
        print("Run:")
        print("python -m src.etl.run_etl")
        return

    print(
        f"Database: {DB_PATH}"
    )

    expected_tables = [
        "companies",
        "profit_loss",
        "balance_sheet",
        "cash_flow",
        "financial_ratios",
        "market_cap",
        "stock_prices",
        "peer_groups",
        "sectors",
        "documents",
    ]

    with sqlite3.connect(DB_PATH) as conn:

        for table in expected_tables:
            exists = check_table(
                conn,
                table,
            )

            if exists:
                count = conn.execute(
                    f"SELECT COUNT(*) FROM {table}"
                ).fetchone()[0]

                print(
                    f"{table:<20} "
                    f"{count:>8} rows"
                )

            else:
                print(
                    f"{table:<20} MISSING"
                )

        fk = conn.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

        print()
        print(
            f"Foreign-key errors: {len(fk)}"
        )

        if check_table(
            conn,
            "financial_ratios",
        ):
            count = conn.execute(
                """
                SELECT COUNT(*)
                FROM financial_ratios
                """
            ).fetchone()[0]

            print(
                f"Financial ratios rows: {count}"
            )

    print()
    print("Verification finished.")


if __name__ == "__main__":
    main()
