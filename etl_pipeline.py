"""
etl_pipeline.py
Bluestock MF Capstone — D1 Deliverable
ETL: Load raw CSVs → Clean → Save processed → Load into SQLite
Run: python scripts/etl_pipeline.py
"""

import os
import sys
import logging
import pandas as pd
import numpy as np
from pathlib import Path
from sqlalchemy import create_engine, text

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).resolve().parent.parent
RAW_DIR    = BASE_DIR / "data" / "raw"
PROC_DIR   = BASE_DIR / "data" / "processed"
DB_DIR     = BASE_DIR / "data" / "db"
DB_PATH    = DB_DIR / "bluestock_mf.db"

PROC_DIR.mkdir(parents=True, exist_ok=True)
DB_DIR.mkdir(parents=True, exist_ok=True)

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
log = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════════════════════
# 1. LOAD RAW
# ══════════════════════════════════════════════════════════════════════════════

def load_raw() -> dict:
    """Load all 10 raw CSVs and log shape / dtypes."""
    files = {
        "fund_master":        "01_fund_master.csv",
        "nav_history":        "02_nav_history.csv",
        "aum_by_fund_house":  "03_aum_by_fund_house.csv",
        "monthly_sip":        "04_monthly_sip_inflows.csv",
        "category_inflows":   "05_category_inflows.csv",
        "folio_count":        "06_industry_folio_count.csv",
        "scheme_performance": "07_scheme_performance.csv",
        "investor_txns":      "08_investor_transactions.csv",
        "portfolio_holdings": "09_portfolio_holdings.csv",
        "benchmark_indices":  "10_benchmark_indices.csv",
    }
    dfs = {}
    for key, fname in files.items():
        path = RAW_DIR / fname
        if not path.exists():
            log.error(f"Missing file: {path}")
            continue
        df = pd.read_csv(path, low_memory=False)
        log.info(f"Loaded {fname}: {df.shape[0]:,} rows × {df.shape[1]} cols")
        dfs[key] = df
    return dfs

# ══════════════════════════════════════════════════════════════════════════════
# 2. CLEAN
# ══════════════════════════════════════════════════════════════════════════════

