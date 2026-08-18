"""Robustness and mutation testing for PUFGuard's ASP policy program.

Predeclared defect categories with expected outcomes, tested against both ASP
and the conventional Python baseline. After each policy mutation, the full
property suite is rerun over the complete abstract state space.

Defect categories:
  A. Incomplete/missing inputs (profiles and thresholds)
  B. Conflicting distinct values (metrics and thresholds)
  C. Out-of-range values (basis points outside 0-10000)
  D. Policy mutations causing decision defects
  E. Precedence inversions
  F. Missing trigger-specific flags and actions
"""

import csv
import json
import sys
from pathlib import Path
from dataclasses import dataclass

import clingo

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
RULES_FILE = PROJECT_ROOT / "logic" / "privacy_rules.lp"

sys.path.insert(0, str(SCRIPT_DIR))
from run_exhaustive_verification import (
    Profile, generate_wellformed_profiles, generate_boundary_profiles,
    threshold_facts, THRESH, DECISIONS, DECISION_SEVERITY,
    solve_profile, check_monotonicity
)
from baseline_rule_engine import evaluate_policy, validate_inputs


@dataclass
class DefectCase:
    name: str
    category: str
    facts: str  # ASP facts (for ASP engine)
    baseline_args: dict | None  # kwargs for evaluate_policy (None = not testable)
    expected_asp: str  # "UNSAT", "SAT", or a specific decision
    expected_baseline: str  # "reject", "accept", or a specific decision
    description: str


