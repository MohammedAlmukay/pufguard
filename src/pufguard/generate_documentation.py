"""Generate auditable metadata and documentation from the immutable corpus.

This module never writes row-level derivatives. It reads the configured source
workbooks and creates only metadata, aggregate quality findings, checksums, and
human-readable documentation. Free text and direct-identifier values are
suppressed from every generated artifact.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import date
from pathlib import Path

import pandas as pd

try:  # Package execution: python -m pufguard.generate_documentation
    from .analyze_corpus import available, normalize_column, normalized_frame
except ImportError:  # Script execution used by run_all.ps1
    from analyze_corpus import available, normalize_column, normalized_frame


VERIFICATION_DATE = date(2026, 8, 10)


METRICS = [
    {
        "metric": "missing_cell_rate",
        "definition": "Fraction of all dataset cells that are missing after import.",
        "formula": "missing cells / (rows * columns)",
        "scope": "dataset",
        "range": "0 to 1",
        "interpretation": "Describes completeness; it is not a privacy-risk metric by itself.",
        "implementation": "src/pufguard/analyze_corpus.py",
    },
    {
        "metric": "unique_rate_nonmissing",
        "definition": "Fraction of nonmissing values in a column that are distinct.",
        "formula": "distinct nonmissing values / nonmissing values",
        "scope": "column",
        "range": "0 to 1",
        "interpretation": "High values can indicate identifier-like or high-cardinality fields.",
        "implementation": "src/pufguard/analyze_corpus.py",
    },
    {
        "metric": "entropy_bits",
        "definition": "Shannon entropy of a column after representing missing values as a category.",
        "formula": "-sum(p_i * log2(p_i))",
        "scope": "column",
        "range": "0 to log2(number of categories)",
        "interpretation": "Information-content descriptor; not an identification probability.",
        "implementation": "src/pufguard/analyze_corpus.py",
    },
    {
        "metric": "equivalence_class",
        "definition": "Records sharing the same normalized values on a selected quasi-identifier set.",
        "formula": "group by configured QID tuple; missing is a literal category",
        "scope": "scenario",
        "range": "one or more records",
        "interpretation": "The class depends completely on the selected QIDs and observed sample.",
        "implementation": "src/pufguard/analyze_corpus.py::equivalence_metrics",
    },
    {
        "metric": "minimum_k",
        "definition": "Smallest observed equivalence-class size.",
        "formula": "min(class size)",
        "scope": "scenario",
        "range": "1 to number of records",
        "interpretation": "k=1 means at least one sample-unique record under the scenario.",
        "implementation": "src/pufguard/analyze_corpus.py::equivalence_metrics",
    },
    {
        "metric": "median_k",
        "definition": "Median size across equivalence classes, not across records.",
        "formula": "median(class sizes)",
        "scope": "scenario",
        "range": "1 to number of records",
        "interpretation": "Summarizes a typical class; it can hide a risky lower tail.",
        "implementation": "src/pufguard/analyze_corpus.py::equivalence_metrics",
    },
    {
        "metric": "singleton_rate",
        "definition": "Fraction of records belonging to equivalence classes of size one.",
        "formula": "records in size-1 classes / all records",
        "scope": "scenario",
        "range": "0 to 1",
        "interpretation": "Sample uniqueness warning only; not proof of population uniqueness or re-identification.",
        "implementation": "src/pufguard/analyze_corpus.py::equivalence_metrics",
    },
    {
        "metric": "records_below_k5_rate",
        "definition": "Fraction of records in equivalence classes smaller than five.",
        "formula": "records in classes with size < 5 / all records",
        "scope": "scenario",
        "range": "0 to 1",
        "interpretation": "Descriptive benchmark using k=5; not a legal threshold.",
        "implementation": "src/pufguard/analyze_corpus.py::equivalence_metrics",
    },
    {
        "metric": "homogeneous_sensitive_rate_non_singleton",
        "definition": "Fraction of all records in non-singleton QID classes containing only one normalized sensitive value.",
        "formula": "records in classes size>=2 and sensitive diversity<2 / all records",
        "scope": "scenario",
        "range": "0 to 1",
        "interpretation": "Attribute-disclosure warning; missing sensitive values are treated as a category.",
        "implementation": "src/pufguard/analyze_corpus.py::equivalence_metrics",
    },
    {
        "metric": "item_pattern_unique_rate",
        "definition": "Fraction of distinct row patterns across configured item-level columns.",
        "formula": "distinct item-response rows / all records",
        "scope": "dataset",
        "range": "0 to 1",
        "interpretation": "Describes fingerprint-like granularity of response vectors.",
        "implementation": "src/pufguard/analyze_corpus.py",
    },
    {
        "metric": "qid_retention_fraction",
        "definition": "Share of extended-scenario QIDs retained in a scenario.",
        "formula": "scenario QID count / extended QID count",
        "scope": "scenario",
        "range": "0 to 1",
        "interpretation": "A structural utility proxy, not measured analytic utility.",
        "implementation": "src/pufguard/analyze_corpus.py",
    },
]


def sha256_file(path: Path) -> str:
    """Return the lowercase SHA-256 digest of *path* using streamed reads."""

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def replace_groups(template: str, match: re.Match[str]) -> str:
    """Replace ``{1}``, ``{2}``, ... placeholders with regex groups."""

    result = template
    for index, value in enumerate(match.groups(), start=1):
        result = result.replace("{" + str(index) + "}", value)
    return result


def infer_measurement_level(series: pd.Series) -> str:
    """Infer a conservative measurement-level label from dtype/cardinality."""

    nonmissing = series.dropna()
    unique = nonmissing.nunique()
    if pd.api.types.is_numeric_dtype(series):
        return "numeric" if unique > 12 else "numeric code or discrete score"
    return "categorical text" if unique <= 30 else "high-cardinality text"


def observed_summary(series: pd.Series, roles: set[str]) -> str:
    """Describe values without exposing free text or identifier contents."""

    nonmissing = series.dropna()
    unique = int(nonmissing.nunique())
    if "free_text" in roles:
        return f"{unique} distinct nonmissing texts; contents suppressed"
    if "structural_identifier" in roles:
        return f"{unique} distinct nonmissing values; contents suppressed"
    if not len(nonmissing):
        return "no nonmissing values"
    if pd.api.types.is_numeric_dtype(series):
        if unique <= 12:
            values = sorted(nonmissing.unique().tolist())
            return "; ".join(str(value) for value in values)
        return f"min={nonmissing.min():g}; max={nonmissing.max():g}; {unique} distinct"
    values = sorted({normalize_column(value) for value in nonmissing.astype(str)})
    if unique <= 12 and sum(len(value) for value in values) <= 600:
        return "; ".join(values)
    return f"{unique} observed categories/text values; not enumerated"


def semantic_annotation(dataset_id: str, column: str, annotations: dict) -> dict:
    """Resolve an exact or pattern annotation, otherwise document uncertainty."""

    dataset = annotations["datasets"][dataset_id]
    exact = dataset.get("exact", {})
    if column in exact:
        item = dict(exact[column])
        item.setdefault("status", dataset.get("default_status", "needs_author_confirmation"))
        return item
    for rule in dataset.get("patterns", []):
        match = re.fullmatch(rule["regex"], column)
        if match:
            return {
                "description": replace_groups(rule["description_template"], match),
                "measurement_level": rule.get("measurement_level", "not specified"),
                "unit": rule.get("unit", ""),
                "coding": rule.get("coding", ""),
                "formula": rule.get("formula", ""),
                "source": rule.get("source", "pattern annotation"),
                "status": rule.get("status", dataset.get("default_status", "needs_author_confirmation")),
            }
    if len(column) >= 18 or "?" in column:
        return {
            "description": column,
            "source": "self-describing column header",
            "status": dataset.get("default_status", "confirmed_column_header"),
        }
    return {
        "description": f"Deposited variable '{column}'; a more specific semantic definition is not available in the local package.",
        "source": "column header only",
        "status": "needs_author_confirmation",
    }


def role_rationale(roles: set[str], dataset_id: str, column: str) -> str:
    """Explain why a variable has its configured privacy role."""

    reasons: list[str] = []
    if "structural_identifier" in roles:
        reasons.append("identifier-like or operational field excluded from public release candidates")
    if "free_text" in roles:
        reasons.append("unstructured text may contain unforeseen personal details")
    if "sensitive" in roles:
        domain = "health/psychological" if dataset_id in {"D1", "D2", "D3"} else "employment/health"
        reasons.append(f"configured outcome or {domain} attribute used for attribute-disclosure checks")
    if "quasi_identifier" in roles:
        reasons.append("plausibly linkable background attribute under the stated auxiliary-knowledge model")
    if "item_level" in roles:
        reasons.append("fine-grained response item contributing to a potentially distinctive response pattern")
    if not reasons:
        reasons.append("not used by the current privacy-role configuration")
    return "; ".join(reasons)


def build_dictionary(root: Path, configs: dict, annotations: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build the variable dictionary and aggregate quality-finding table."""

    rows: list[dict] = []
    quality: list[dict] = []
    for dataset_id, cfg in configs.items():
        source_frame = pd.read_excel(root / cfg["file"], sheet_name=cfg.get("sheet", 0))
        frame = normalized_frame(source_frame)
        columns = list(frame.columns)
        direct = set(available(columns, cfg["structural_identifiers"]))
        free_text = set(available(columns, cfg["free_text"]))
        sensitive = set(available(columns, cfg["sensitive"]))
        extended = set(available(columns, cfg["extended_qids"]))
        pattern = {
            column
            for column in columns
            if any(column.startswith(prefix) for prefix in cfg.get("pattern_prefixes", []))
        }
        scenarios = {
            name: set(available(columns, qids)) for name, qids in cfg["scenarios"].items()
        }
        for index, column in enumerate(columns, start=1):
            series = frame[column]
            source_series = source_frame.iloc[:, index - 1]
            roles: set[str] = set()
            if column in direct:
                roles.add("structural_identifier")
            if column in free_text:
                roles.add("free_text")
            if column in sensitive:
                roles.add("sensitive")
            if column in extended:
                roles.add("quasi_identifier")
            if column in pattern:
                roles.add("item_level")
            annotation = semantic_annotation(dataset_id, column, annotations)
            nonmissing = int(series.notna().sum())
            missing = int(series.isna().sum())
            unique = int(series.nunique(dropna=True))
            memberships = [name for name, members in scenarios.items() if column in members]
            rows.append(
                {
                    "dataset_id": dataset_id,
                    "short_name": cfg["name"],
                    "column_index": index,
                    "variable_name": column,
                    "privacy_role": ";".join(sorted(roles)) if roles else "other",
                    "role_rationale": role_rationale(roles, dataset_id, column),
                    "semantic_description": annotation["description"],
                    "measurement_level": annotation.get("measurement_level", infer_measurement_level(series)),
                    "unit": annotation.get("unit", ""),
                    "coding_or_expected_range": annotation.get("coding", ""),
                    "observed_values_summary": observed_summary(series, roles),
                    "nonmissing_count": nonmissing,
                    "missing_count": missing,
                    "missing_rate": missing / len(frame) if len(frame) else 0.0,
                    "unique_count": unique,
                    "scenario_membership": ";".join(memberships),
                    "derived_formula": annotation.get("formula", ""),
                    "semantic_source": annotation.get("source", "not specified"),
                    "semantic_status": annotation["status"],
                    "source_url": annotations["datasets"][dataset_id]["source_url"],
                }
            )

            raw_text = source_series.dropna().astype(str)
            whitespace_count = int(raw_text.map(lambda value: value != value.strip()).sum())
            nbsp_count = int(raw_text.str.contains("\u00a0", regex=False).sum())
            error_count = int(raw_text.str.fullmatch(r"#(?:VALUE!|REF!|N/A|NAME\?)", case=False).sum())
            if missing:
                quality.append(
                    {
                        "dataset_id": dataset_id,
                        "variable_name": column,
                        "issue_type": "missing_values",
                        "count": missing,
                        "rate": missing / len(frame),
                        "severity": "warning" if missing / len(frame) >= 0.05 else "information",
                        "detail": "Missing values are retained as a literal category in QID equivalence calculations.",
                        "recommended_action": "Confirm whether missingness is structural, refusal, or data loss before substantive analysis.",
                    }
                )
            if whitespace_count or nbsp_count:
                quality.append(
                    {
                        "dataset_id": dataset_id,
                        "variable_name": column,
                        "issue_type": "whitespace_normalization",
                        "count": max(whitespace_count, nbsp_count),
                        "rate": max(whitespace_count, nbsp_count) / max(len(frame), 1),
                        "severity": "information",
                        "detail": "Leading/trailing or non-breaking whitespace is present in the source file.",
                        "recommended_action": "Normalize only in an analysis copy; preserve the raw file unchanged.",
                    }
                )
            if error_count:
                quality.append(
                    {
                        "dataset_id": dataset_id,
                        "variable_name": column,
                        "issue_type": "spreadsheet_error_token",
                        "count": error_count,
                        "rate": error_count / len(frame),
                        "severity": "warning",
                        "detail": "The literal token #VALUE! or another spreadsheet-error label appears as data.",
                        "recommended_action": "Obtain depositor clarification and define a documented missing/invalid-value rule.",
                    }
                )
            if "structural_identifier" in roles:
                quality.append(
                    {
                        "dataset_id": dataset_id,
                        "variable_name": column,
                        "issue_type": "identifier_like_field",
                        "count": nonmissing,
                        "rate": nonmissing / max(len(frame), 1),
                        "severity": "high",
                        "detail": "Configured as a direct or operational identifier-like field.",
                        "recommended_action": "Exclude or transform before any derived public release; document the decision.",
                    }
                )
            if "free_text" in roles:
                quality.append(
                    {
                        "dataset_id": dataset_id,
                        "variable_name": column,
                        "issue_type": "free_text_field",
                        "count": nonmissing,
                        "rate": nonmissing / max(len(frame), 1),
                        "severity": "high",
                        "detail": "Unstructured text can contain unanticipated personal or sensitive information.",
                        "recommended_action": "Do not quote or redistribute; use a separately approved redaction or feature-extraction protocol.",
                    }
                )
            if annotation["status"] in {"coding_not_deposited", "needs_author_confirmation", "partially_verified_rounding_unresolved"}:
                quality.append(
                    {
                        "dataset_id": dataset_id,
                        "variable_name": column,
                        "issue_type": "semantic_documentation_gap",
                        "count": 1,
                        "rate": 1.0,
                        "severity": "warning",
                        "detail": annotation["status"],
                        "recommended_action": "Resolve with the depositor or report the limitation explicitly; do not infer code labels.",
                    }
                )

        duplicate_count = int(frame.duplicated(keep=False).sum())
        if duplicate_count:
            quality.append(
                {
                    "dataset_id": dataset_id,
                    "variable_name": "<dataset>",
                    "issue_type": "exact_duplicate_records_involved",
                    "count": duplicate_count,
                    "rate": duplicate_count / len(frame),
                    "severity": "information",
                    "detail": "Count includes every row participating in an exact duplicate group.",
                    "recommended_action": "Determine whether duplicates are expected before modeling; do not alter the raw file.",
                }
            )
    return pd.DataFrame(rows), pd.DataFrame(quality)


