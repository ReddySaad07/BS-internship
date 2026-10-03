from pathlib import Path
import sqlite3
import numpy as np
import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "db" / "nifty100.db"
CONFIG_PATH = ROOT / "config" / "screener_config.yaml"
OUTPUT_DIR = ROOT / "output"


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_ratios():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(
            """
            SELECT *
            FROM financial_ratios
            """,
            conn,
        )


def winsorize(series, lower=0.10, upper=0.90):
    series = pd.to_numeric(series, errors="coerce")

    if series.dropna().empty:
        return series

    low = series.quantile(lower)
    high = series.quantile(upper)

    return series.clip(low, high)


def percentile_score(series, inverse=False):
    values = pd.to_numeric(series, errors="coerce")

    result = values.rank(
        pct=True,
        method="average",
    ) * 100

    if inverse:
        result = 100 - result

    return result


def latest_company_data(df):
    """Keep the latest available year for each company."""
    df = df.copy()

    df["year"] = pd.to_numeric(
        df["year"],
        errors="coerce",
    )

    return (
        df.sort_values(
            ["company_id", "year"]
        )
        .drop_duplicates(
            "company_id",
            keep="last",
        )
    )


def build_scores(df):
    """Build a transparent 0-100 composite score."""
    df = df.copy()

    metrics = {
        "roe": False,
        "roce": False,
        "net_profit_margin": False,
        "revenue_cagr_5y": False,
        "fcf_cagr_5y": False,
        "debt_to_equity": True,
        "interest_coverage": False,
        "asset_turnover": False,
        "fcf_conversion_pct": False,
        "operating_profit_margin": False,
    }

    score_columns = []

    for metric, inverse in metrics.items():

        if metric not in df.columns:
            continue

        values = winsorize(df[metric])

        column = f"{metric}_score"

        df[column] = percentile_score(
            values,
            inverse=inverse,
        )

        score_columns.append(column)

    if score_columns:
        df["composite_score"] = (
            df[score_columns]
            .mean(axis=1, skipna=True)
        )
    else:
        df["composite_score"] = np.nan

    df["composite_score"] = (
        df["composite_score"]
        .clip(0, 100)
    )

    return df


def apply_preset(df, preset):
    """Apply a transparent screener preset."""
    preset = preset.lower()

    conditions = {
        "quality": (
            (df["roe"] >= 15)
            & (df["roce"] >= 15)
            & (df["debt_to_equity"] <= 1.0)
        ),
        "growth": (
            (df["revenue_cagr_5y"] >= 10)
            & (df["operating_profit_margin"] >= 10)
        ),
        "value": (
            (df["composite_score"] >= 40)
            & (df["debt_to_equity"] <= 1.5)
        ),
        "dividend": (
            df["composite_score"] >= 50
        ),
        "low_debt": (
            df["debt_to_equity"] <= 0.5
        ),
        "balanced": (
            (df["composite_score"] >= 50)
            & (df["roe"] >= 10)
            & (df["debt_to_equity"] <= 1.5)
        ),
    }

    if preset not in conditions:
        raise ValueError(
            f"Unknown preset: {preset}"
        )

    return df.loc[
        conditions[preset]
    ].copy()


def build_screener():
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    config = load_config()

    df = load_ratios()

    if df.empty:
        raise RuntimeError(
            "financial_ratios is empty. "
            "Run the ETL and ratio pipeline first."
        )

    df = latest_company_data(df)

    df = build_scores(df)

    presets = [
        "quality",
        "growth",
        "value",
        "dividend",
        "low_debt",
        "balanced",
    ]

    preset_frames = {}

    for preset in presets:
        preset_frames[preset] = apply_preset(
            df,
            preset,
        )

    output_xlsx = (
        OUTPUT_DIR / "screener_output.xlsx"
    )

    with pd.ExcelWriter(
        output_xlsx,
        engine="openpyxl",
    ) as writer:

        df.to_excel(
            writer,
            sheet_name="All Companies",
            index=False,
        )

        for preset, frame in preset_frames.items():
            frame.to_excel(
                writer,
                sheet_name=preset[:31],
                index=False,
            )

    config_path = (
        OUTPUT_DIR / "screener_results.csv"
    )

    df.to_csv(
        config_path,
        index=False,
    )

    print(
        f"Screener created: {output_xlsx}"
    )

    for preset, frame in preset_frames.items():
        print(
            f"{preset}: {len(frame)} companies"
        )


if __name__ == "__main__":
    build_screener()