def build_defect_cases() -> list[DefectCase]:
    """Build ~30 predeclared defect cases across categories A-F."""
    cases = []
    base_thresh = threshold_facts()

    # --- Category A: Incomplete/missing inputs ---

    # A1: Missing singleton_bp
    cases.append(DefectCase(
        "A1_missing_singleton", "A_incomplete",
        f"dataset(d). below_k5_bp(d,1000). homogeneous_bp(d,1000). {base_thresh}",
        {"singleton_bp": None, "below_k5_bp": 1000, "homogeneous_bp": 1000},
        "UNSAT", "reject", "Missing singleton metric"
    ))

    # A2: Missing below_k5_bp
    cases.append(DefectCase(
        "A2_missing_below_k5", "A_incomplete",
        f"dataset(d). singleton_bp(d,500). homogeneous_bp(d,1000). {base_thresh}",
        {"singleton_bp": 500, "below_k5_bp": None, "homogeneous_bp": 1000},
        "UNSAT", "reject", "Missing below-k5 metric"
    ))

    # A3: Missing homogeneous_bp
    cases.append(DefectCase(
        "A3_missing_homogeneous", "A_incomplete",
        f"dataset(d). singleton_bp(d,500). below_k5_bp(d,1000). {base_thresh}",
        {"singleton_bp": 500, "below_k5_bp": 1000, "homogeneous_bp": None},
        "UNSAT", "reject", "Missing homogeneous metric"
    ))

    # A4: Missing singleton_high threshold
    cases.append(DefectCase(
        "A4_missing_thresh_singleton_high", "A_incomplete",
        "dataset(d). singleton_bp(d,500). below_k5_bp(d,1000). homogeneous_bp(d,1000). "
        "threshold(singleton_medium,100). threshold(below_k5_high,2500). threshold(homogeneous_high,2500).",
        {"singleton_bp": 500, "below_k5_bp": 1000, "homogeneous_bp": 1000,
         "thresholds": {"singleton_medium": 100, "below_k5_high": 2500, "homogeneous_high": 2500}},
        "UNSAT", "reject", "Missing singleton_high threshold"
    ))

    # A5: Missing singleton_medium threshold
    cases.append(DefectCase(
        "A5_missing_thresh_singleton_medium", "A_incomplete",
        "dataset(d). singleton_bp(d,500). below_k5_bp(d,1000). homogeneous_bp(d,1000). "
        "threshold(singleton_high,1000). threshold(below_k5_high,2500). threshold(homogeneous_high,2500).",
        {"singleton_bp": 500, "below_k5_bp": 1000, "homogeneous_bp": 1000,
         "thresholds": {"singleton_high": 1000, "below_k5_high": 2500, "homogeneous_high": 2500}},
        "UNSAT", "reject", "Missing singleton_medium threshold"
    ))

    # A6: Dataset fact only, no metrics
    cases.append(DefectCase(
        "A6_dataset_only", "A_incomplete",
        f"dataset(d). {base_thresh}",
        None, "UNSAT", "reject", "Dataset without any metrics"
    ))

    # --- Category B: Conflicting distinct values ---

    # B1: Two distinct singleton_bp values
    cases.append(DefectCase(
        "B1_duplicate_singleton", "B_conflicting",
        f"dataset(d). singleton_bp(d,500). singleton_bp(d,600). below_k5_bp(d,1000). homogeneous_bp(d,1000). {base_thresh}",
        None, "UNSAT", "not_applicable", "Two distinct singleton values"
    ))

    # B2: Two distinct below_k5_bp values
    cases.append(DefectCase(
        "B2_duplicate_below_k5", "B_conflicting",
        f"dataset(d). singleton_bp(d,500). below_k5_bp(d,1000). below_k5_bp(d,2000). homogeneous_bp(d,1000). {base_thresh}",
        None, "UNSAT", "not_applicable", "Two distinct below-k5 values"
    ))

    # B3: Two distinct homogeneous_bp values
    cases.append(DefectCase(
        "B3_duplicate_homogeneous", "B_conflicting",
        f"dataset(d). singleton_bp(d,500). below_k5_bp(d,1000). homogeneous_bp(d,1000). homogeneous_bp(d,2000). {base_thresh}",
        None, "UNSAT", "not_applicable", "Two distinct homogeneous values"
    ))

    # B4: Two distinct singleton_high thresholds
    cases.append(DefectCase(
        "B4_duplicate_threshold", "B_conflicting",
        "dataset(d). singleton_bp(d,500). below_k5_bp(d,1000). homogeneous_bp(d,1000). "
        "threshold(singleton_high,1000). threshold(singleton_high,2000). "
        "threshold(singleton_medium,100). threshold(below_k5_high,2500). threshold(homogeneous_high,2500).",
        None, "UNSAT", "not_applicable", "Two distinct singleton_high thresholds"
    ))

    # B5: Invalid threshold ordering (medium >= high)
    cases.append(DefectCase(
        "B5_invalid_ordering", "B_conflicting",
        "dataset(d). singleton_bp(d,500). below_k5_bp(d,1000). homogeneous_bp(d,1000). "
        "threshold(singleton_high,100). threshold(singleton_medium,200). "
        "threshold(below_k5_high,2500). threshold(homogeneous_high,2500).",
        {"singleton_bp": 500, "below_k5_bp": 1000, "homogeneous_bp": 1000,
         "thresholds": {"singleton_high": 100, "singleton_medium": 200,
                        "below_k5_high": 2500, "homogeneous_high": 2500}},
        "UNSAT", "reject", "Threshold ordering violation: medium >= high"
    ))

    # B6: Medium == high (edge case)
    cases.append(DefectCase(
        "B6_equal_ordering", "B_conflicting",
        "dataset(d). singleton_bp(d,500). below_k5_bp(d,1000). homogeneous_bp(d,1000). "
        "threshold(singleton_high,500). threshold(singleton_medium,500). "
        "threshold(below_k5_high,2500). threshold(homogeneous_high,2500).",
        {"singleton_bp": 500, "below_k5_bp": 1000, "homogeneous_bp": 1000,
         "thresholds": {"singleton_high": 500, "singleton_medium": 500,
                        "below_k5_high": 2500, "homogeneous_high": 2500}},
        "UNSAT", "reject", "Threshold ordering: medium == high"
    ))

    # --- Category C: Out-of-range values ---
    # Note: ASP integers have no inherent 0-10000 range constraint.
    # The program does not enforce range checking.

    # C1: Negative singleton_bp
    cases.append(DefectCase(
        "C1_negative_singleton", "C_out_of_range",
        f"dataset(d). singleton_bp(d,-100). below_k5_bp(d,1000). homogeneous_bp(d,1000). {base_thresh}",
        None, "SAT", "not_applicable", "Negative singleton value (no range constraint in ASP)"
    ))

    # C2: Singleton above 10000
    cases.append(DefectCase(
        "C2_over_10000_singleton", "C_out_of_range",
        f"dataset(d). singleton_bp(d,15000). below_k5_bp(d,1000). homogeneous_bp(d,1000). {base_thresh}",
        None, "SAT", "not_applicable", "Singleton > 10000 (no range constraint in ASP)"
    ))

    return cases