def write_dictionary_markdown(dictionary: pd.DataFrame, root: Path) -> None:
    """Write a navigable Markdown view of the complete variable dictionary."""

    lines = [
        "# Complete variable dictionary",
        "",
        "This document is generated from `configs/semantic_annotations.json` and the immutable source workbooks.",
        "The authoritative machine-readable version is `data/metadata/data_dictionary.csv`.",
        "Observed free-text and identifier values are intentionally suppressed.",
        "",
        "## Status vocabulary",
        "",
        "- `confirmed_*`: supported by a repository description, related publication, source document, or self-describing survey header.",
        "- `derived_and_empirically_verified`: formula reproduced for every deposited row.",
        "- `partially_verified_rounding_unresolved`: construct is known but deposited rounding is not exactly reproducible.",
        "- `coding_not_deposited`: construct is known but numeric code labels are missing.",
        "- `needs_author_confirmation`: a specific semantic claim would require depositor confirmation.",
    ]
    for dataset_id, group in dictionary.groupby("dataset_id", sort=True):
        lines += [
            "",
            f"## {dataset_id}: {group.iloc[0]['short_name']}",
            "",
            "| # | Variable | Privacy role | Meaning | Coding/unit | Semantic status |",
            "|---:|---|---|---|---|---|",
        ]
        for _, row in group.iterrows():
            escape = lambda value: str(value).replace("|", "\\|").replace("\n", " ")
            coding = "; ".join(filter(None, [str(row["coding_or_expected_range"]), str(row["unit"])]))
            lines.append(
                f"| {int(row['column_index'])} | `{escape(row['variable_name'])}` | "
                f"{escape(row['privacy_role'])} | {escape(row['semantic_description'])} | "
                f"{escape(coding)} | {escape(row['semantic_status'])} |"
            )
    (root / "docs/DATA_DICTIONARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_quality_markdown(quality: pd.DataFrame, root: Path) -> None:
    """Write aggregate quality findings without exposing row contents."""

    counts = quality.groupby(["dataset_id", "severity"]).size().unstack(fill_value=0)
    lines = [
        "# Data quality and semantic audit",
        "",
        "This audit describes source-file conditions; it does not edit raw data and does not label participants.",
        "The detailed machine-readable findings are in `data/metadata/data_quality_findings.csv`.",
        "",
        "## Finding counts",
        "",
        "| Dataset | Information | Warning | High |",
        "|---|---:|---:|---:|",
    ]
    for dataset_id in sorted(quality["dataset_id"].unique()):
        row = counts.loc[dataset_id]
        lines.append(
            f"| {dataset_id} | {int(row.get('information', 0))} | {int(row.get('warning', 0))} | {int(row.get('high', 0))} |"
        )
    lines += [
        "",
        "## Material findings",
        "",
        "- D1 contains a small number of exact duplicate rows; the raw file is preserved and no deduplication is performed.",
        "- D2 contains record-unique timestamps, an operational researcher code, free text, literal spreadsheet-error tokens, and translated category labels requiring clarification.",
        "- D3 contains a participant ID and several coded demographic variables without a local code-to-label map. Aggregate Gain/Loss fields show a small deposited rounding discrepancy (maximum 0.05) relative to visible components.",
        "- D4 contains a participant ID and extensive whitespace/category variants. The included Word files support most semantic definitions, but the numeric allowance code still requires confirmation.",
        "",
        "## Handling rule",
        "",
        "All normalization occurs in memory for analysis. Corrections belong in a versioned processed-data layer with an explicit transformation log; they must never overwrite `data/raw/`.",
    ]
    (root / "docs/DATA_QUALITY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_coverage_markdown(dictionary: pd.DataFrame, root: Path) -> None:
    """Document semantic-coverage counts and unresolved fields."""

    status_counts = dictionary["semantic_status"].value_counts().sort_index()
    unresolved_statuses = {
        "coding_not_deposited",
        "needs_author_confirmation",
        "partially_verified_rounding_unresolved",
    }
    unresolved = dictionary[dictionary["semantic_status"].isin(unresolved_statuses)]
    supported = len(dictionary) - len(unresolved)
    lines = [
        "# Documentation coverage",
        "",
        f"The dictionary contains all **{len(dictionary)}** variables across five source datasets.",
        f"**{supported}** variables have repository-, publication-, source-document-, header-, or formula-supported semantics; **{len(unresolved)}** retain an explicit documentation limitation.",
        "Coverage means that every variable has a row and status; it does not mean that missing code labels were guessed.",
        "",
        "## Status counts",
        "",
        "| Semantic status | Variables |",
        "|---|---:|",
    ]
    lines += [f"| `{status}` | {int(count)} |" for status, count in status_counts.items()]
    lines += [
        "",
        "## Fields requiring follow-up",
        "",
        "| Dataset | Variable | Status | Required clarification |",
        "|---|---|---|---|",
    ]
    for _, row in unresolved.iterrows():
        lines.append(
            f"| {row.dataset_id} | `{str(row.variable_name).replace('|', '/')} ` | "
            f"`{row.semantic_status}` | Confirm coding, item mapping, or rounding with the depositor. |"
        )
    (root / "docs/DOCUMENTATION_COVERAGE.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_manifest(root: Path, configs: dict) -> pd.DataFrame:
    """Create a checksummed manifest for every immutable raw input file."""

    source_by_dataset = {dataset_id: cfg for dataset_id, cfg in configs.items()}
    rows: list[dict] = []
    checksum_lines: list[str] = []
    for path in sorted((root / "data/raw").rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        dataset_id = path.parent.name.split("_", 1)[0]
        digest = sha256_file(path)
        cfg = source_by_dataset[dataset_id]
        rows.append(
            {
                "dataset_id": dataset_id,
                "relative_path": relative,
                "file_type": path.suffix.lower().lstrip("."),
                "size_bytes": path.stat().st_size,
                "sha256": digest,
                "repository_url": json.loads((root / "configs/semantic_annotations.json").read_text(encoding="utf-8"))["datasets"][dataset_id]["source_url"],
                "license": "CC BY 4.0",
                "retrieval_date": "not_recorded",
                "integrity_verified_on": VERIFICATION_DATE.isoformat(),
                "project_handling": "immutable input; never overwritten",
            }
        )
        checksum_lines.append(f"{digest} *{relative}")
    (root / "data/metadata/checksums.sha256").write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")
    return pd.DataFrame(rows)


def main() -> None:
    """Generate the complete documentation metadata package."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, required=True, help="Root directory of the PUFGuard project.")
    args = parser.parse_args()
    root = args.project_root.resolve()
    configs = json.loads((root / "configs/datasets.json").read_text(encoding="utf-8"))
    annotations = json.loads((root / "configs/semantic_annotations.json").read_text(encoding="utf-8"))

    dictionary, quality = build_dictionary(root, configs, annotations)
    metadata = root / "data/metadata"
    metadata.mkdir(parents=True, exist_ok=True)
    dictionary.to_csv(metadata / "data_dictionary.csv", index=False, encoding="utf-8-sig")
    quality.to_csv(metadata / "data_quality_findings.csv", index=False, encoding="utf-8-sig")
    manifest = write_manifest(root, configs)
    manifest.to_csv(metadata / "integrity_manifest.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(METRICS).to_csv(metadata / "metric_dictionary.csv", index=False, encoding="utf-8-sig")

    write_dictionary_markdown(dictionary, root)
    write_quality_markdown(quality, root)
    write_coverage_markdown(dictionary, root)
    print(
        json.dumps(
            {
                "variables_documented": len(dictionary),
                "quality_findings": len(quality),
                "raw_files_checksummed": len(manifest),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
