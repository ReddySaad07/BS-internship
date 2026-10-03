"""
Live NAV data fetcher for selected mutual fund schemes.

Fetches NAV history from the MFAPI service, enriches the response
with scheme metadata, and saves individual and combined CSV files.
"""

from datetime import datetime
from pathlib import Path
import time

import pandas as pd
import requests


RAW_PATH = Path("data/raw")
BASE_URL = "https://api.mfapi.in/mf/"

SCHEMES = {
    "HDFC_Top100_Direct": 125497,
    "SBI_Bluechip": 119551,
    "ICICI_Bluechip": 120503,
    "Nippon_LargeCap": 118632,
    "Axis_Bluechip": 119092,
    "Kotak_Bluechip": 120841,
}


def fetch_nav(
    scheme_name: str,
    scheme_code: int,
    output_path: Path = RAW_PATH,
) -> pd.DataFrame | None:
    """Fetch NAV history for one mutual fund scheme.

    Parameters
    ----------
    scheme_name : str
        Local name used for the output file.
    scheme_code : int
        MFAPI scheme identifier.
    output_path : Path
        Directory where the CSV file is saved.

    Returns
    -------
    pandas.DataFrame or None
        NAV data when the request succeeds; otherwise None.
    """
    output_path.mkdir(parents=True, exist_ok=True)
    url = f"{BASE_URL}{scheme_code}"

    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()

        payload = response.json()
        metadata = payload.get("meta", {})
        nav_data = payload.get("data", [])

        if not nav_data:
            return None

        df = pd.DataFrame(nav_data)
        df["scheme_code"] = scheme_code
        df["scheme_name"] = metadata.get("scheme_name", scheme_name)
        df["fund_house"] = metadata.get("fund_house", "N/A")
        df["fetched_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        df["nav"] = pd.to_numeric(df["nav"], errors="coerce")

        filename = output_path / f"nav_{scheme_name}.csv"
        df.to_csv(filename, index=False)

        return df

    except (requests.RequestException, ValueError, KeyError):
        return None


def main() -> None:
    """Fetch NAV data for all configured schemes."""
    RAW_PATH.mkdir(parents=True, exist_ok=True)

    all_dfs = []

    for scheme_name, scheme_code in SCHEMES.items():
        df = fetch_nav(scheme_name, scheme_code)

        if df is not None:
            all_dfs.append(df)

        time.sleep(0.5)

    if all_dfs:
        master = pd.concat(all_dfs, ignore_index=True)
        master.to_csv(
            RAW_PATH / "nav_all_schemes_combined.csv",
            index=False,
        )


if __name__ == "__main__":
    main()
