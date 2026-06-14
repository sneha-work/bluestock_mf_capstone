# Data Dictionary — Bluestock MF Capstone

## Overview
All datasets cover **January 2022 – December 2025**. Units are in Indian Rupees (INR) unless stated.

---

## 01 — dim_fund (fund_master)
| Column | Type | Description |
|---|---|---|
| amfi_code | INTEGER | AMFI scheme code — unique fund identifier |
| fund_house | TEXT | Asset Management Company name |
| scheme_name | TEXT | Full SEBI registered scheme name |
| category | TEXT | SEBI category: Equity / Debt / Hybrid / Liquid / ELSS |
| sub_category | TEXT | Sub-category: Large Cap, Mid Cap, Small Cap, Flexi Cap, etc. |
| plan | TEXT | Regular or Direct |
| launch_date | DATE | Scheme inception date |
| benchmark | TEXT | Official benchmark index (e.g., NIFTY 100 TRI) |
| expense_ratio_pct | REAL | Annual Total Expense Ratio in % (valid range: 0.1–2.5) |
| exit_load_pct | REAL | Exit load % charged on early redemption |
| min_sip_amount | REAL | Minimum SIP instalment in INR |
| min_lumpsum_amount | REAL | Minimum lumpsum investment in INR |
| fund_manager | TEXT | Lead portfolio manager name |
| risk_category | TEXT | Riskometer: Low / Moderate / High / Very High |
| sebi_category_code | TEXT | SEBI internal category code |

---

## 02 — fact_nav (nav_history)
| Column | Type | Description |
|---|---|---|
| amfi_code | INTEGER | FK → dim_fund |
| date | DATE | NAV date (weekends forward-filled) |
| nav | REAL | Net Asset Value in INR per unit (must be > 0) |

---

## 03 — fact_aum (aum_by_fund_house)
| Column | Type | Description |
|---|---|---|
| date | DATE | Quarter-end date |
| fund_house | TEXT | AMC name |
| aum_lakh_crore | REAL | AUM in lakh crore INR (1 lakh crore = ₹1 trillion) |
| aum_crore | REAL | AUM in crore INR |
| num_schemes | INTEGER | Number of active schemes |

---

## 04 — fact_sip_inflows (monthly_sip_inflows)
| Column | Type | Description |
|---|---|---|
| month | DATE | Month (YYYY-MM) |
| sip_inflow_crore | REAL | Industry SIP inflow in crore INR |
| active_sip_accounts_crore | REAL | Active SIP folios in crore |
| new_sip_accounts_lakh | REAL | New SIPs registered in lakh |
| sip_aum_lakh_crore | REAL | Total SIP AUM in lakh crore INR |
| yoy_growth_pct | REAL | Year-over-year growth % (null for first 12 months) |

---

## 05 — fact_category_inflows (category_inflows)
| Column | Type | Description |
|---|---|---|
| month | DATE | Month (YYYY-MM) |
| category | TEXT | Fund category |
| net_inflow_crore | REAL | Net inflow (inflow minus redemption) in crore INR |

---

## 06 — fact_folio_count (industry_folio_count)
| Column | Type | Description |
|---|---|---|
| month | DATE | Month (YYYY-MM) |
| total_folios_crore | REAL | Total investor accounts in crore |
| equity_folios_crore | REAL | Equity fund accounts in crore |
| debt_folios_crore | REAL | Debt fund accounts in crore |
| hybrid_folios_crore | REAL | Hybrid fund accounts in crore |
| others_folios_crore | REAL | Other category accounts in crore |

---

## 07 — fact_performance (scheme_performance)
| Column | Type | Description |
|---|---|---|
| amfi_code | INTEGER | FK → dim_fund |
| return_1yr_pct | REAL | 1-year trailing return % |
| return_3yr_pct | REAL | 3-year CAGR % |
| return_5yr_pct | REAL | 5-year CAGR % |
| benchmark_3yr_pct | REAL | Benchmark 3-year CAGR % |
| alpha | REAL | Annualised alpha vs benchmark |
| beta | REAL | Beta vs benchmark |
| sharpe_ratio | REAL | Sharpe ratio (Rf = 6.5%) |
| sortino_ratio | REAL | Sortino ratio (downside deviation) |
| std_dev_ann_pct | REAL | Annualised standard deviation % |
| max_drawdown_pct | REAL | Maximum peak-to-trough drawdown % |
| aum_crore | REAL | Scheme AUM in crore INR |
| expense_ratio_pct | REAL | TER % |
| morningstar_rating | INTEGER | Star rating 1–5 |
| risk_grade | TEXT | Low / Moderate / High / Very High |

---

## 08 — fact_transactions (investor_transactions)
| Column | Type | Description |
|---|---|---|
| investor_id | TEXT | Anonymised investor ID |
| transaction_date | DATE | Date of transaction |
| amfi_code | INTEGER | FK → dim_fund |
| transaction_type | TEXT | SIP / Lumpsum / Redemption |
| amount_inr | REAL | Transaction amount in INR (must be > 0) |
| state | TEXT | Investor's state |
| city | TEXT | Investor's city |
| city_tier | TEXT | T30 (top 30 cities) or B30 (beyond top 30) |
| age_group | TEXT | 18-25 / 26-35 / 36-45 / 46-55 / 56+ |
| gender | TEXT | Male / Female / Other |
| annual_income_lakh | REAL | Annual income in lakh INR |
| payment_mode | TEXT | UPI / NEFT / Cheque / etc. |
| kyc_status | TEXT | Verified / Pending |

---

## 09 — fact_portfolio_holdings (portfolio_holdings)
| Column | Type | Description |
|---|---|---|
| amfi_code | INTEGER | FK → dim_fund |
| stock_symbol | TEXT | NSE/BSE ticker symbol |
| stock_name | TEXT | Company full name |
| sector | TEXT | SEBI sector classification |
| weight_pct | REAL | Stock weight in fund portfolio % |
| market_value_cr | REAL | Market value held by fund in crore INR |
| current_price_inr | REAL | Stock price at portfolio date |
| portfolio_date | DATE | Portfolio disclosure date |

---

## 10 — fact_benchmark (benchmark_indices)
| Column | Type | Description |
|---|---|---|
| date | DATE | Trading date |
| index_name | TEXT | NIFTY50 / NIFTY100 |
| close_value | REAL | Index closing value |

---

## Derived / Processed CSVs (data/processed/)
| File | Description |
|---|---|
| 11_nav_with_returns.csv | NAV history with daily_return column added |
| 12_nifty50_returns.csv | NIFTY50 daily returns |
| 13_cohort_analysis.csv | Investor cohorts by first transaction year |
| 14_sip_continuity.csv | Per-investor SIP gap analysis |
| 15_sector_hhi.csv | Herfindahl-Hirschman Index per fund |
| fund_scorecard.csv | Composite 0-100 fund scorecard |
| alpha_beta.csv | Alpha & Beta for all 40 funds |
| var_cvar_report.csv | Historical VaR (95%) and CVaR per fund |
