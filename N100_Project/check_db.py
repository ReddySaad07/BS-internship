import sqlite3

db_path = "db/nifty100.db"

connection = sqlite3.connect(db_path)

print("TABLES:")
tables = connection.execute(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
).fetchall()

for table in tables:
    print(" -", table[0])

print("\nROW COUNTS:")

table_names = [
    "companies",
    "profit_loss",
    "balance_sheet",
    "cash_flow",
    "documents",
    "pros_cons",
    "analysis",
    "financial_ratios",
    "market_cap",
    "peer_groups",
    "sectors",
    "stock_prices",
]

for table in table_names:
    count = connection.execute(
        f"SELECT COUNT(*) FROM {table}"
    ).fetchone()[0]

    print(f" - {table}: {count}")

print("\nFOREIGN KEY CHECK:")
foreign_keys = connection.execute(
    "PRAGMA foreign_key_check"
).fetchall()

print(foreign_keys)

connection.close()