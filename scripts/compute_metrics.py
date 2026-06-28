"""
compute_metrics.py
Bluestock MF Capstone — D4 Deliverable
Computes CAGR, Sharpe, Sortino, Alpha, Beta, MaxDD, Scorecard for all 40 funds.
Run: python scripts/compute_metrics.py
"""

import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats

BASE_DIR  = Path(__file__).resolve().parent.parent
PROC_DIR  = BASE_DIR / "data" / "processed"
OUT_DIR   = BASE_DIR / "data" / "processed"

RF_ANNUAL = 0.065   # RBI repo rate proxy
TRADING_DAYS = 252


def load_data():
    nav = pd.read_csv(PROC_DIR / "02_nav_history_clean.csv", parse_dates=["date"])
    bench = pd.read_csv(PROC_DIR / "10_benchmark_indices_clean.csv", parse_dates=["date"])
    funds = pd.read_csv(PROC_DIR / "01_fund_master_clean.csv")
    perf  = pd.read_csv(PROC_DIR / "07_scheme_performance_clean.csv")
    return nav, bench, funds, perf


def compute_daily_returns(nav: pd.DataFrame) -> pd.DataFrame:
    nav = nav.sort_values(["amfi_code", "date"])
    nav["daily_return"] = nav.groupby("amfi_code")["nav"].pct_change()
    return nav


def compute_cagr(nav_df, amfi_code, years):
    sub = nav_df[nav_df["amfi_code"] == amfi_code].sort_values("date")
    if len(sub) < 2:
        return np.nan
    end_nav   = sub["nav"].iloc[-1]
    end_date  = sub["date"].iloc[-1]
    start_date = end_date - pd.DateOffset(years=years)
    sub_period = sub[sub["date"] >= start_date]
    if len(sub_period) < 10:
        return np.nan
    start_nav = sub_period["nav"].iloc[0]
    n_days    = (sub_period["date"].iloc[-1] - sub_period["date"].iloc[0]).days
    n_years   = n_days / 365.25
    if n_years <= 0 or start_nav <= 0:
        return np.nan
    return (end_nav / start_nav) ** (1 / n_years) - 1


def compute_sharpe(returns: pd.Series) -> float:
    r = returns.dropna()
    if len(r) < 30:
        return np.nan
    rf_daily = RF_ANNUAL / TRADING_DAYS
    excess   = r - rf_daily
    std      = r.std()
    return (excess.mean() / std * np.sqrt(TRADING_DAYS)) if std > 0 else np.nan


def compute_sortino(returns: pd.Series) -> float:
    r = returns.dropna()
    if len(r) < 30:
        return np.nan
    rf_daily  = RF_ANNUAL / TRADING_DAYS
    excess    = r - rf_daily
    downside  = r[r < 0].std()
    return (excess.mean() / downside * np.sqrt(TRADING_DAYS)) if downside > 0 else np.nan


def compute_max_drawdown(nav_series: pd.Series) -> float:
    roll_max = nav_series.cummax()
    dd       = nav_series / roll_max - 1
    return dd.min()


def compute_alpha_beta(fund_returns: pd.Series, bench_returns: pd.Series):
    merged = pd.concat([fund_returns, bench_returns], axis=1).dropna()
    if len(merged) < 30:
        return np.nan, np.nan
    merged.columns = ["fund", "bench"]
    slope, intercept, r, p, se = stats.linregress(merged["bench"], merged["fund"])
    alpha = intercept * TRADING_DAYS
    beta  = slope
    return alpha, beta


def build_scorecard(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    def rank_pct(s, ascending=True):
        return s.rank(ascending=ascending, pct=True)

    df["rank_3yr"]    = rank_pct(df["cagr_3yr"])
    df["rank_sharpe"] = rank_pct(df["sharpe"])
    df["rank_alpha"]  = rank_pct(df["alpha"])
    df["rank_exp"]    = rank_pct(df["expense_ratio_pct"], ascending=False)  # lower is better
    df["rank_mdd"]    = rank_pct(df["max_drawdown"], ascending=False)       # less negative is better

    df["scorecard"] = (
        0.30 * df["rank_3yr"] +
        0.25 * df["rank_sharpe"] +
        0.20 * df["rank_alpha"] +
        0.15 * df["rank_exp"] +
        0.10 * df["rank_mdd"]
    ) * 100

    return df.sort_values("scorecard", ascending=False)


def main():
    print("Loading data ...")
    nav, bench, funds, perf = load_data()

    nav_ret = compute_daily_returns(nav)
    bench_nifty = bench[bench["index_name"] == "NIFTY100"].set_index("date")["close_value"]
    bench_ret   = bench_nifty.pct_change().rename("bench_return")

    codes = nav["amfi_code"].unique()
    results = []

    for code in codes:
        sub = nav_ret[nav_ret["amfi_code"] == code].set_index("date")
        r   = sub["daily_return"].dropna()

        fund_info = funds[funds["amfi_code"] == code]
        exp_ratio = fund_info["expense_ratio_pct"].values[0] if len(fund_info) > 0 else np.nan
        scheme    = fund_info["scheme_name"].values[0] if len(fund_info) > 0 else str(code)

        alpha, beta = compute_alpha_beta(r, bench_ret)

        results.append({
            "amfi_code":        code,
            "scheme_name":      scheme,
            "expense_ratio_pct": exp_ratio,
            "cagr_1yr":         compute_cagr(nav, code, 1),
            "cagr_3yr":         compute_cagr(nav, code, 3),
            "cagr_5yr":         compute_cagr(nav, code, 5),
            "sharpe":           compute_sharpe(r),
            "sortino":          compute_sortino(r),
            "alpha":            alpha,
            "beta":             beta,
            "max_drawdown":     compute_max_drawdown(sub["nav"]),
            "volatility_ann":   r.std() * np.sqrt(TRADING_DAYS),
        })

    df = pd.DataFrame(results)
    df = build_scorecard(df)

    # Save
    df.to_csv(OUT_DIR / "fund_scorecard.csv", index=False)
    print(f"Saved fund_scorecard.csv  ({len(df)} funds)")

    ab = df[["amfi_code", "scheme_name", "alpha", "beta"]].copy()
    ab.to_csv(OUT_DIR / "alpha_beta.csv", index=False)
    print(f"Saved alpha_beta.csv")

    print("\nTop 10 funds by scorecard:")
    print(df[["scheme_name","cagr_3yr","sharpe","alpha","scorecard"]].head(10).to_string(index=False))


if __name__ == "__main__":
    main()
