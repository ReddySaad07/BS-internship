cat << 'PYEOF' > scripts/live_nav_fetch.py
"""
Day 1 - Live NAV Fetch (per official capstone brief)
Bluestock MF Analytics Capstone

Fetches live NAV from mfapi.in for:
  - HDFC Top 100        (125497)  -- primary task
  - SBI Bluechip        (119551)
  - ICICI Bluechip      (120503)
  - Nippon Large Cap    (118632)
  - Axis Bluechip       (119092)
  - Kotak Bluechip      (120841)

Saves one raw CSV per scheme into data/raw/, matching the brief's
"5 raw NAV CSV files" deliverable (+ the HDFC primary fetch).
"""

import os
import requests
import pandas as pd

OUTPUT_DIR = "data/raw"
API_URL = "https://api.mfapi.in/mf/{code}"

SCHEMES = {
    125497: "hdfc_top100_live_nav",
    119551: "sbi_bluechip_live_nav",
    120503: "icici_bluechip_live_nav",
    118632: "nippon_large_cap_live_nav",
    119092: "axis_bluechip_live_nav",
    120841: "kotak_bluechip_live_nav",
}


def fetch_scheme_nav(amfi_code: int) -> pd.DataFrame | None:
    """Return the full NAV history for a scheme as a DataFrame, or None on failure."""
    try:
        response = requests.get(API_URL.format(code=amfi_code), timeout=15)
        response.raise_for_status()
        payload = response.json()

        records = payload.get("data", [])
        if not records:
            return None

        df = pd.DataFrame(records)  # columns: date, nav
        df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y")
        df["nav"] = df["nav"].astype(float)
        df = df.sort_values("date").reset_index(drop=True)
        return df
    except (requests.RequestException, KeyError, ValueError) as exc:
        print(f"  ERROR fetching {amfi_code}: {exc}")
        return None


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for code, filename in SCHEMES.items():
        print(f"Fetching AMFI code {code} ({filename})...")
        df = fetch_scheme_nav(code)

        if df is None:
            print(f"  SKIP {code}: no data returned")
            continue

        out_path = os.path.join(OUTPUT_DIR, f"{filename}.csv")
        df.to_csv(out_path, index=False)
        print(f"  Saved {len(df)} rows -> {out_path}")

    print("\nLive NAV fetch complete.")


if __name__ == "__main__":
    main()
PYEOF
echo "live_nav_fetch.py created."