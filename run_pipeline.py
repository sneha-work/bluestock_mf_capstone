"""
run_pipeline.py
Bluestock MF Capstone — Master Execution Script
Runs all pipeline steps in order.
Usage: python run_pipeline.py
"""

import subprocess
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
SCRIPTS  = BASE_DIR / "scripts"


def run(script: str, label: str):
    log.info(f"Running: {label} ...")
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / script)],
        capture_output=False
    )
    if result.returncode != 0:
        log.error(f"FAILED: {label}")
        sys.exit(1)
    log.info(f"Done: {label} ✓\n")


def main():
    log.info("=" * 55)
    log.info("BLUESTOCK MF CAPSTONE — PIPELINE START")
    log.info("=" * 55)

    run("etl_pipeline.py",    "Step 1: ETL — Load, Clean, Save, SQLite")
    run("compute_metrics.py", "Step 2: Performance Metrics — Scorecard, Alpha/Beta")
    run("recommender.py",     "Step 3: Fund Recommender — Test output")

    log.info("=" * 55)
    log.info("ALL STEPS COMPLETE ✓")
    log.info(f"Processed CSVs  → data/processed/")
    log.info(f"SQLite DB       → data/db/bluestock_mf.db")
    log.info(f"Scorecard CSV   → data/processed/fund_scorecard.csv")
    log.info(f"VaR/CVaR CSV    → data/processed/var_cvar_report.csv")
    log.info("=" * 55)


if __name__ == "__main__":
    main()