def clean_fund_master(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["launch_date"] = pd.to_datetime(df["launch_date"], errors="coerce")
    df["expense_ratio_pct"] = pd.to_numeric(df["expense_ratio_pct"], errors="coerce")
    df["exit_load_pct"]     = pd.to_numeric(df["exit_load_pct"], errors="coerce")
    df = df.drop_duplicates(subset=["amfi_code"])
    anomalies = df[df["expense_ratio_pct"] > 2.5]
    if not anomalies.empty:
        log.warning(f"Expense ratio > 2.5% in {len(anomalies)} schemes — flagged")
    log.info(f"fund_master cleaned: {df.shape}")
    return df


def clean_nav_history(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["nav"]  = pd.to_numeric(df["nav"], errors="coerce")
    df = df.dropna(subset=["date", "nav"])
    df = df[df["nav"] > 0]
    df = df.sort_values(["amfi_code", "date"]).drop_duplicates(subset=["amfi_code", "date"])

    # Forward-fill weekends / holidays per fund
    all_dates = pd.date_range(df["date"].min(), df["date"].max(), freq="D")
    codes = df["amfi_code"].unique()
    chunks = []
    for code in codes:
        sub = df[df["amfi_code"] == code].set_index("date")["nav"]
        sub = sub.reindex(all_dates).ffill().reset_index()
        sub.columns = ["date", "nav"]
        sub["amfi_code"] = code
        chunks.append(sub)
    df = pd.concat(chunks, ignore_index=True)[["amfi_code", "date", "nav"]]
    df = df.dropna(subset=["nav"])
    log.info(f"nav_history cleaned (with ffill): {df.shape}")
    return df


def clean_investor_txns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
    df["amount_inr"] = pd.to_numeric(df["amount_inr"], errors="coerce")
    df = df[df["amount_inr"] > 0]
    df["transaction_type"] = df["transaction_type"].str.strip().str.title()
    valid_types = {"Sip", "Lumpsum", "Redemption"}
    bad = ~df["transaction_type"].isin(valid_types)
    if bad.any():
        log.warning(f"{bad.sum()} rows with unexpected transaction_type — kept as-is")
    df["kyc_status"] = df["kyc_status"].str.strip().str.title()
    df = df.drop_duplicates()
    log.info(f"investor_txns cleaned: {df.shape}")
    return df


def clean_scheme_performance(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    numeric_cols = ["return_1yr_pct","return_3yr_pct","return_5yr_pct",
                    "alpha","beta","sharpe_ratio","sortino_ratio",
                    "std_dev_ann_pct","max_drawdown_pct","aum_crore",
                    "expense_ratio_pct","morningstar_rating"]
    for c in numeric_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    anomalies = df[df["expense_ratio_pct"] > 2.5]
    if not anomalies.empty:
        log.warning(f"Expense ratio anomalies: {len(anomalies)} schemes")
    log.info(f"scheme_performance cleaned: {df.shape}")
    return df


def clean_generic_date(df: pd.DataFrame, date_col: str) -> pd.DataFrame:
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df = df.sort_values(date_col).reset_index(drop=True)
    return df


def clean_all(dfs: dict) -> dict:
    cleaned = {}
    cleaned["fund_master"]        = clean_fund_master(dfs["fund_master"])
    cleaned["nav_history"]        = clean_nav_history(dfs["nav_history"])
    cleaned["aum_by_fund_house"]  = clean_generic_date(dfs["aum_by_fund_house"], "date")
    cleaned["monthly_sip"]        = clean_generic_date(dfs["monthly_sip"], "month")
    cleaned["category_inflows"]   = clean_generic_date(dfs["category_inflows"], "month")
    cleaned["folio_count"]        = clean_generic_date(dfs["folio_count"], "month")
    cleaned["scheme_performance"] = clean_scheme_performance(dfs["scheme_performance"])
    cleaned["investor_txns"]      = clean_investor_txns(dfs["investor_txns"])
    cleaned["portfolio_holdings"] = dfs["portfolio_holdings"].copy()
    cleaned["benchmark_indices"]  = clean_generic_date(dfs["benchmark_indices"], "date")
    return cleaned

# ══════════════════════════════════════════════════════════════════════════════
# 3. SAVE PROCESSED CSVs
# ══════════════════════════════════════════════════════════════════════════════

def save_processed(cleaned: dict):
    name_map = {
        "fund_master":        "01_fund_master_clean.csv",
        "nav_history":        "02_nav_history_clean.csv",
        "aum_by_fund_house":  "03_aum_by_fund_house_clean.csv",
        "monthly_sip":        "04_monthly_sip_clean.csv",
        "category_inflows":   "05_category_inflows_clean.csv",
        "folio_count":        "06_folio_count_clean.csv",
        "scheme_performance": "07_scheme_performance_clean.csv",
        "investor_txns":      "08_investor_txns_clean.csv",
        "portfolio_holdings": "09_portfolio_holdings_clean.csv",
        "benchmark_indices":  "10_benchmark_indices_clean.csv",
    }
    for key, fname in name_map.items():
        path = PROC_DIR / fname
        cleaned[key].to_csv(path, index=False)
        log.info(f"Saved: {path.name}")

# ══════════════════════════════════════════════════════════════════════════════
# 4. LOAD INTO SQLITE
# ══════════════════════════════════════════════════════════════════════════════

def load_to_sqlite(cleaned: dict):
    engine = create_engine(f"sqlite:///{DB_PATH}")
    table_map = {
        "fund_master":        "dim_fund",
        "nav_history":        "fact_nav",
        "aum_by_fund_house":  "fact_aum",
        "monthly_sip":        "fact_sip_inflows",
        "category_inflows":   "fact_category_inflows",
        "folio_count":        "fact_folio_count",
        "scheme_performance": "fact_performance",
        "investor_txns":      "fact_transactions",
        "portfolio_holdings": "fact_portfolio_holdings",
        "benchmark_indices":  "fact_benchmark",
    }
    with engine.connect() as conn:
        for key, tbl in table_map.items():
            df = cleaned[key].copy()
            # Convert datetime cols to string for SQLite compatibility
            for col in df.select_dtypes(include=["datetime64[ns]","datetime64[ns, UTC]"]).columns:
                df[col] = df[col].astype(str)
            df.to_sql(tbl, conn, if_exists="replace", index=False)
            result = conn.execute(text(f"SELECT COUNT(*) FROM {tbl}")).fetchone()
            log.info(f"  {tbl}: {result[0]:,} rows loaded")
    log.info(f"SQLite DB saved to: {DB_PATH}")

# ══════════════════════════════════════════════════════════════════════════════
# 5. DATA QUALITY SUMMARY
# ══════════════════════════════════════════════════════════════════════════════

def data_quality_check(raw: dict, cleaned: dict):
    print("\n" + "="*60)
    print("DATA QUALITY SUMMARY")
    print("="*60)
    for key in raw:
        r, c = raw[key], cleaned[key]
        nulls = c.isnull().sum().sum()
        print(f"\n{key}:")
        print(f"  Raw rows: {len(r):,}  →  Cleaned rows: {len(c):,}")
        print(f"  Null values remaining: {nulls}")
    # Validate AMFI code coverage
    nav_codes  = set(cleaned["nav_history"]["amfi_code"].unique())
    fund_codes = set(cleaned["fund_master"]["amfi_code"].unique())
    missing = fund_codes - nav_codes
    extra   = nav_codes - fund_codes
    print(f"\nAMFI code check:")
    print(f"  fund_master codes: {len(fund_codes)}")
    print(f"  nav_history codes: {len(nav_codes)}")
    print(f"  In fund_master but NOT in nav_history: {missing or 'None'}")
    print(f"  In nav_history but NOT in fund_master: {len(extra)} extra codes (transaction schemes)")
    print("="*60 + "\n")

# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    log.info("── STEP 1: Loading raw CSVs ──")
    raw = load_raw()

    log.info("── STEP 2: Cleaning data ──")
    cleaned = clean_all(raw)

    log.info("── STEP 3: Saving processed CSVs ──")
    save_processed(cleaned)

    log.info("── STEP 4: Loading into SQLite ──")
    load_to_sqlite(cleaned)

    log.info("── STEP 5: Data quality check ──")
    data_quality_check(raw, cleaned)

    log.info("ETL pipeline complete ✓")


if __name__ == "__main__":
    main()
