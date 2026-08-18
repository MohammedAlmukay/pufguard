"""Compare sdcMicro output with PUFGuard metrics.

Reads the CSV produced by run_sdcmicro.R and the PUFGuard pipeline output,
aligns overlapping metrics, and produces a comparison table.

Run after: Rscript run_sdcmicro.R
"""

import csv
import json
import sys
from pathlib import Path

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent


def main():
    sdc_path = SCRIPT_DIR / "sdcmicro_results.csv"
    puf_path = PROJECT_ROOT / "results" / "tables" / "dataset_privacy_profiles.csv"

    if not sdc_path.exists():
        print(f"ERROR: sdcMicro results not found at {sdc_path}")
        print("Run 'Rscript run_sdcmicro.R' first.")
        return 1

    sdc = pd.read_csv(sdc_path)
    puf = pd.read_csv(puf_path)

    print("=" * 80)
    print("sdcMicro vs PUFGuard Metric Comparison")
    print("=" * 80)

    # Find D1 in PUFGuard results
    d1_puf = puf[puf["dataset_id"] == "D1"].iloc[0]
    d1_sdc = sdc[sdc["dataset"].str.contains("D1", na=False)]

    if d1_sdc.empty:
        print("No D1 results in sdcMicro output. Only testdata comparison available.")
        d1_sdc = None
    else:
        d1_sdc = d1_sdc.iloc[0]

    print("\n--- D1 (BMI_Depression) Core QID Comparison ---")
    if d1_sdc is not None:
        comparisons = []

        # Singleton rate
        puf_sr = d1_puf["singleton_rate_core"]
        sdc_sr = d1_sdc.get("singleton_rate", None)
        if sdc_sr is not None:
            comparisons.append({
                "metric": "Singleton rate (core)",
                "pufguard": f"{puf_sr:.4f} ({puf_sr*100:.1f}%)",
                "sdcmicro": f"{sdc_sr:.4f} ({sdc_sr*100:.1f}%)",
                "abs_diff": f"{abs(puf_sr - sdc_sr):.6f}",
                "match": abs(puf_sr - sdc_sr) < 0.001,
            })

        # Below-k=5 rate
        puf_bk = d1_puf["records_below_k5_rate_core"]
        sdc_bk = d1_sdc.get("below_k5_rate", None)
        if sdc_bk is not None:
            comparisons.append({
                "metric": "Below-k=5 rate (core)",
                "pufguard": f"{puf_bk:.4f} ({puf_bk*100:.1f}%)",
                "sdcmicro": f"{sdc_bk:.4f} ({sdc_bk*100:.1f}%)",
                "abs_diff": f"{abs(puf_bk - sdc_bk):.6f}",
                "match": abs(puf_bk - sdc_bk) < 0.001,
            })

        # Min k
        puf_mk = d1_puf.get("minimum_k_extended", None)  # Use core if available
        sdc_mk = d1_sdc.get("min_k", None)

        for c in comparisons:
            status = "MATCH" if c["match"] else "DIFFER"
            print(f"  {c['metric']}: PUFGuard={c['pufguard']}, "
                  f"sdcMicro={c['sdcmicro']} [{status}]")

        # sdcMicro-specific measures (no PUFGuard equivalent)
        print("\n--- sdcMicro-specific measures (no direct PUFGuard equivalent) ---")
        if "global_risk" in d1_sdc.index:
            print(f"  Global risk (expected re-identifications): {d1_sdc['global_risk']:.4f}")
        if "global_risk_pct" in d1_sdc.index:
            print(f"  Global risk percentage: {d1_sdc['global_risk_pct']:.2f}%")
        if "records_risk_100pct" in d1_sdc.index:
            print(f"  Records at 100% individual risk: {int(d1_sdc['records_risk_100pct'])}")

        print("\n--- Semantic differences ---")
        print("  PUFGuard singleton_rate = fraction of records in k=1 equivalence classes")
        print("  sdcMicro individual risk = 1/f_k (frequency-based, unweighted)")
        print("  sdcMicro global risk = expected number of re-identifications (sum of 1/f_k)")
        print("  These are related but not identical measures.")

        # Save comparison
        comp_path = SCRIPT_DIR / "sdcmicro_comparison.json"
        with open(comp_path, "w", encoding="utf-8") as f:
            json.dump({
                "comparisons": comparisons,
                "pufguard_version": "PUFGuard pipeline",
                "sdcmicro_version": str(d1_sdc.get("sdcmicro_version", "unknown")),
                "r_version": str(d1_sdc.get("r_version", "unknown")),
            }, f, indent=2, default=str)
        print(f"\n  Results: {comp_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
