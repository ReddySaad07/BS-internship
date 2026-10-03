from pathlib import Path
import sqlite3
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "db" / "nifty100.db"
OUTPUT_DIR = ROOT / "output"


PEER_METRICS = [
    "roe",
    "roce",
    "roa",
    "net_profit_margin",
    "operating_profit_margin",
    "debt_to_equity",
    "leverage",
    "revenue_cagr_5y",
    "fcf_cagr_5y",
    "fcf_conversion_pct",
]


def build_peer_percentiles():
    with sqlite3.connect(DB_PATH) as conn:
        ratios = pd.read_sql_query(
            "SELECT * FROM financial_ratios",
            conn,
        )

        peers = pd.read_sql_query(
            "SELECT * FROM peer_groups",
            conn,
        )

    if ratios.empty:
        raise RuntimeError(
            "financial_ratios is empty."
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

    if peers.empty:
        peers = latest[
            ["company_id"]
        ].copy()

        peers["peer_group"] = "All Companies"
    else:
        peers.columns = [
            str(c).strip().lower()
            for c in peers.columns
        ]

        if "peer_group" not in peers.columns:
            possible = [
                c for c in peers.columns
                if "peer" in c
            ]

            if possible:
                peers["peer_group"] = (
                    peers[possible[0]]
                )
            else:
                peers["peer_group"] = (
                    "All Companies"
                )

    merged = latest.merge(
        peers[
            [
                c for c in [
                    "company_id",
                    "peer_group",
                ]
                if c in peers.columns
            ]
        ],
        on="company_id",
        how="left",
    )

    merged["peer_group"] = (
        merged["peer_group"]
        .fillna("All Companies")
        .astype(str)
    )

    records = []

    for peer_group, group in merged.groupby(
        "peer_group"
    ):

        for metric in PEER_METRICS:

            if metric not in group.columns:
                continue

            values = pd.to_numeric(
                group[metric],
                errors="coerce",
            )

            inverse = metric == "debt_to_equity"

            ranks = (
                values.rank(
                    pct=True,
                    method="average",
                ) * 100
            )

            if inverse:
                ranks = 100 - ranks

            temp = pd.DataFrame({
                "company_id":
                    group["company_id"],
                "peer_group":
                    peer_group,
                "metric":
                    metric,
                "value":
                    values,
                "percentile":
                    ranks,
            })

            records.append(temp)

    if not records:
        result = pd.DataFrame(
            columns=[
                "company_id",
                "peer_group",
                "metric",
                "value",
                "percentile",
            ]
        )
    else:
        result = pd.concat(
            records,
            ignore_index=True,
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_csv(
        OUTPUT_DIR / "peer_percentiles.csv",
        index=False,
    )

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS peer_percentiles (
                company_id TEXT,
                peer_group TEXT,
                metric TEXT,
                value REAL,
                percentile REAL
            )
            """
        )

        conn.execute(
            "DELETE FROM peer_percentiles"
        )

        result.to_sql(
            "peer_percentiles",
            conn,
            if_exists="append",
            index=False,
        )

        conn.commit()

    print(
        f"Peer percentiles created: "
        f"{len(result)} rows"
    )


if __name__ == "__main__":
    build_peer_percentiles()
