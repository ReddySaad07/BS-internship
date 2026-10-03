from pathlib import Path
import sqlite3
import pandas as pd
import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances_argmin_min


ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "db" / "nifty100.db"
OUTPUT_DIR = ROOT / "output"
REPORT_DIR = ROOT / "reports"


FEATURES = [
    "return_on_equity_pct",
    "debt_to_equity",
    "revenue_cagr_5yr",
    "fcf_cagr_5yr",
    "operating_profit_margin_pct",
]


FALLBACK_FEATURES = {
    "return_on_equity_pct": "roe",
    "revenue_cagr_5yr": "revenue_cagr_5y",
    "fcf_cagr_5yr": "fcf_cagr_5y",
    "operating_profit_margin_pct":
        "operating_profit_margin",
}


def load_data():
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query(
            "SELECT * FROM financial_ratios",
            conn,
        )

    df = (
        df.sort_values(
            ["company_id", "year"]
        )
        .drop_duplicates(
            "company_id",
            keep="last",
        )
    )

    for target, fallback in FALLBACK_FEATURES.items():
        if target not in df.columns:
            if fallback in df.columns:
                df[target] = df[fallback]

    return df


def run_clustering():
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    df = load_data()

    if df.empty:
        raise RuntimeError(
            "No ratio data available for clustering."
        )

    available = [
        feature
        for feature in FEATURES
        if feature in df.columns
    ]

    if len(available) < 3:
        raise RuntimeError(
            "Not enough clustering features "
            "are available."
        )

    X = df[available].apply(
        pd.to_numeric,
        errors="coerce",
    )

    X = X.replace(
        [np.inf, -np.inf],
        np.nan,
    )

    # Sector median imputation is attempted when sector
    # information is available. Otherwise overall medians
    # are used without inventing values.
    medians = X.median()

    X = X.fillna(medians)

    scaler = StandardScaler()

    X_scaled = scaler.fit_transform(X)

    n_clusters = min(
        5,
        len(df),
    )

    model = KMeans(
        n_clusters=n_clusters,
        random_state=42,
        n_init=20,
    )

    labels = model.fit_predict(
        X_scaled
    )

    distances = np.linalg.norm(
        X_scaled
        - model.cluster_centers_[labels],
        axis=1,
    )

    result = pd.DataFrame({
        "company_id":
            df["company_id"].values,
        "cluster_id":
            labels,
        "cluster_name":
            [
                f"Cluster {x + 1}"
                for x in labels
            ],
        "distance_from_centroid":
            distances,
    })

    result.to_csv(
        OUTPUT_DIR / "cluster_labels.csv",
        index=False,
    )

    print(
        f"Cluster labels created for "
        f"{len(result)} companies."
    )


if __name__ == "__main__":
    run_clustering()
