"""
live_nav_fetch.py
Bluestock MF Capstone — D1 Deliverable
Fetches live NAV from mfapi.in for 5 key schemes and saves as CSV.
Run: python scripts/live_nav_fetch.py
"""

import requests
import pandas as pd
import logging
import sys
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR  = BASE_DIR / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
log = logging.getLogger(__name__)

SCHEMES = {
    119551: "SBI Bluechip Fund - Direct Plan",
    120503: "ICICI Pru Bluechip Fund - Direct Plan",
    118632: "Nippon India Large Cap Fund - Direct Plan",
    119092: "Axis Bluechip Fund - Direct Plan",
    120841: "Kotak Bluechip Fund - Direct Plan",
}

BASE_URL = "https://api.mfapi.in/mf/{}"


def fetch_nav(amfi_code: int, scheme_name: str) -> pd.DataFrame:
    """Fetch full NAV history for one scheme from mfapi.in."""
    url = BASE_URL.format(amfi_code)
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        records = data.get("data", [])
        df = pd.DataFrame(records)
        df["amfi_code"]   = amfi_code
        df["scheme_name"] = scheme_name
        df.rename(columns={"date": "nav_date", "nav": "nav_value"}, inplace=True)
        df["nav_date"] = pd.to_datetime(df["nav_date"], format="%d-%m-%Y", errors="coerce")
        df["nav_value"] = pd.to_numeric(df["nav_value"], errors="coerce")
        df = df.dropna(subset=["nav_date", "nav_value"])
        df = df.sort_values("nav_date").reset_index(drop=True)
        log.info(f"  {scheme_name} ({amfi_code}): {len(df)} records fetched")
        return df
    except requests.exceptions.ConnectionError:
        log.warning(f"  {scheme_name}: Network unavailable — skipping live fetch")
        return pd.DataFrame()
    except Exception as e:
        log.error(f"  {scheme_name} ({amfi_code}): Failed — {e}")
        return pd.DataFrame()


def main():
    log.info("Fetching live NAV data from mfapi.in ...")
    all_dfs = []
    for code, name in SCHEMES.items():
        df = fetch_nav(code, name)
        if not df.empty:
            all_dfs.append(df)

    if all_dfs:
        combined = pd.concat(all_dfs, ignore_index=True)
        out_path = RAW_DIR / "live_nav_5schemes.csv"
        combined.to_csv(out_path, index=False)
        log.info(f"Saved: {out_path}  ({len(combined):,} total rows)")
    else:
        log.warning("No data fetched. Check network connectivity.")

    log.info("Live NAV fetch complete ✓")


if __name__ == "__main__":
    main()
