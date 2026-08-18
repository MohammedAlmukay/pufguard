"""
ARX-equivalent risk comparison for PUFGuard.

Computes the three standard re-identification risk measures used by the ARX
Data Anonymization Tool (Prasser & Kohlmayer, 2015) from the same equivalence
classes that PUFGuard computes, and compares them side-by-side with PUFGuard's
metrics and policy decisions.

ARX risk model reference:
  El Emam, K., Dankar, F.K., et al. (2009). A globally optimal k-anonymity
  method for the de-identification of health data. JAMIA, 16(5), 670-682.

The three attacker models:
  - Prosecutor: attacker knows the target is in the dataset.
    Risk = max(1/k_i) over all equivalence classes = 1/min(k).
  - Journalist: attacker does not know whether the target is in the dataset
    but tries each record. Equivalent to prosecutor for sample-level risk.
  - Marketer: attacker tries to re-identify as many records as possible.
    Risk = (1/n) * sum(1/k_i) over all records.

All three are computed from equivalence class sizes — the same groupby output
PUFGuard already produces.
"""

import json
import sys
from pathlib import Path

import pandas as pd

# ── locate project root ──────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent

sys.path.insert(0, str(PROJECT_ROOT / "src"))
from pufguard.analyze_corpus import equivalence_metrics, normalized_frame, available  # noqa: E402


def arx_risk_measures(df: pd.DataFrame, qids: list[str]) -> dict:
    """Compute ARX-equivalent prosecutor, journalist, and marketer risk.

    Uses the same normalization as PUFGuard (case-fold, strip, round, fill NA).
    """
    qids_available = [c for c in qids if c in df.columns]
    n = len(df)
    if n == 0 or not qids_available:
        return {
            "prosecutor_risk": 0.0,
            "journalist_risk": 0.0,
            "marketer_risk": 0.0,
            "records_affected_100pct": 0,
            "avg_class_size": 0.0,
            "num_classes": 0,
        }

    # Same normalization as PUFGuard
    keys = df[qids_available].copy().fillna("<MISSING>")
    for c in qids_available:
        if pd.api.types.is_numeric_dtype(keys[c]):
            keys[c] = keys[c].round(6)
        else:
            keys[c] = keys[c].astype(str).str.strip().str.casefold()

    sizes = keys.groupby(qids_available, dropna=False).size()

    min_k = int(sizes.min())
    prosecutor_risk = 1.0 / min_k
    journalist_risk = prosecutor_risk  # same for sample-level analysis

    # Marketer risk: average over all records of 1/k_i
    # Each record in a class of size k contributes 1/k, so each class of size k
    # contributes k * (1/k) = 1. Total = num_classes / n.
    # Equivalently: sum over classes of (class_size * (1/class_size)) / n
    marketer_risk = len(sizes) / n

    # Records at 100% risk (singletons)
    records_at_full_risk = int(sizes[sizes == 1].sum())

    return {
        "prosecutor_risk": prosecutor_risk,
        "journalist_risk": journalist_risk,
        "marketer_risk": marketer_risk,
        "records_affected_100pct": records_at_full_risk,
        "avg_class_size": float(sizes.mean()),
        "num_classes": int(len(sizes)),
    }


def load_datasets(project_root: Path) -> list[dict]:
    """Load dataset configurations and data."""
    with open(project_root / "configs" / "datasets.json") as f:
        config = json.load(f)

    datasets = []
    for ds_id, ds in config.items():
        filepath = project_root / ds["file"]
        sheet = ds.get("sheet", 0)
        df = normalized_frame(pd.read_excel(filepath, sheet_name=sheet))
        # Drop all-empty rows (R7-03 fix)
        df = df.dropna(how="all").reset_index(drop=True)

        datasets.append({
            "dataset_id": ds_id,
            "short_name": ds["name"],
            "df": df,
            "core_qids": ds["core_qids"],
            "extended_qids": ds["extended_qids"],
            "primary_sensitive": ds["primary_sensitive"],
        })
    return datasets


