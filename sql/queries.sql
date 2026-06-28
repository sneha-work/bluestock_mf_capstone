-- queries.sql
-- Bluestock MF Capstone — D2 Deliverable
-- 10 Analytical SQL Queries
-- Run against: data/db/bluestock_mf.db

-- Q1: Top 5 fund houses by AUM (latest quarter)
SELECT fund_house,
       ROUND(aum_lakh_crore, 2) AS aum_lakh_crore,
       ROUND(aum_crore, 0)      AS aum_crore
FROM   fact_aum
WHERE  date = (SELECT MAX(date) FROM fact_aum)
ORDER  BY aum_crore DESC
LIMIT  5;

-- Q2: Average NAV per month for top fund (SBI Bluechip - Direct)
SELECT SUBSTR(date, 1, 7)    AS month,
       ROUND(AVG(nav), 4)    AS avg_nav,
       ROUND(MIN(nav), 4)    AS min_nav,
       ROUND(MAX(nav), 4)    AS max_nav
FROM   fact_nav
WHERE  amfi_code = 119552
GROUP  BY month
ORDER  BY month DESC
LIMIT  24;

-- Q3: SIP inflow year-on-year growth
SELECT SUBSTR(month, 1, 4)          AS year,
       ROUND(SUM(sip_inflow_crore))  AS total_sip_crore,
       ROUND(AVG(yoy_growth_pct), 2) AS avg_yoy_growth_pct
FROM   fact_sip_inflows
GROUP  BY year
ORDER  BY year;

-- Q4: Transaction volume by state (top 10)
SELECT state,
       COUNT(*)                        AS num_transactions,
       ROUND(SUM(amount_inr) / 1e7, 2) AS total_amount_crore
FROM   fact_transactions
GROUP  BY state
ORDER  BY total_amount_crore DESC
LIMIT  10;

-- Q5: Funds with expense ratio < 1% (direct plans, low cost)
SELECT f.scheme_name,
       f.fund_house,
       f.category,
       f.expense_ratio_pct
FROM   dim_fund f
WHERE  f.expense_ratio_pct < 1.0
ORDER  BY f.expense_ratio_pct ASC;

-- Q6: Top 5 funds by 3-year return
SELECT scheme_name,
       fund_house,
       category,
       ROUND(return_3yr_pct, 2) AS return_3yr_pct,
       ROUND(sharpe_ratio, 3)   AS sharpe_ratio
FROM   fact_performance
ORDER  BY return_3yr_pct DESC
LIMIT  5;

-- Q7: SIP vs Lumpsum vs Redemption split (count and amount)
SELECT transaction_type,
       COUNT(*)                        AS num_transactions,
       ROUND(SUM(amount_inr) / 1e7, 2) AS total_amount_crore,
       ROUND(AVG(amount_inr), 0)        AS avg_amount_inr
FROM   fact_transactions
GROUP  BY transaction_type;

-- Q8: Folio count growth year-end snapshot
SELECT month,
       ROUND(total_folios_crore, 2)  AS total_folios_crore,
       ROUND(equity_folios_crore, 2) AS equity_folios_crore
FROM   fact_folio_count
ORDER  BY month;

-- Q9: Top 5 sectors by portfolio weight across all equity funds
SELECT ph.sector,
       ROUND(AVG(ph.weight_pct), 2) AS avg_weight_pct,
       COUNT(DISTINCT ph.amfi_code) AS num_funds_holding
FROM   fact_portfolio_holdings ph
JOIN   dim_fund f ON f.amfi_code = ph.amfi_code
WHERE  f.category IN ('Equity', 'Large Cap', 'Mid Cap', 'Small Cap', 'Flexi Cap', 'ELSS')
GROUP  BY ph.sector
ORDER  BY avg_weight_pct DESC
LIMIT  5;

-- Q10: Investor age group vs average SIP amount
SELECT age_group,
       COUNT(*)                    AS num_sip_txns,
       ROUND(AVG(amount_inr), 0)  AS avg_sip_amount_inr,
       ROUND(SUM(amount_inr)/1e7) AS total_crore
FROM   fact_transactions
WHERE  transaction_type = 'Sip'
GROUP  BY age_group
ORDER  BY avg_sip_amount_inr DESC;
