"""Profile the configured corpus and generate aggregate privacy-risk evidence.

The module reads immutable Excel inputs, normalizes values in memory, computes
column descriptors and QID equivalence-class metrics, and writes only aggregate
outputs. It does not perform identity lookup or cross-dataset record linkage.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path

import pandas as pd


def sha256_file(path: Path) -> str:
    """Return the hex SHA-256 digest of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize_column(value: object) -> str:
    """Normalize a header/value label without changing the raw source file."""

    text = str(value).replace("\u00a0", " ").replace("��", " ").strip()
    return re.sub(r"\s+", " ", text)


def normalized_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Return an analysis copy with normalized headers and string values."""

    result = df.copy()
    result.columns = [normalize_column(c) for c in result.columns]
    for column in result.columns:
        if pd.api.types.is_object_dtype(result[column]) or pd.api.types.is_string_dtype(result[column]):
            result[column] = result[column].map(
                lambda x: re.sub(r"\s+", " ", str(x).strip()) if pd.notna(x) else pd.NA
            )
    return result


def available(columns: list[str], requested: list[str], *, strict: bool = False) -> list[str]:
    """Return configured column names that are actually present, in order.

    When *strict* is True, raise ValueError if any requested column is missing.
    """
    have = set(columns)
    if strict:
        missing = [c for c in requested if c not in have]
        if missing:
            raise ValueError(
                f"Configured columns not found in DataFrame: {missing}. "
                f"Available columns: {sorted(have)}"
            )
    return [c for c in requested if c in have]


def equivalence_metrics(df: pd.DataFrame, qids: list[str], sensitive: str | None) -> dict:
    """Compute sample equivalence-class metrics for a selected QID scenario.

    Missing QID and sensitive values are treated as literal categories. String
    QIDs are stripped and case-folded; numeric QIDs are rounded to six decimals.
    The homogeneous-sensitive numerator excludes singleton classes, while its
    denominator remains the full number of dataset records.
    """

    qids = available(list(df.columns), qids)
    n = len(df)
    if n == 0 or not qids:
        return {
            "qid_count": len(qids), "equivalence_classes": 0, "minimum_k": 0,
            "median_k": 0.0, "singleton_records": 0, "singleton_rate": 0.0,
            "records_below_k5": 0, "records_below_k5_rate": 0.0,
            "homogeneous_sensitive_records_non_singleton": 0,
            "homogeneous_sensitive_rate_non_singleton": 0.0,
        }

    keys = df[qids].copy().fillna("<MISSING>")
    for c in qids:
        if pd.api.types.is_numeric_dtype(keys[c]):
            keys[c] = keys[c].round(6)
        else:
            keys[c] = keys[c].astype(str).str.strip().str.casefold()
    sizes = keys.groupby(qids, dropna=False).size().rename("group_size")
    singleton_records = int(sizes[sizes == 1].sum())
    below_k5_records = int(sizes[sizes < 5].sum())

    homogeneous_records = 0
    if sensitive and sensitive in df.columns:
        temp = keys.copy()
        temp["__sensitive__"] = df[sensitive].fillna("<MISSING>").astype(str).str.strip().str.casefold()
        stats = temp.groupby(qids, dropna=False).agg(
            group_size=("__sensitive__", "size"),
            sensitive_diversity=("__sensitive__", "nunique"),
        )
        homogeneous_records = int(
            stats.loc[(stats.group_size >= 2) & (stats.sensitive_diversity < 2), "group_size"].sum()
        )

    return {
        "qid_count": len(qids),
        "equivalence_classes": int(len(sizes)),
        "minimum_k": int(sizes.min()),
        "median_k": float(sizes.median()),
        "singleton_records": singleton_records,
        "singleton_rate": singleton_records / n,
        "records_below_k5": below_k5_records,
        "records_below_k5_rate": below_k5_records / n,
        "homogeneous_sensitive_records_non_singleton": homogeneous_records,
        "homogeneous_sensitive_rate_non_singleton": homogeneous_records / n,
    }


def nonempty_rate(series: pd.Series) -> float:
    """Return the share of nonmissing cells containing non-whitespace text."""

    values = series.dropna().astype(str).str.strip()
    return float((values != "").mean()) if len(values) else 0.0


def entropy(series: pd.Series) -> float:
    """Return Shannon entropy in bits, treating missing as a category."""

    counts = series.fillna("<MISSING>").astype(str).value_counts(normalize=True)
    return float(-(counts * counts.map(lambda p: math.log2(p) if p else 0.0)).sum())


def write_svg_bar(rows: list[dict], path: Path) -> None:
    """Write a dependency-free SVG of extended-scenario singleton rates."""

    width, height = 840, 430
    margin_left, margin_bottom, margin_top = 190, 70, 35
    chart_width = width - margin_left - 40
    chart_height = height - margin_bottom - margin_top
    maximum = max((r["singleton_rate_extended"] for r in rows), default=1.0)
    maximum = max(maximum, 0.01)
    bar_h = chart_height / max(len(rows), 1) * 0.58
    gap = chart_height / max(len(rows), 1)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#17202A}.label{font-size:15px}.value{font-size:14px;font-weight:bold}.axis{font-size:12px;fill:#52606D}</style>',
        f'<text x="{width/2}" y="24" text-anchor="middle" font-size="18" font-weight="bold">Extended quasi-identifier sample uniqueness</text>',
    ]
    for i, row in enumerate(rows):
        y = margin_top + i * gap + (gap - bar_h) / 2
        rate = row["singleton_rate_extended"]
        w = chart_width * rate / maximum
        parts.append(f'<text class="label" x="{margin_left-12}" y="{y+bar_h*0.68}" text-anchor="end">{row["dataset_id"]}: {row["short_name"]}</text>')
        parts.append(f'<rect x="{margin_left}" y="{y}" width="{w:.2f}" height="{bar_h:.2f}" rx="4" fill="#0F766E"/>')
        parts.append(f'<text class="value" x="{margin_left+w+8}" y="{y+bar_h*0.68}">{rate:.1%}</text>')
    parts.append(f'<line x1="{margin_left}" y1="{height-margin_bottom+5}" x2="{width-40}" y2="{height-margin_bottom+5}" stroke="#AAB7B8"/>')
    parts.append(f'<text class="axis" x="{margin_left}" y="{height-25}">0%</text>')
    parts.append(f'<text class="axis" x="{width-40}" y="{height-25}" text-anchor="end">maximum observed: {maximum:.1%}</text>')
    parts.append('</svg>')
    path.write_text("\n".join(parts), encoding="utf-8")


def main() -> None:
    """Run the configured corpus analysis and serialize aggregate products."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-root",
        type=Path,
        required=True,
        help="Root directory containing configs/, data/, logic/, and results/.",
    )
    args = parser.parse_args()
    root = args.project_root.resolve()
    configs = json.loads((root / "configs/datasets.json").read_text(encoding="utf-8"))
    thresholds = json.loads((root / "configs/policy_thresholds.json").read_text(encoding="utf-8"))

    # Verify source-file checksums against the immutable manifest (fail-closed)
    manifest_path = root / "data/metadata/integrity_manifest.csv"
    if not manifest_path.exists():
        raise FileNotFoundError(
            f"Integrity manifest not found: {manifest_path}. "
            f"Cannot verify source-file provenance."
        )
    manifest_df = pd.read_csv(manifest_path, encoding="utf-8-sig")
    expected_hashes: dict[str, str] = {}
    for _, row in manifest_df.iterrows():
        rel_path = row["relative_path"]
        if rel_path in expected_hashes:
            raise ValueError(
                f"Duplicate path in integrity manifest: {rel_path}"
            )
        expected_hashes[rel_path] = row["sha256"]

    source_checksums: list[dict] = []
    for dataset_id, cfg in configs.items():
        file_path = root / cfg["file"]
        if not file_path.exists():
            raise FileNotFoundError(
                f"Source file missing for {dataset_id}: {cfg['file']}"
            )
        if cfg["file"] not in expected_hashes:
            raise ValueError(
                f"No manifest entry for {dataset_id} ({cfg['file']}). "
                f"Every configured source must have a manifest row."
            )
        digest = sha256_file(file_path)
        expected = expected_hashes[cfg["file"]]
        if digest != expected:
            raise ValueError(
                f"SHA-256 mismatch for {dataset_id} ({cfg['file']}): "
                f"expected {expected[:16]}..., got {digest[:16]}... "
                f"Source file may have been modified."
            )
        source_checksums.append({
            "dataset_id": dataset_id, "file": cfg["file"],
            "sha256": digest, "status": "verified",
        })
        print(f"  {dataset_id}: {digest[:16]}...  verified  {cfg['file']}")

    profiles: list[dict] = []
    column_rows: list[dict] = []
    scenario_rows: list[dict] = []
    fact_lines: list[str] = [
        "% Generated by analyze_corpus.py; do not edit manually.",
        "% Source-file checksums compared against integrity_manifest.csv.",
    ]
    fact_lines += [
        f"threshold(singleton_high,{thresholds['singleton_high_basis_points']}).",
        f"threshold(singleton_medium,{thresholds['singleton_medium_basis_points']}).",
        f"threshold(below_k5_high,{thresholds['records_below_k5_high_basis_points']}).",
        f"threshold(homogeneous_high,{thresholds['homogeneous_sensitive_high_basis_points']}).",
    ]

    for dataset_id, cfg in configs.items():
        file_path = root / cfg["file"]
        df = normalized_frame(pd.read_excel(file_path, sheet_name=cfg.get("sheet", 0)))
        df = df.dropna(how="all").reset_index(drop=True)
        n, p = df.shape
        direct = available(list(df.columns), cfg["structural_identifiers"])
        free_text = available(list(df.columns), cfg["free_text"])
        sensitive = available(list(df.columns), cfg["sensitive"])
        primary_sensitive = cfg["primary_sensitive"] if cfg["primary_sensitive"] in df.columns else None
        available(list(df.columns), cfg["core_qids"], strict=True)
        available(list(df.columns), cfg["extended_qids"], strict=True)
        core = equivalence_metrics(df, cfg["core_qids"], primary_sensitive)
        extended = equivalence_metrics(df, cfg["extended_qids"], primary_sensitive)
        exact_duplicates = int(df.duplicated(keep=False).sum())
        missing_rate = float(df.isna().sum().sum() / (n * p)) if n and p else 0.0
        direct_unique = max(
            (df[c].nunique(dropna=True) / max(df[c].notna().sum(), 1) for c in direct),
            default=0.0,
        )
        free_text_rate = max((nonempty_rate(df[c]) for c in free_text), default=0.0)
        pattern_columns = [
            c for c in df.columns
            if any(c.startswith(prefix) for prefix in cfg.get("pattern_prefixes", []))
            and c != primary_sensitive
        ]
        pattern_unique_rate = 0.0
        if pattern_columns:
            pattern_unique_rate = float(df[pattern_columns].fillna("<MISSING>").drop_duplicates().shape[0] / n)

        profile = {
            "dataset_id": dataset_id,
            "short_name": cfg["name"],
            "domain": cfg["domain"],
            "rows": n,
            "columns": p,
            "structural_identifier_columns": len(direct),
            "free_text_columns": len(free_text),
            "sensitive_columns_configured": len(sensitive),
            "missing_cell_rate": missing_rate,
            "exact_duplicate_records_involved": exact_duplicates,
            "maximum_structural_identifier_uniqueness": direct_unique,
            "maximum_free_text_nonempty_rate": free_text_rate,
            "item_pattern_unique_rate": pattern_unique_rate,
            "singleton_rate_core": core["singleton_rate"],
            "records_below_k5_rate_core": core["records_below_k5_rate"],
            "singleton_rate_extended": extended["singleton_rate"],
            "records_below_k5_rate_extended": extended["records_below_k5_rate"],
            "homogeneous_sensitive_rate_extended": extended["homogeneous_sensitive_rate_non_singleton"],
            "minimum_k_extended": extended["minimum_k"],
            "median_k_extended": extended["median_k"],
        }
        profiles.append(profile)

        role_map: dict[str, str] = {}
        for c in df.columns:
            roles = []
            if c in direct: roles.append("structural_identifier")
            if c in free_text: roles.append("free_text")
            if c in sensitive: roles.append("sensitive")
            if c in available(list(df.columns), cfg["extended_qids"]): roles.append("quasi_identifier")
            if any(c.startswith(prefix) for prefix in cfg.get("pattern_prefixes", [])): roles.append("item_level")
            role_map[c] = ";".join(roles) if roles else "other"
            nonmissing = int(df[c].notna().sum())
            unique = int(df[c].nunique(dropna=True))
            column_rows.append({
                "dataset_id": dataset_id,
                "column_name": c,
                "role": role_map[c],
                "nonmissing_count": nonmissing,
                "missing_rate": 1 - nonmissing / n if n else 0.0,
                "unique_count": unique,
                "unique_rate_nonmissing": unique / nonmissing if nonmissing else 0.0,
                "entropy_bits": entropy(df[c]),
            })

        extended_qid_count = max(len(available(list(df.columns), cfg["extended_qids"])), 1)
        for scenario_name, qids in cfg["scenarios"].items():
            metrics = equivalence_metrics(df, qids, primary_sensitive)
            scenario_rows.append({
                "dataset_id": dataset_id,
                "short_name": cfg["name"],
                "scenario": scenario_name,
                "qid_count": metrics["qid_count"],
                "qid_retention_fraction": metrics["qid_count"] / extended_qid_count,
                "equivalence_classes": metrics["equivalence_classes"],
                "minimum_k": metrics["minimum_k"],
                "median_k": metrics["median_k"],
                "singleton_rate": metrics["singleton_rate"],
                "records_below_k5_rate": metrics["records_below_k5_rate"],
                "homogeneous_sensitive_rate": metrics["homogeneous_sensitive_rate_non_singleton"],
            })

        atom = dataset_id.lower()
        fact_lines += [
            f"dataset({atom}).",
            f"rows({atom},{n}).",
            f"columns({atom},{p}).",
            f"singleton_bp({atom},{round(extended['singleton_rate'] * 10000)}).",
            f"below_k5_bp({atom},{round(extended['records_below_k5_rate'] * 10000)}).",
            f"homogeneous_bp({atom},{round(extended['homogeneous_sensitive_rate_non_singleton'] * 10000)}).",
        ]
        if sensitive: fact_lines.append(f"sensitive({atom}).")
        if direct: fact_lines.append(f"structural_identifier({atom}).")
        if free_text: fact_lines.append(f"free_text({atom}).")

    tables = root / "results/tables"
    figures = root / "results/figures"
    processed = root / "data/processed"
    logic = root / "logic"
    for folder in (tables, figures, processed, logic): folder.mkdir(parents=True, exist_ok=True)

    profiles_df = pd.DataFrame(profiles)
    profiles_df.to_csv(tables / "dataset_privacy_profiles.csv", index=False, encoding="utf-8-sig")
    profiles_df.to_csv(processed / "dataset_level_profiles.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(column_rows).to_csv(tables / "column_inventory.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(scenario_rows).to_csv(tables / "privacy_utility_scenarios.csv", index=False, encoding="utf-8-sig")
    (logic / "generated_facts.lp").write_text("\n".join(fact_lines) + "\n", encoding="utf-8")
    write_svg_bar(profiles, figures / "singleton_rates.svg")

    # Write source checksums alongside results
    pd.DataFrame(source_checksums).to_csv(
        tables / "source_checksums.csv", index=False, encoding="utf-8-sig"
    )

    macros = [
        "% Generated result macros — verified against source-file checksums.",
        "% Rerun analyze_corpus.py to regenerate; see source_checksums.csv for provenance.",
    ]
    for row in profiles:
        key = {"D1": "DOne", "D2": "DTwo", "D3": "DThree", "D4": "DFour", "D5": "DFive"}.get(
            row["dataset_id"], row["dataset_id"].replace("_", "")
        )
        macros += [
            rf"\newcommand{{\{key}Rows}}{{{row['rows']:,}}}",
            rf"\newcommand{{\{key}Cols}}{{{row['columns']}}}",
            rf"\newcommand{{\{key}Singleton}}{{{row['singleton_rate_extended'] * 100:.1f}\%}}",
            rf"\newcommand{{\{key}CoreSingleton}}{{{row['singleton_rate_core'] * 100:.1f}\%}}",
            rf"\newcommand{{\{key}BelowKFive}}{{{row['records_below_k5_rate_extended'] * 100:.1f}\%}}",
        ]
    (tables / "paper1_macros.tex").write_text("\n".join(macros) + "\n", encoding="utf-8")

    table_lines = []
    for row in profiles:
        table_lines.append(
            f"{row['dataset_id']} & {row['rows']:,} & {row['columns']} & "
            f"{row['structural_identifier_columns']} & {row['free_text_columns']} & "
            f"{row['singleton_rate_core'] * 100:.1f}\\% & {row['singleton_rate_extended'] * 100:.1f}\\% & "
            f"{row['records_below_k5_rate_extended'] * 100:.1f}\\% \\\\"
        )
    (tables / "paper1_profile_rows.tex").write_text("\n".join(table_lines) + "\n", encoding="utf-8")

    print(profiles_df.to_string(index=False))


if __name__ == "__main__":
    main()
