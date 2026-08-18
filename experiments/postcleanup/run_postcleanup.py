"""Post-cleanup (second-stage) disclosure-risk assessment.

The main pipeline screens raw deposits. For the three datasets classified as
``restricted_review'' (D2, D3, D4), that outcome is driven by removable
structural fields -- record identifiers, a timestamp, and a free-text column.
A realistic release workflow has two stages: (1) screen the raw deposit and
recommend removals, then (2) re-assess the cleaned file. This script performs
stage 2 by removing exactly the facts that correspond to the rule base's own
recommended actions (``remove_structural_identifiers'' and
``redact_or_model_free_text'') and re-solving the unchanged policy program.

The quasi-identifier metrics (singleton rate, below-k=5 rate, homogeneity) are
unchanged by removing a record-identifier or free-text column, because those
columns are not quasi-identifiers. The experiment therefore isolates one
question: once the structural triggers are gone, does the file become a
public-use candidate, or does residual quasi-identifier linkability still force
remediation?

Usage:
    python experiments/postcleanup/run_postcleanup.py --project-root .
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

import clingo

# Datasets whose raw-deposit outcome is restricted_review, and the structural
# facts a custodian would remove by applying the recommended actions.
CLEANUP = {
    "d2": ["structural_identifier(d2).", "free_text(d2)."],
    "d3": ["structural_identifier(d3)."],
    "d4": ["structural_identifier(d4)."],
}


def solve(rules: str, facts: str) -> tuple[dict[str, str], dict[str, list[str]]]:
    """Return (decisions, flags) from one stable model of rules+facts."""
    control = clingo.Control(["0"])
    control.add("base", [], rules + "\n" + facts)
    control.ground([("base", [])])
    decisions: dict[str, str] = {}
    flags: dict[str, list[str]] = defaultdict(list)
    models = 0
    with control.solve(yield_=True) as handle:
        for model in handle:
            models += 1
            atoms = [str(s) for s in model.symbols(shown=True)]
            if models > 1:
                raise SystemExit("ERROR: multiple stable models; expected one.")
            decisions.clear()
            flags.clear()
            for atom in atoms:
                pred, rest = atom.split("(", 1)
                d, v = [p.strip() for p in rest[:-1].split(",", 1)]
                if pred == "decision":
                    decisions[d] = v
                elif pred == "flag":
                    flags[d].append(v)
    if models == 0:
        raise SystemExit("ERROR: UNSATISFIABLE; check facts.")
    return decisions, {k: sorted(v) for k, v in flags.items()}


def make_cleaned_facts(facts: str) -> str:
    """Drop the structural_identifier/free_text lines listed in CLEANUP."""
    remove = {line for lines in CLEANUP.values() for line in lines}
    kept = [ln for ln in facts.splitlines() if ln.strip() not in remove]
    return "\n".join(kept)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, required=True)
    args = parser.parse_args()
    root = args.project_root.resolve()

    rules = (root / "logic/privacy_rules.lp").read_text(encoding="utf-8")
    facts = (root / "logic/generated_facts.lp").read_text(encoding="utf-8")

    before_dec, before_flags = solve(rules, facts)
    after_dec, after_flags = solve(rules, make_cleaned_facts(facts))

    rows = []
    for d in sorted(before_dec):
        cleaned = d in CLEANUP
        rows.append(
            {
                "dataset_id": d.upper(),
                "raw_deposit_decision": before_dec[d],
                "cleaned": "yes" if cleaned else "no (unchanged)",
                "post_cleanup_decision": after_dec[d],
                "decision_changed": "yes" if before_dec[d] != after_dec[d] else "no",
                "raw_flags": "; ".join(before_flags.get(d, [])),
                "post_cleanup_flags": "; ".join(after_flags.get(d, [])),
            }
        )

    out_dir = root / "experiments/postcleanup"
    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / "postcleanup_results.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (out_dir / "postcleanup_results.json").write_text(
        json.dumps({"cleanup_applied": CLEANUP, "results": rows}, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
