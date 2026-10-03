from pathlib import Path
import sqlite3
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "db" / "nifty100.db"


def main():
    connection = sqlite3.connect(DB_PATH)

    checks = []

    # DQ-01: company count
    companies = connection.execute(
        "SELECT COUNT(*) FROM companies"
    ).fetchone()[0]

    checks.append(
        ("DQ-01", "Company count = 92", companies == 92, companies)
    )

    # DQ-02: profit and loss rows
    pnl = connection.execute(
        "SELECT COUNT(*) FROM profit_loss"
    ).fetchone()[0]

    checks.append(
        ("DQ-02", "P&L rows > 0", pnl > 0, pnl)
    )

    # DQ-03: balance sheet rows
    bs = connection.execute(
        "SELECT COUNT(*) FROM balance_sheet"
    ).fetchone()[0]

    checks.append(
        ("DQ-03", "Balance sheet rows > 0", bs > 0, bs)
    )

    # DQ-04: cash flow rows
    cf = connection.execute(
        "SELECT COUNT(*) FROM cash_flow"
    ).fetchone()[0]

    checks.append(
        ("DQ-04", "Cash flow rows > 0", cf > 0, cf)
    )

    # DQ-05: financial ratios
    ratios = connection.execute(
        "SELECT COUNT(*) FROM financial_ratios"
    ).fetchone()[0]

    checks.append(
        ("DQ-05", "Financial ratios >= 1100", ratios >= 1100, ratios)
    )

    # DQ-06: stock prices
    prices = connection.execute(
        "SELECT COUNT(*) FROM stock_prices"
    ).fetchone()[0]

    checks.append(
        ("DQ-06", "Stock prices > 0", prices > 0, prices)
    )

    # DQ-07: sectors
    sectors = connection.execute(
        "SELECT COUNT(*) FROM sectors"
    ).fetchone()[0]

    checks.append(
        ("DQ-07", "Sector rows > 0", sectors > 0, sectors)
    )

    # DQ-08: foreign key integrity
    fk = connection.execute(
        "PRAGMA foreign_key_check"
    ).fetchall()

    checks.append(
        ("DQ-08", "Foreign key check = 0", len(fk) == 0, len(fk))
    )

    # DQ-09: duplicate company/year P&L records
    duplicates = connection.execute(
        """
        SELECT company_id, year, COUNT(*)
        FROM profit_loss
        WHERE year IS NOT NULL
        GROUP BY company_id, year
        HAVING COUNT(*) > 1
        """
    ).fetchall()

    checks.append(
        (
            "DQ-09",
            "P&L duplicate company/year records",
            len(duplicates) == 0,
            len(duplicates),
        )
    )

    # DQ-10: duplicate company/year balance-sheet records
    duplicates_bs = connection.execute(
        """
        SELECT company_id, year, COUNT(*)
        FROM balance_sheet
        WHERE year IS NOT NULL
        GROUP BY company_id, year
        HAVING COUNT(*) > 1
        """
    ).fetchall()

    checks.append(
        (
            "DQ-10",
            "Balance sheet duplicate company/year records",
            len(duplicates_bs) == 0,
            len(duplicates_bs),
        )
    )

    connection.close()

    print("=" * 70)
    print("SPRINT 1 DATA QUALITY CHECK")
    print("=" * 70)

    failures = 0

    for code, description, passed, value in checks:
        status = "PASS" if passed else "FAIL"

        if not passed:
            failures += 1

        print(
            f"{code}: {status} | {description} | value={value}"
        )

    print("=" * 70)
    print(f"CHECKS: {len(checks)}")
    print(f"FAILURES: {failures}")
    print("=" * 70)

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()