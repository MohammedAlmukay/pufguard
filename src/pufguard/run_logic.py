"""Execute the PUFGuard Answer Set Program and serialize its rule trace.

The pipeline is fail-closed: if the program is unsatisfiable (e.g., because
required profile facts are missing), the runner exits with an error rather
than producing an empty or permissive result.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

import clingo


def parse_shown_atoms(atoms: list[str]) -> tuple[dict[str, str], dict[str, list[str]], dict[str, list[str]]]:
    """Parse shown decision, action, and flag atoms by dataset."""

    decisions: dict[str, str] = {}
    actions: dict[str, list[str]] = defaultdict(list)
    flags: dict[str, list[str]] = defaultdict(list)
    for atom in atoms:
        predicate, rest = atom.split("(", 1)
        args_text = rest[:-1]
        dataset, value = [part.strip() for part in args_text.split(",", 1)]
        if predicate == "decision":
            decisions[dataset.upper()] = value
        elif predicate == "action":
            actions[dataset.upper()].append(value)
        elif predicate == "flag":
            flags[dataset.upper()].append(value)
    return decisions, actions, flags


def build_decision_rows(atoms: list[str]) -> list[dict[str, str]]:
    """Return deterministic CSV-ready decision rows from shown ASP atoms."""

    decisions, actions, flags = parse_shown_atoms(atoms)
    rows: list[dict[str, str]] = []
    for dataset in sorted(set(decisions) | set(actions) | set(flags)):
        rows.append(
            {
                "dataset_id": dataset,
                "decision": decisions.get(dataset, "unresolved"),
                "flags": "; ".join(sorted(flags.get(dataset, []))),
                "recommended_actions": "; ".join(sorted(actions.get(dataset, []))),
            }
        )
    return rows


def main() -> None:
    """Load facts/rules, solve, and write the explainable trace.

    Fail-closed behavior: if the solver finds no stable model (UNSATISFIABLE),
    the pipeline halts with a non-zero exit code. This occurs when required
    profile facts are missing or integrity constraints are violated.
    """

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, required=True, help="Root directory of the PUFGuard project.")
    args = parser.parse_args()
    root = args.project_root.resolve()

    control = clingo.Control(["0"])
    control.load(str(root / "logic/privacy_rules.lp"))
    control.load(str(root / "logic/generated_facts.lp"))
    control.ground([("base", [])])

    models_found = 0
    atoms: list[str] = []
    with control.solve(yield_=True) as handle:
        for model in handle:
            models_found += 1
            atoms = sorted(str(symbol) for symbol in model.symbols(shown=True))
            if models_found > 1:
                print("ERROR: Multiple stable models found. The ASP program "
                      "should produce exactly one. Check integrity constraints.",
                      file=sys.stderr)
                sys.exit(2)

    if models_found == 0:
        print("ERROR: No stable model found (UNSATISFIABLE). This means "
              "required profile facts are missing or integrity constraints "
              "are violated. Check generated_facts.lp for completeness.",
              file=sys.stderr)
        sys.exit(1)

    rows = build_decision_rows(atoms)

    output = root / "results/tables/logic_decisions.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=["dataset_id", "decision", "flags", "recommended_actions"])
        writer.writeheader()
        writer.writerows(rows)
    (root / "results/tables/logic_model.json").write_text(
        json.dumps({"shown_atoms": atoms, "decisions": rows}, indent=2), encoding="utf-8"
    )
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
