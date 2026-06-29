# Bluestock MF Capstone Project

> End-to-end Mutual Fund analytics project — ETL, EDA, Performance Metrics, Dashboard & Advanced Analytics

## Team
Sneha Thakur

---

## Project Structure

```
bluestock_mf_capstone/
├── data/
│   ├── raw/           ← original 10 CSV datasets
│   ├── processed/     ← cleaned + derived CSVs (15 files)
│   └── db/            ← bluestock_mf.db (SQLite) — NOT committed
├── scripts/
│   ├── etl_pipeline.py      ← D1: full ETL
│   ├── live_nav_fetch.py    ← D1: live NAV from mfapi.in
│   ├── compute_metrics.py   ← D4: CAGR, Sharpe, Alpha/Beta, Scorecard
│   └── recommender.py       ← D6: risk-based fund recommender
├── sql/
│   ├── schema.sql     ← D2: SQLite star schema DDL
│   └── queries.sql    ← D2: 10 analytical queries
├── notebooks/
│   ├── 01_data_ingestion.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_eda_analysis.ipynb
│   ├── 04_performance_analytics.ipynb
│   └── 05_advanced_analytics.ipynb
├── dashboard/         ← Tableau .twbx file
├── reports/           ← Final PDF report and PPTX
├── run_pipeline.py    ← Master script — runs everything
├── requirements.txt
├── data_dictionary.md
└── README.md
```

---

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/<your-team>/bluestock_mf_capstone.git
cd bluestock_mf_capstone

# 2. Install dependencies
pip install -r requirements.txt

# 3. Place raw CSVs in data/raw/
#    (01_fund_master.csv ... 10_benchmark_indices.csv)

# 4. Run the full pipeline
python run_pipeline.py
```

This will:
- Clean all 10 datasets → `data/processed/`
- Load them into SQLite → `data/db/bluestock_mf.db`
- Compute fund scorecards → `data/processed/fund_scorecard.csv`
- Compute VaR/CVaR → `data/processed/var_cvar_report.csv`

---

## Datasets

| # | File | Rows | Description |
|---|------|------|-------------|
| 01 | fund_master.csv | 40 | Fund metadata — 40 schemes across 9 AMCs |
| 02 | nav_history.csv | 46,000 | Daily NAV Jan 2022 – Dec 2025 |
| 03 | aum_by_fund_house.csv | 90 | Quarterly AUM per AMC |
| 04 | monthly_sip_inflows.csv | 48 | Industry SIP inflow monthly |
| 05 | category_inflows.csv | 144 | Net inflow by fund category |
| 06 | industry_folio_count.csv | 21 | Industry folio count milestones |
| 07 | scheme_performance.csv | 40 | Pre-computed performance metrics |
| 08 | investor_transactions.csv | 32,778 | Simulated investor transactions |
| 09 | portfolio_holdings.csv | 322 | Fund equity holdings |
| 10 | benchmark_indices.csv | 8,050 | NIFTY50 & NIFTY100 daily index values |

---

## Deliverables

| ID | Deliverable | Weight | Status |
|----|------------|--------|--------|
| D1 | ETL pipeline script | 15% | ✅ |
| D2 | SQLite database + SQL | 10% | ✅ |
| D3 | EDA notebook | 15% | ✅ |
| D4 | Performance metrics | 15% | ✅ |
| D5 | Interactive dashboard | 20% | ✅ |
| D6 | Advanced analytics | 10% | ✅ |
| D7 | Final report + slides | 15% | ✅ |

---

## Live NAV Fetch

```bash
python scripts/live_nav_fetch.py
# Fetches NAV from https://api.mfapi.in/mf/<amfi_code>
# Saves to data/raw/live_nav_5schemes.csv
```

---

## Fund Recommender

```python
from scripts.recommender import recommend
recs = recommend("moderate")   # "low" | "moderate" | "high"
print(recs)
```

---

## Tableau Dashboard
Open `dashboard/bluestock_mf.twbx` in Tableau Desktop or Tableau Public. Data source: connect to `data/processed/` CSVs.

**Live Dashboard:** https://public.tableau.com/app/profile/sneha.thakur4375/viz/tableau_mf/Dashboard1
---

## Notes
- `.db` files are excluded from Git (see `.gitignore`). Use `sql/schema.sql` to recreate the database.
- All file paths use `pathlib.Path` — no hard-coded paths.
- NAV weekends/holidays forward-filled with `ffill()`.
- CAGR uses trading days (252), not calendar days.