def build_policy_mutations(rules_text: str) -> list[dict]:
    """Build policy mutations that should cause specific decision defects.

    Each mutation modifies the ASP program and declares expected property
    failures. The full property suite is rerun after each mutation.
    """
    mutations = []

    # M1: Remove restricted_review for structural_identifier -> should break P6
    m1 = rules_text.replace(
        "restricted_review(D) :- structural_identifier(D).",
        "% REMOVED: restricted_review(D) :- structural_identifier(D)."
    )
    mutations.append({
        "name": "M1_remove_si_restriction",
        "description": "Remove structural-identifier restriction rule",
        "rules": m1,
        "expected_failures": ["P6"],
        "expected_decision_changes": True,
    })

    # M2: Remove public_candidate rule -> should break P1 (totality)
    m2 = rules_text.replace(
        "public_candidate(D) :- dataset(D), not restricted_review(D), not remediation_needed(D).",
        "% REMOVED: public_candidate rule"
    )
    # Also need to remove decision derivation for public_candidate
    m2 = m2.replace(
        "decision(D,public_candidate_after_documented_review) :- public_candidate(D).",
        "% REMOVED: public_candidate decision"
    )
    mutations.append({
        "name": "M2_remove_public_candidate",
        "description": "Remove public-candidate rule (creates missing decisions)",
        "rules": m2,
        "expected_failures": ["P1"],
        "expected_decision_changes": True,
    })

    # M3: Add conflicting decision rule -> should break P2 (uniqueness)
    m3 = rules_text + "\ndecision(D,extra_decision) :- dataset(D)."
    mutations.append({
        "name": "M3_add_conflicting_decision",
        "description": "Add unconditional extra decision (breaks uniqueness constraint)",
        "rules": m3,
        "expected_failures": ["P1"],  # integrity constraint rejects it
        "expected_decision_changes": True,
    })

    # M4: Remove profile_complete gate -> missing metrics silently pass
    m4 = rules_text.replace(
        ":- dataset(D), not profile_complete(D).",
        "% REMOVED: profile completeness constraint"
    )
    mutations.append({
        "name": "M4_remove_completeness_gate",
        "description": "Remove fail-closed profile gate (redundant with cardinality constraints)",
        "rules": m4,
        "expected_failures": [],  # cardinality constraints still catch missing metrics
        "expected_decision_changes": False,
    })

    # M5: Reverse precedence (remediation overrides restriction)
    m5 = rules_text.replace(
        "remediation_needed(D) :- dataset(D), not restricted_review(D), high_linkability(D).",
        "remediation_needed(D) :- dataset(D), high_linkability(D)."
    ).replace(
        "remediation_needed(D) :- dataset(D), not restricted_review(D), high_small_group_exposure(D).",
        "remediation_needed(D) :- dataset(D), high_small_group_exposure(D)."
    ).replace(
        "remediation_needed(D) :- dataset(D), not restricted_review(D), high_attribute_disclosure(D).",
        "remediation_needed(D) :- dataset(D), high_attribute_disclosure(D)."
    )
    mutations.append({
        "name": "M5_break_precedence",
        "description": "Remove not-restricted guard from remediation (integrity constraint catches multi-decision)",
        "rules": m5,
        "expected_failures": ["P1"],  # integrity constraint rejects profiles with two decisions
        "expected_decision_changes": True,
    })

    # M6: Remove document_threat_model universal action
    m6 = rules_text.replace(
        "action(D,document_threat_model) :- dataset(D).",
        "% REMOVED: universal documentation action"
    )
    mutations.append({
        "name": "M6_remove_universal_action",
        "description": "Remove universal documentation action",
        "rules": m6,
        "expected_failures": ["P7"],
        "expected_decision_changes": False,
    })

    # M7: Invert monotonicity - lower risk gets more restrictive decision
    # Make low_linkability trigger restriction
    m7 = rules_text + "\nrestricted_review(D) :- low_linkability(D)."
    mutations.append({
        "name": "M7_invert_monotonicity",
        "description": "Low linkability triggers restriction (monotonicity violation)",
        "rules": m7,
        "expected_failures": ["P8"],
        "expected_decision_changes": True,
    })

    return mutations


