"""
Expanded sensitivity analysis for PUFGuard (RF-06 response).

Three analysis dimensions:
  1. One-at-a-time threshold sweeps for singleton_high, below_k5_high,
     and homogeneous_high (holding the other two at default).
  2. Role-perturbation tests: remove sensitive(D) from D1,
     remove structural_identifier(D) from D2, and observe decision changes.
  3. Summary table covering all experiments.

Results are saved to sensitivity_full_results.csv and .json.
"""
import sys, os, json, time, csv
from pathlib import Path

# Add project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import clingo

RULES_FILE = PROJECT_ROOT / "logic" / "privacy_rules.lp"
FACTS_FILE = PROJECT_ROOT / "logic" / "generated_facts.lp"
OUTPUT_DIR = Path(__file__).resolve().parent
OUTPUT_CSV = OUTPUT_DIR / "sensitivity_full_results.csv"
OUTPUT_JSON = OUTPUT_DIR / "sensitivity_full_results.json"

# ---------- Threshold configurations ----------
DEFAULTS = {
    "singleton_high": 1000,
    "singleton_medium": 100,
    "below_k5_high": 2500,
    "homogeneous_high": 2500,
}

SWEEPS = {
    "singleton_high":   [500, 750, 1000, 1500, 2000],
    "below_k5_high":    [1500, 2000, 2500, 3000, 3500],
    "homogeneous_high": [1500, 2000, 2500, 3000, 3500],
}

DATASETS = ["d1", "d2", "d3", "d4", "d5"]


# ---------- Helpers ----------

def load_facts_without_thresholds(facts_path):
    """Load generated facts, stripping threshold lines (we override them)."""
    lines = []
    with open(facts_path) as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith("threshold("):
                continue
            if stripped.startswith("%"):
                continue
            if stripped:
                lines.append(stripped)
    return "\n".join(lines)


def remove_fact(facts_str, fact_to_remove):
    """Remove a specific fact atom (e.g. 'sensitive(d1).') from the facts string."""
    lines = facts_str.split("\n")
    filtered = [l for l in lines if l.strip() != fact_to_remove]
    return "\n".join(filtered)


def run_clingo(rules_path, facts_str, threshold_overrides):
    """Run Clingo with given facts and threshold overrides. Return decisions, flags, actions."""
    threshold_facts = "\n".join(
        f"threshold({name},{val})."
        for name, val in threshold_overrides.items()
    )
    full_program = facts_str + "\n" + threshold_facts

    ctl = clingo.Control(["0"])
    ctl.load(str(rules_path))
    ctl.add("base", [], full_program)
    ctl.ground([("base", [])])

    decisions = {}
    flags = {}
    actions = {}

    def on_model(model):
        for atom in model.symbols(shown=True):
            name = atom.name
            args = [str(a) for a in atom.arguments]
            if name == "decision":
                decisions[args[0]] = args[1]
            elif name == "flag":
                flags.setdefault(args[0], []).append(args[1])
            elif name == "action":
                actions.setdefault(args[0], []).append(args[1])

    result = ctl.solve(on_model=on_model)
    satisfiable = result.satisfiable
    return decisions, flags, actions, satisfiable


def build_row(experiment, param_name, param_value, thresholds, decisions, flags, actions, elapsed, satisfiable):
    """Build a result row dict."""
    row = {
        "experiment": experiment,
        "varied_param": param_name,
        "param_value": param_value,
        "singleton_high_bp": thresholds.get("singleton_high", ""),
        "below_k5_high_bp": thresholds.get("below_k5_high", ""),
        "homogeneous_high_bp": thresholds.get("homogeneous_high", ""),
        "solve_time_ms": round(elapsed * 1000, 1),
        "satisfiable": satisfiable,
    }
    for ds in DATASETS:
        dec = decisions.get(ds, "UNSAT" if not satisfiable else "none")
        ds_flags = sorted(flags.get(ds, []))
        ds_actions = sorted(actions.get(ds, []))
        row[f"{ds}_decision"] = dec
        row[f"{ds}_flags"] = "; ".join(ds_flags)
        row[f"{ds}_actions"] = "; ".join(ds_actions)
    return row


# ---------- Main ----------

