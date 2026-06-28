-- schema.sql
-- Bluestock MF Capstone
-- Auto-generated from bluestock_mf.db

CREATE TABLE dim_fund (
	amfi_code BIGINT, 
	fund_house TEXT, 
	scheme_name TEXT, 
	category TEXT, 
	sub_category TEXT, 
	"plan" TEXT, 
	launch_date TEXT, 
	benchmark TEXT, 
	expense_ratio_pct FLOAT, 
	exit_load_pct FLOAT, 
	min_sip_amount BIGINT, 
	min_lumpsum_amount BIGINT, 
	fund_manager TEXT, 
	risk_category TEXT, 
	sebi_category_code TEXT
);

CREATE TABLE fact_nav (
	amfi_code BIGINT, 
	date TEXT, 
	nav FLOAT
);