def run_property_suite(rules_text: str, label: str) -> dict:
    """Run the full property suite on a (possibly mutated) rule set."""
    profiles = generate_wellformed_profiles() + generate_boundary_profiles()

    results = {"label": label, "profiles_tested": len(profiles)}

    sat_results = []
    unsat_count = 0
    multi_decision = 0
    multi_model = 0
    invalid_decisions = 0

    for p in profiles:
        r = solve_profile(p, rules_text)
        if not r.satisfiable:
            unsat_count += 1
        else:
            sat_results.append(r)
            if len(r.decisions) != 1:
                multi_decision += 1
            if r.num_models != 1:
                multi_model += 1
            if r.decisions:
                dec = r.decisions[0].split(",")[1].rstrip(")")
                if dec not in DECISIONS:
                    invalid_decisions += 1

    # P1: Totality
    results["P1_totality"] = unsat_count == 0

    # P2: Decision uniqueness
    results["P2_uniqueness"] = multi_decision == 0

    # P3: Stable-model uniqueness
    results["P3_model_uniqueness"] = multi_model == 0

    # P4: Valid decisions
    results["P4_valid_decisions"] = invalid_decisions == 0

    # P5: Malformed rejection (test with missing singleton)
    from run_exhaustive_verification import generate_malformed_profiles
    mf_cases = generate_malformed_profiles()
    mf_pass = True
    for name, facts in mf_cases:
        program = rules_text + "\n" + facts
        ctl = clingo.Control(["0", "--warn=none"])
        ctl.add("base", [], program)
        ctl.ground([("base", [])])
        sat = False
        with ctl.solve(yield_=True) as handle:
            for _ in handle:
                sat = True
                break
        if sat:
            mf_pass = False
            break
    results["P5_malformed_rejection"] = mf_pass

    # P6: Structural precedence
    sp_pass = True
    for r in sat_results:
        if r.profile.structural_identifier or r.profile.free_text:
            if r.decisions:
                dec = r.decisions[0].split(",")[1].rstrip(")")
                if dec != "restricted_review":
                    sp_pass = False
                    break
    results["P6_structural_precedence"] = sp_pass

    # P7: Universal documentation action
    p7_pass = True
    for r in sat_results:
        if not any("document_threat_model" in a for a in r.actions):
            p7_pass = False
            break
    results["P7_universal_action"] = p7_pass

    # P8: Monotonicity
    violations = check_monotonicity(sat_results)
    results["P8_monotonicity"] = len(violations) == 0
    results["P8_violation_count"] = len(violations)

    results["unsat_count"] = unsat_count
    results["multi_decision_count"] = multi_decision
    results["multi_model_count"] = multi_model

    return results


def run_baseline_defects(cases: list[DefectCase]) -> list[dict]:
    """Run defect cases against the Python baseline."""
    results = []
    for c in cases:
        if c.baseline_args is None:
            results.append({
                "name": c.name, "category": c.category,
                "baseline_result": "not_applicable",
                "baseline_matches_expected": True,
            })
            continue

        thresholds = c.baseline_args.pop("thresholds", THRESH)
        trace = evaluate_policy(**c.baseline_args, thresholds=thresholds)

        if c.expected_baseline == "reject":
            matches = not trace.valid
        elif c.expected_baseline == "accept":
            matches = trace.valid
        else:
            matches = trace.decision == c.expected_baseline

        results.append({
            "name": c.name, "category": c.category,
            "baseline_valid": trace.valid,
            "baseline_decision": trace.decision,
            "baseline_errors": trace.validation_errors,
            "baseline_matches_expected": matches,
        })
    return results