def main():
    print("=" * 80)
    print("PUFGuard  Expanded Sensitivity Analysis  (RF-06)")
    print("=" * 80)

    base_facts = load_facts_without_thresholds(FACTS_FILE)
    all_results = []

    # ===== Part 1: One-at-a-time threshold sweeps =====
    for sweep_param, values in SWEEPS.items():
        print(f"\n{'-' * 80}")
        print(f"SWEEP: {sweep_param}")
        print(f"{'-' * 80}")
        for val in values:
            thresholds = dict(DEFAULTS)
            thresholds[sweep_param] = val
            pct = val / 100

            start = time.perf_counter()
            decisions, flags, actions, sat = run_clingo(RULES_FILE, base_facts, thresholds)
            elapsed = time.perf_counter() - start

            is_default = "(default)" if val == DEFAULTS[sweep_param] else ""
            print(f"\n  {sweep_param} = {pct:.1f}% ({val} bp) {is_default}")
            print(f"    Solve time: {elapsed*1000:.1f} ms  |  SAT: {sat}")
            for ds in DATASETS:
                dec = decisions.get(ds, "UNSAT")
                ds_flags = sorted(flags.get(ds, []))
                print(f"    {ds.upper()}: {dec:40s} flags: {', '.join(ds_flags)}")

            row = build_row(
                experiment=f"sweep_{sweep_param}",
                param_name=sweep_param,
                param_value=val,
                thresholds=thresholds,
                decisions=decisions, flags=flags, actions=actions,
                elapsed=elapsed, satisfiable=sat,
            )
            all_results.append(row)

    # ===== Part 2: Role perturbation =====
    print(f"\n{'-' * 80}")
    print("ROLE PERTURBATION TESTS")
    print(f"{'-' * 80}")

    perturbations = [
        ("remove_sensitive_d1", "sensitive(d1).",
         "Remove sensitive(D) from D1 — test whether high_attribute_disclosure flag and decision change"),
        ("remove_structural_identifier_d2", "structural_identifier(d2).",
         "Remove structural_identifier(D) from D2 — test whether restricted_review is still triggered by free_text or metrics"),
        ("remove_sensitive_d5", "sensitive(d5).",
         "Remove sensitive(D) from D5 — test whether public_candidate decision persists without sensitive role"),
    ]

    for perturb_name, fact_atom, description in perturbations:
        print(f"\n  {perturb_name}: {description}")
        perturbed_facts = remove_fact(base_facts, fact_atom)
        thresholds = dict(DEFAULTS)

        start = time.perf_counter()
        decisions, flags, actions, sat = run_clingo(RULES_FILE, perturbed_facts, thresholds)
        elapsed = time.perf_counter() - start

        print(f"    Solve time: {elapsed*1000:.1f} ms  |  SAT: {sat}")
        for ds in DATASETS:
            dec = decisions.get(ds, "UNSAT")
            ds_flags = sorted(flags.get(ds, []))
            print(f"    {ds.upper()}: {dec:40s} flags: {', '.join(ds_flags)}")

        row = build_row(
            experiment=f"perturbation",
            param_name=perturb_name,
            param_value=f"removed {fact_atom}",
            thresholds=thresholds,
            decisions=decisions, flags=flags, actions=actions,
            elapsed=elapsed, satisfiable=sat,
        )
        all_results.append(row)

    # ===== Save results =====
    fieldnames = list(all_results[0].keys())
    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_results)

    with open(OUTPUT_JSON, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\n{'=' * 80}")
    print(f"Results written to:")
    print(f"  CSV:  {OUTPUT_CSV}")
    print(f"  JSON: {OUTPUT_JSON}")

    # ===== Summary tables =====
    print(f"\n{'=' * 80}")
    print("SUMMARY TABLES")
    print(f"{'=' * 80}")

    # Table per sweep
    for sweep_param in SWEEPS:
        sweep_rows = [r for r in all_results if r["varied_param"] == sweep_param]
        print(f"\n--- Sweep: {sweep_param} ---")
        hdr = f"{'Value (bp)':>12} {'Value (%)':>10} | {'D1':>40} | {'D2':>28} | {'D3':>28} | {'D4':>28} | {'D5':>45}"
        print(hdr)
        print("-" * len(hdr))
        for r in sweep_rows:
            val = r["param_value"]
            pct = f"{val/100:.1f}%"
            d1 = r["d1_decision"]
            d2 = r["d2_decision"]
            d3 = r["d3_decision"]
            d4 = r["d4_decision"]
            d5 = r["d5_decision"]
            default_mark = " *" if val == DEFAULTS[sweep_param] else "  "
            print(f"{val:>10}{default_mark} {pct:>10} | {d1:>40} | {d2:>28} | {d3:>28} | {d4:>28} | {d5:>45}")
        print("  (* = default value)")

    # Perturbation summary
    print(f"\n--- Role Perturbation ---")
    perturb_rows = [r for r in all_results if r["experiment"] == "perturbation"]
    # Also get the baseline (default thresholds, no perturbation)
    baseline = [r for r in all_results
                if r["experiment"] == "sweep_singleton_high"
                and r["param_value"] == DEFAULTS["singleton_high"]]
    if baseline:
        print(f"  {'Condition':<40} | {'D1':>40} | {'D2':>28} | {'D3':>28} | {'D4':>28} | {'D5':>45}")
        print("  " + "-" * 220)
        b = baseline[0]
        print(f"  {'Baseline (all defaults)':<40} | {b['d1_decision']:>40} | {b['d2_decision']:>28} | {b['d3_decision']:>28} | {b['d4_decision']:>28} | {b['d5_decision']:>45}")
        for r in perturb_rows:
            label = r["varied_param"]
            print(f"  {label:<40} | {r['d1_decision']:>40} | {r['d2_decision']:>28} | {r['d3_decision']:>28} | {r['d4_decision']:>28} | {r['d5_decision']:>45}")

    # Decision stability summary
    print(f"\n--- Decision Stability Summary ---")
    for ds in DATASETS:
        col = f"{ds}_decision"
        sweep_decisions = set()
        for r in all_results:
            if r["experiment"].startswith("sweep_"):
                sweep_decisions.add(r[col])
        stable = len(sweep_decisions) == 1
        print(f"  {ds.upper()}: {'STABLE' if stable else 'VARIES'} across threshold sweeps -> {sweep_decisions}")

    print()


if __name__ == "__main__":
    main()
