"""
recommender.py
Bluestock MF Capstone — D6 Deliverable
Simple fund recommender: input risk appetite → top 3 funds by Sharpe ratio.
Run: python scripts/recommender.py
"""

import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROC_DIR = BASE_DIR / "data" / "processed"


RISK_MAP = {
    "low":      ["Low"],
    "moderate": ["Moderate"],
    "high":     ["High", "Very High"],
}


def load_performance() -> pd.DataFrame:
    path = PROC_DIR / "07_scheme_performance_clean.csv"
    df = pd.read_csv(path)
    return df


def recommend(risk_appetite: str, top_n: int = 3) -> pd.DataFrame:
    """
    Returns top N funds matching risk appetite, ranked by Sharpe ratio.

    Parameters
    ----------
    risk_appetite : str  — 'low', 'moderate', or 'high'
    top_n         : int  — number of recommendations (default 3)
    """
    risk_appetite = risk_appetite.strip().lower()
    if risk_appetite not in RISK_MAP:
        raise ValueError(f"risk_appetite must be one of: {list(RISK_MAP.keys())}")

    grades = RISK_MAP[risk_appetite]
    df = load_performance()
    filtered = df[df["risk_grade"].isin(grades)].copy()

    if filtered.empty:
        print(f"No funds found for risk grade: {grades}")
        return pd.DataFrame()

    filtered = filtered.sort_values("sharpe_ratio", ascending=False).head(top_n)

    cols = ["scheme_name", "fund_house", "category", "risk_grade",
            "sharpe_ratio", "return_3yr_pct", "expense_ratio_pct", "aum_crore"]
    available = [c for c in cols if c in filtered.columns]

    result = filtered[available].reset_index(drop=True)
    result.index += 1
    return result


def main():
    print("=" * 65)
    print("BLUESTOCK MF FUND RECOMMENDER")
    print("=" * 65)

    for risk in ["low", "moderate", "high"]:
        print(f"\nRisk Appetite: {risk.upper()}")
        print("-" * 65)
        recs = recommend(risk)
        if not recs.empty:
            print(recs.to_string())
        else:
            print("  No matching funds found.")

    print("\n" + "=" * 65)
    print("Usage: from recommender import recommend")
    print('       recommend("moderate")  # returns DataFrame')
    print("=" * 65)


if __name__ == "__main__":
    main()