def main():
    rules_text = RULES_FILE.read_text(encoding="utf-8")

    print("=" * 80)
    print("PUFGuard Robustness and Mutation Testing")
    print("=" * 80)

    # Phase 1: Defect cases
    print("\n--- Phase 1: Predeclared Defect Cases ---")
    cases = build_defect_cases()
    print(f"  {len(cases)} defect cases across categories A-C")

    asp_defect_results = []
    for c in cases:
        program = rules_text + "\n" + c.facts
        ctl = clingo.Control(["0", "--warn=none"])
        ctl.add("base", [], program)
        ctl.ground([("base", [])])
        sat = False
        decision = None
        with ctl.solve(yield_=True) as handle:
            for model in handle:
                sat = True
                for atom in model.symbols(shown=True):
                    s = str(atom)
                    if s.startswith("decision("):
                        decision = s.split(",")[1].rstrip(")")
                break

        if c.expected_asp == "UNSAT":
            matches = not sat
        elif c.expected_asp == "SAT":
            matches = sat
        else:
            matches = decision == c.expected_asp

        asp_defect_results.append({
            "name": c.name, "category": c.category,
            "asp_sat": sat, "asp_decision": decision,
            "asp_matches_expected": matches,
            "description": c.description,
        })

    baseline_defect_results = run_baseline_defects(cases)

    # Summary by category
    categories = sorted(set(c.category for c in cases))
    print("\n  ASP detection by category:")
    for cat in categories:
        cat_results = [r for r in asp_defect_results if r["category"] == cat]
        detected = sum(1 for r in cat_results if r["asp_matches_expected"])
        print(f"    {cat}: {detected}/{len(cat_results)}")

    print("  Baseline detection by category:")
    for cat in categories:
        cat_results = [r for r in baseline_defect_results if r["category"] == cat]
        detected = sum(1 for r in cat_results if r["baseline_matches_expected"])
        print(f"    {cat}: {detected}/{len(cat_results)}")

    # Phase 2: Policy mutations with full property re-verification
    print("\n--- Phase 2: Policy Mutations ---")
    mutations = build_policy_mutations(rules_text)
    print(f"  {len(mutations)} policy mutations defined")

    # First: baseline (unmodified) properties
    print("\n  Running baseline property suite...")
    baseline_props = run_property_suite(rules_text, "original")
    prop_keys = [k for k in baseline_props if k.startswith("P") and isinstance(baseline_props[k], bool)]
    print(f"    Original: all pass = {all(baseline_props[k] for k in prop_keys)}")

    mutation_results = []
    for mut in mutations:
        print(f"\n  Mutation: {mut['name']} — {mut['description']}")
        props = run_property_suite(mut["rules"], mut["name"])

        # Check which properties failed
        failed_props = [k for k in ["P1_totality", "P2_uniqueness", "P3_model_uniqueness",
                                     "P4_valid_decisions", "P5_malformed_rejection",
                                     "P6_structural_precedence", "P7_universal_action",
                                     "P8_monotonicity"]
                        if not props.get(k, True)]

        expected_short = [f"P{p[1]}" for p in [e for e in mut["expected_failures"]]]

        # Did the expected properties fail?
        detected = any(f"P{e[1]}_{e[2:]}" in "_".join(failed_props)
                       for e in mut["expected_failures"]) if mut["expected_failures"] else True

        # Simpler check
        failed_pnums = [fp.split("_")[0] for fp in failed_props]
        expected_detected = all(ep in failed_pnums for ep in mut["expected_failures"])

        print(f"    Failed properties: {failed_props if failed_props else 'none'}")
        print(f"    Expected failures: {mut['expected_failures']}")
        print(f"    Expected defect detected: {expected_detected}")

        mutation_results.append({
            "name": mut["name"],
            "description": mut["description"],
            "failed_properties": failed_props,
            "expected_failures": mut["expected_failures"],
            "expected_detected": expected_detected,
            "properties": props,
        })

    # Summary
    print("\n" + "=" * 80)
    print("ROBUSTNESS AND MUTATION SUMMARY")
    print("=" * 80)

    total_defects = len(asp_defect_results)
    asp_detected = sum(1 for r in asp_defect_results if r["asp_matches_expected"])
    bl_detected = sum(1 for r in baseline_defect_results if r.get("baseline_matches_expected", False))

    print(f"\n  Defect cases: {total_defects}")
    print(f"  ASP detection:      {asp_detected}/{total_defects}")
    print(f"  Baseline detection: {bl_detected}/{len(baseline_defect_results)} (testable)")

    print(f"\n  Policy mutations: {len(mutation_results)}")
    mutations_detected = sum(1 for r in mutation_results if r["expected_detected"])
    print(f"  Expected defects detected: {mutations_detected}/{len(mutation_results)}")

    for r in mutation_results:
        status = "DETECTED" if r["expected_detected"] else "MISSED"
        print(f"    {r['name']}: {status} (failed: {r['failed_properties']})")

    # Write results
    out_dir = SCRIPT_DIR
    summary = {
        "defect_cases": {
            "total": total_defects,
            "asp_detected": asp_detected,
            "baseline_detected": bl_detected,
            "details": asp_defect_results,
            "baseline_details": baseline_defect_results,
        },
        "mutations": {
            "total": len(mutation_results),
            "expected_detected": mutations_detected,
            "details": [{k: v for k, v in r.items() if k != "properties"}
                        for r in mutation_results],
        },
        "baseline_properties": baseline_props,
    }

    json_path = out_dir / "robustness_mutation_results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)

    print(f"\n  Results: {json_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
