import os
import sys
import pandas as pd
from dotenv import load_dotenv
from google import genai

# Load environment variables from .env if present
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    print("=" * 60)
    print("Error: GEMINI_API_KEY environment variable not found.")
    print("Set it in your terminal:")
    print("   $env:GEMINI_API_KEY=\"your_api_key_here\"")
    print("Or add it to a local .env file inside this directory.")
    print("=" * 60)
    sys.exit(1)


def compute_kpi_drift(baseline_path: str, current_path: str, dimensions: list, metric: str) -> dict:
    """
    Deterministically computes baseline vs current metric variance
    and decomposes delta contribution across cohort dimensions.
    """
    df_base = pd.read_csv(baseline_path)
    df_curr = pd.read_csv(current_path)

    base_total = float(df_base[metric].sum())
    curr_total = float(df_curr[metric].sum())
    total_delta = curr_total - base_total
    pct_change = (total_delta / base_total * 100) if base_total != 0 else 0.0

    # Group by dimensions
    group_base = df_base.groupby(dimensions, as_index=False)[metric].sum()
    group_curr = df_curr.groupby(dimensions, as_index=False)[metric].sum()

    merged = pd.merge(
        group_base,
        group_curr,
        on=dimensions,
        suffixes=("_baseline", "_current"),
        how="outer"
    ).fillna(0)

    merged["delta"] = merged[f"{metric}_current"] - merged[f"{metric}_baseline"]
    denom = abs(total_delta) if total_delta != 0 else 1.0
    merged["pct_contribution_to_delta"] = ((merged["delta"] / denom) * 100).round(2)

    # Sort cohorts by largest drop
    sorted_df = merged.sort_values(by="delta", ascending=True)

    return {
        "metric": metric,
        "baseline_total": base_total,
        "current_total": curr_total,
        "absolute_delta": total_delta,
        "percentage_change": round(pct_change, 2),
        "primary_negative_drivers": sorted_df.head(3).to_dict(orient="records"),
        "top_positive_drivers": sorted_df.tail(3).sort_values(by="delta", ascending=False).to_dict(orient="records")
    }


def run_rca_agent(stats: dict) -> str:
    """
    Sends deterministic math facts to Gemini 2.5 Flash for root-cause diagnosis.
    """
    client = genai.Client(api_key=API_KEY)

    prompt = f"""
You are an expert Analytics RCA & Diagnostics Agent.
Review the following deterministic mathematical decomposition of a metric variance:

Metric: {stats['metric']}
Baseline: {stats['baseline_total']} -> Current: {stats['current_total']}
Overall Change: {stats['absolute_delta']} ({stats['percentage_change']}%)

Primary Negative Drivers (Largest Drop Cohorts):
{stats['primary_negative_drivers']}

Top Positive Drivers:
{stats['top_positive_drivers']}

Generate an executive root cause diagnosis formatted in clean Markdown with:
1. **Executive Summary**: 2 clear sentences describing the business impact.
2. **Primary Anomaly Cohort**: Specify the exact dimension combination driving the drop and its percentage contribution.
3. **Plausible Technical & Business Hypotheses**: 3 realistic hypotheses for why this specific cohort dropped (e.g., checkout/tracking bug, ad campaign fatigue, localized payment gateway issue).
4. **Targeted Triage Queries**: 2-3 specific SQL checks or log inspection actions for the analytics engineer to run next.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )
    return response.text


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    baseline_csv = os.path.join(base_dir, "data", "baseline.csv")
    current_csv = os.path.join(base_dir, "data", "current.csv")

    dimensions = ["country", "device", "channel"]
    metric = "conversions"

    print("=" * 65)
    print("STEP 1: Computing Deterministic Cohort Decomposition...")
    print("=" * 65)

    stats = compute_kpi_drift(baseline_csv, current_csv, dimensions, metric)
    print(f"Target Metric : {stats['metric']}")
    print(f"Variance      : {stats['baseline_total']} -> {stats['current_total']} ({stats['percentage_change']}%)")
    top_drag = stats['primary_negative_drivers'][0]
    print(f"Top Culprit   : {top_drag['country']} / {top_drag['device']} / {top_drag['channel']} (Delta: {top_drag['delta']})")

    print("\n" + "=" * 65)
    print("STEP 2: Calling Gemini 2.5 Flash for Root Cause Diagnosis...")
    print("=" * 65 + "\n")

    report = run_rca_agent(stats)
    print(report)


if __name__ == "__main__":
    main()