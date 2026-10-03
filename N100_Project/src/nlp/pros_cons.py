from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "output"


def load_pros_cons():
    path = OUTPUT_DIR / "pros_cons.csv"

    if not path.exists():
        return pd.DataFrame(
            columns=[
                "company_id",
                "pros",
                "cons",
            ]
        )

    return pd.read_csv(path)


def get_company_pros_cons(company_id):
    df = load_pros_cons()

    if df.empty:
        return {
            "pros": [],
            "cons": [],
        }

    match = df.loc[
        df["company_id"].astype(str).str.upper()
        == str(company_id).upper()
    ]

    if match.empty:
        return {
            "pros": [],
            "cons": [],
        }

    row = match.iloc[0]

    return {
        "pros": str(row["pros"]).split(" | "),
        "cons": str(row["cons"]).split(" | "),
    }
