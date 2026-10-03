from pathlib import Path
import sqlite3
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "db" / "nifty100.db"


def get_connection():
    """Return a SQLite connection with foreign keys enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def read_table(table_name):
    """Read an SQLite table into pandas."""
    with get_connection() as conn:
        return pd.read_sql_query(
            f"SELECT * FROM {table_name}",
            conn,
        )


def table_exists(table_name):
    """Check whether a table exists."""
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type='table' AND name=?
            """,
            (table_name,),
        ).fetchone()

    return row is not None