def main():
    project_root = PROJECT_ROOT
    datasets = load_datasets(project_root)

    rows = []
    for ds in datasets:
        ds_id = ds["dataset_id"]
        name = ds["short_name"]
        df = ds["df"]
        n = len(df)

        for scenario, qids in [("core", ds["core_qids"]),
                                ("extended", ds["extended_qids"])]:
            # Validate all configured QIDs resolve after normalization
            available(list(df.columns), qids, strict=True)

            # PUFGuard metrics
            puf = equivalence_metrics(df, qids, ds["primary_sensitive"])

            # ARX-equivalent metrics
            arx = arx_risk_measures(df, qids)

            rows.append({
                "dataset_id": ds_id,
                "short_name": name,
                "scenario": scenario,
                "records": n,
                "qid_count": puf["qid_count"],
                # PUFGuard metrics
                "puf_singleton_rate": puf["singleton_rate"],
                "puf_below_k5_rate": puf["records_below_k5_rate"],
                "puf_homogeneous_rate": puf["homogeneous_sensitive_rate_non_singleton"],
                "puf_min_k": puf["minimum_k"],
                "puf_median_k": puf["median_k"],
                # ARX-equivalent metrics
                "arx_prosecutor_risk": arx["prosecutor_risk"],
                "arx_journalist_risk": arx["journalist_risk"],
                "arx_marketer_risk": arx["marketer_risk"],
                "arx_records_100pct_risk": arx["records_affected_100pct"],
                "arx_avg_class_size": arx["avg_class_size"],
                "arx_num_classes": arx["num_classes"],
            })

    results = pd.DataFrame(rows)

    # Save CSV
    out_dir = SCRIPT_DIR
    results.to_csv(out_dir / "arx_comparison_results.csv", index=False)

    # Print summary
    print("=" * 80)
    print("PUFGuard vs ARX-Equivalent Risk Comparison")
    print("=" * 80)

    for _, row in results.iterrows():
        print(f"\n{row['dataset_id']} ({row['short_name']}) — {row['scenario']} "
              f"({row['qid_count']} QIDs, {row['records']} records)")
        print(f"  PUFGuard singleton rate:    {row['puf_singleton_rate']:.4f} "
              f"({row['puf_singleton_rate']*100:.1f}%)")
        pr = row['arx_prosecutor_risk']
        pr_pct = '100%' if pr == 1.0 else f'{pr*100:.1f}%'
        print(f"  ARX prosecutor risk:        {pr:.4f} ({pr_pct})")
        print(f"  ARX marketer risk:          {row['arx_marketer_risk']:.4f} "
              f"({row['arx_marketer_risk']*100:.1f}%)")
        print(f"  PUFGuard min k:             {row['puf_min_k']}")
        print(f"  PUFGuard below-k=5 rate:    {row['puf_below_k5_rate']:.4f} "
              f"({row['puf_below_k5_rate']*100:.1f}%)")
        print(f"  PUFGuard homogeneous rate:  {row['puf_homogeneous_rate']:.4f} "
              f"({row['puf_homogeneous_rate']*100:.1f}%)")
        print(f"  ARX avg class size:         {row['arx_avg_class_size']:.1f}")

    # Print capability comparison
    print("\n" + "=" * 80)
    print("CAPABILITY COMPARISON: PUFGuard vs ARX vs sdcMicro")
    print("=" * 80)
    cap_table = [
        ("Sample k-anonymity risk", "Yes", "Yes", "Yes"),
        ("l-diversity / t-closeness risk", "Homogeneous-sensitive", "Yes (full)", "Yes (full)"),
        ("Population-based risk estimation", "No (future work)", "Yes", "Yes"),
        ("Structural identifier screening", "Yes", "No", "No"),
        ("Free-text detection", "Yes", "No", "No"),
        ("Configurable QID scenarios", "Yes (core/extended/coarse)", "Manual", "Manual"),
        ("Explainable policy decisions (ASP)", "Yes", "No", "No"),
        ("Fail-closed integrity constraints", "Yes", "No", "No"),
        ("Data transformation / anonymization", "No (assessment only)", "Yes", "Yes"),
        ("Sensitivity analysis automation", "Yes", "Manual", "Manual"),
        ("Deterministic reproducibility", "Yes (SHA-256 manifest)", "Partial", "Partial"),
        ("Source-file immutability enforcement", "Yes", "No", "No"),
    ]
    print(f"{'Capability':<45} {'PUFGuard':<30} {'ARX':<15} {'sdcMicro':<15}")
    print("-" * 105)
    for cap, puf, arx_v, sdc in cap_table:
        print(f"{cap:<45} {puf:<30} {arx_v:<15} {sdc:<15}")

    print(f"\nResults saved to: {out_dir / 'arx_comparison_results.csv'}")


if __name__ == "__main__":
    main()
