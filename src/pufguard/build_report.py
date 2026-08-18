"""Build the aggregate Markdown report from generated profile and logic tables."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def format_report(profiles: pd.DataFrame, decisions: pd.DataFrame) -> str:
    """Return the preliminary report text from dataset and decision frames."""

    merged = profiles.merge(decisions, on="dataset_id", how="left")
    lines = [
        "# PUFGuard preliminary benchmark report",
        "",
        "This report describes aggregate, sample-based signals. It does not claim that any person is identifiable.",
        "",
        "## Dataset-level findings",
        "",
        "| Dataset | Rows | Columns | Core singleton | Extended singleton | Below k=5 | Logic decision |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for _, row in merged.iterrows():
        lines.append(
            f"| {row.dataset_id}: {row.short_name} | {int(row.rows):,} | {int(row['columns'])} | "
            f"{row.singleton_rate_core:.1%} | {row.singleton_rate_extended:.1%} | "
            f"{row.records_below_k5_rate_extended:.1%} | {row.decision} |"
        )
    lines += [
        "",
        "## Interpretation limits",
        "",
        "- Direct identifiers and free text are structural release concerns, but their presence does not prove disclosure.",
        "- Sample uniqueness is an upper-layer warning signal; population uniqueness requires external population information.",
        "- The logic thresholds are research configuration values and are not legal safe-harbor thresholds.",
        "- Results must be validated by domain and privacy experts before any release decision.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    """Read generated tables and write the preliminary Markdown report."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, required=True, help="Root directory of the PUFGuard project.")
    args = parser.parse_args()
    root = args.project_root.resolve()
    profiles = pd.read_csv(root / "results/tables/dataset_privacy_profiles.csv")
    decisions = pd.read_csv(root / "results/tables/logic_decisions.csv")
    report = root / "results/reports/preliminary_findings.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(format_report(profiles, decisions), encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
