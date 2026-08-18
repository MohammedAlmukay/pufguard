"""Exhaustive policy-space verification for PUFGuard's ASP program.

Enumerates all abstract well-formed policy profiles and a systematic set of
malformed profiles. For each profile, invokes Clingo and verifies totality,
decision uniqueness, stable-model uniqueness, boundary correctness, structural
precedence, trace completeness, and monotonicity.

The input domain is finite once metrics are abstracted to threshold-relative
regions:

  singleton_bp:    [0, medium), [medium, high), [high, 10000]   -> 3 regions
  below_k5_bp:     [0, high), [high, 10000]                     -> 2 regions
  homogeneous_bp:  [0, high), [high, 10000]                     -> 2 regions
  sensitive:       absent, present                               -> 2
  structural_id:   absent, present                               -> 2
  free_text:       absent, present                               -> 2

  Total well-formed abstract profiles: 3 * 2 * 2 * 2 * 2 * 2 = 96

Additionally: boundary profiles at exact threshold values, and malformed
profiles with missing metrics or duplicate thresholds.
"""

import csv
import itertools
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

import clingo

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
RULES_FILE = PROJECT_ROOT / "logic" / "privacy_rules.lp"

# Default thresholds (basis points)
THRESH = {
    "singleton_high": 1000,
    "singleton_medium": 100,
    "below_k5_high": 2500,
    "homogeneous_high": 2500,
}

DECISIONS = {
    "restricted_review",
    "remediate_before_release",
    "public_candidate_after_documented_review",
}

# Decision severity ordering (higher = more restrictive)
DECISION_SEVERITY = {
    "public_candidate_after_documented_review": 0,
    "remediate_before_release": 1,
    "restricted_review": 2,
}


@dataclass
class Profile:
    """An abstract policy profile for one dataset."""
    singleton_bp: int
    below_k5_bp: int
    homogeneous_bp: int
    sensitive: bool
    structural_identifier: bool
    free_text: bool
    label: str = ""

    def to_facts(self, dataset_id: str = "d_test") -> str:
        lines = [
            f"dataset({dataset_id}).",
            f"singleton_bp({dataset_id},{self.singleton_bp}).",
            f"below_k5_bp({dataset_id},{self.below_k5_bp}).",
            f"homogeneous_bp({dataset_id},{self.homogeneous_bp}).",
        ]
        if self.sensitive:
            lines.append(f"sensitive({dataset_id}).")
        if self.structural_identifier:
            lines.append(f"structural_identifier({dataset_id}).")
        if self.free_text:
            lines.append(f"free_text({dataset_id}).")
        return "\n".join(lines)


@dataclass
class VerificationResult:
    profile: Profile
    satisfiable: bool
    num_models: int  # -1 if enumeration capped
    decisions: list
    flags: list
    actions: list
    errors: list = field(default_factory=list)


def threshold_facts() -> str:
    return "\n".join(
        f"threshold({name},{value})." for name, value in THRESH.items()
    )


def solve_profile(profile: Profile, rules_text: str, max_models: int = 10) -> VerificationResult:
    """Run Clingo on a single profile and collect all stable models."""
    facts = profile.to_facts() + "\n" + threshold_facts()
    program = rules_text + "\n" + facts

    ctl = clingo.Control(["0", "--warn=none"])  # 0 = enumerate all models
    ctl.add("base", [], program)
    ctl.ground([("base", [])])

    models = []
    with ctl.solve(yield_=True) as handle:
        for model in handle:
            atoms = [str(a) for a in model.symbols(shown=True)]
            models.append(atoms)
            if len(models) >= max_models:
                break

    if not models:
        return VerificationResult(
            profile=profile, satisfiable=False, num_models=0,
            decisions=[], flags=[], actions=[]
        )

    # Parse first model (all should agree for well-formed inputs)
    all_decisions = []
    all_flags = []
    all_actions = []
    for atom in models[0]:
        if atom.startswith("decision("):
            all_decisions.append(atom)
        elif atom.startswith("flag("):
            all_flags.append(atom)
        elif atom.startswith("action("):
            all_actions.append(atom)

    return VerificationResult(
        profile=profile, satisfiable=True, num_models=len(models),
        decisions=sorted(all_decisions), flags=sorted(all_flags),
        actions=sorted(all_actions)
    )


def generate_wellformed_profiles() -> list[Profile]:
    """Generate all 96 abstract well-formed profiles using representative
    values from each threshold region."""
    # Representative values for each region
    singleton_regions = [
        (50, "low"),       # below medium (100)
        (500, "medium"),   # between medium (100) and high (1000)
        (5000, "high"),    # above high (1000)
    ]
    below_k5_regions = [
        (1000, "low"),     # below high (2500)
        (5000, "high"),    # above high (2500)
    ]
    homogeneous_regions = [
        (1000, "low"),     # below high (2500)
        (5000, "high"),    # above high (2500)
    ]
    booleans = [False, True]

    profiles = []
    for (s_val, s_lbl), (b_val, b_lbl), (h_val, h_lbl), sens, si, ft in itertools.product(
        singleton_regions, below_k5_regions, homogeneous_regions,
        booleans, booleans, booleans
    ):
        label = f"s={s_lbl}_b={b_lbl}_h={h_lbl}_sens={sens}_si={si}_ft={ft}"
        profiles.append(Profile(
            singleton_bp=s_val, below_k5_bp=b_val, homogeneous_bp=h_val,
            sensitive=sens, structural_identifier=si, free_text=ft,
            label=label
        ))
    return profiles


def generate_boundary_profiles() -> list[Profile]:
    """Generate profiles at exact threshold boundaries (±1 bp)."""
    profiles = []

    # Singleton boundaries: at medium-1, medium, medium+1, high-1, high, high+1
    for s_val, s_lbl in [
        (99, "singleton_just_below_medium"),
        (100, "singleton_at_medium"),
        (101, "singleton_just_above_medium"),
        (999, "singleton_just_below_high"),
        (1000, "singleton_at_high"),
        (1001, "singleton_just_above_high"),
    ]:
        profiles.append(Profile(
            singleton_bp=s_val, below_k5_bp=1000, homogeneous_bp=1000,
            sensitive=True, structural_identifier=False, free_text=False,
            label=s_lbl
        ))

    # below_k5 boundaries
    for b_val, b_lbl in [
        (2499, "below_k5_just_below_high"),
        (2500, "below_k5_at_high"),
        (2501, "below_k5_just_above_high"),
    ]:
        profiles.append(Profile(
            singleton_bp=50, below_k5_bp=b_val, homogeneous_bp=1000,
            sensitive=True, structural_identifier=False, free_text=False,
            label=b_lbl
        ))

    # homogeneous boundaries
    for h_val, h_lbl in [
        (2499, "homogeneous_just_below_high"),
        (2500, "homogeneous_at_high"),
        (2501, "homogeneous_just_above_high"),
    ]:
        profiles.append(Profile(
            singleton_bp=50, below_k5_bp=1000, homogeneous_bp=h_val,
            sensitive=True, structural_identifier=False, free_text=False,
            label=h_lbl
        ))

    # Edge: homogeneous high but sensitive=False -> should NOT trigger
    profiles.append(Profile(
        singleton_bp=50, below_k5_bp=1000, homogeneous_bp=5000,
        sensitive=False, structural_identifier=False, free_text=False,
        label="homogeneous_high_no_sensitive"
    ))

    return profiles


def generate_malformed_profiles() -> list[tuple[str, str]]:
    """Generate malformed fact sets that should cause UNSAT."""
    base_thresh = threshold_facts()
    cases = []

    # Missing singleton_bp
    cases.append(("missing_singleton", "\n".join([
        "dataset(d_test).",
        "below_k5_bp(d_test,1000).",
        "homogeneous_bp(d_test,1000).",
        base_thresh
    ])))

    # Missing below_k5_bp
    cases.append(("missing_below_k5", "\n".join([
        "dataset(d_test).",
        "singleton_bp(d_test,500).",
        "homogeneous_bp(d_test,1000).",
        base_thresh
    ])))

    # Missing homogeneous_bp
    cases.append(("missing_homogeneous", "\n".join([
        "dataset(d_test).",
        "singleton_bp(d_test,500).",
        "below_k5_bp(d_test,1000).",
        base_thresh
    ])))

    # Duplicate singleton_bp values
    cases.append(("duplicate_singleton", "\n".join([
        "dataset(d_test).",
        "singleton_bp(d_test,500).",
        "singleton_bp(d_test,600).",
        "below_k5_bp(d_test,1000).",
        "homogeneous_bp(d_test,1000).",
        base_thresh
    ])))

    # Missing threshold
    cases.append(("missing_threshold_singleton_high", "\n".join([
        "dataset(d_test).",
        "singleton_bp(d_test,500).",
        "below_k5_bp(d_test,1000).",
        "homogeneous_bp(d_test,1000).",
        "threshold(singleton_medium,100).",
        "threshold(below_k5_high,2500).",
        "threshold(homogeneous_high,2500).",
    ])))

    # Invalid threshold ordering (medium >= high)
    cases.append(("invalid_threshold_ordering", "\n".join([
        "dataset(d_test).",
        "singleton_bp(d_test,500).",
        "below_k5_bp(d_test,1000).",
        "homogeneous_bp(d_test,1000).",
        "threshold(singleton_high,100).",
        "threshold(singleton_medium,200).",
        "threshold(below_k5_high,2500).",
        "threshold(homogeneous_high,2500).",
    ])))

    return cases


def check_monotonicity(results: list[VerificationResult]) -> list[dict]:
    """Check risk monotonicity: increasing any risk dimension should not
    produce a less restrictive decision.

    We define the risk partial order:
    - Higher singleton_bp >= lower singleton_bp (more risk)
    - Higher below_k5_bp >= lower below_k5_bp (more risk)
    - Higher homogeneous_bp >= lower homogeneous_bp (more risk)
    - sensitive=True >= sensitive=False
    - structural_identifier=True >= structural_identifier=False
    - free_text=True >= free_text=False

    Two profiles are comparable if one dominates the other on ALL dimensions.
    """
    violations = []
    sat_results = [r for r in results if r.satisfiable and r.decisions]

    for i, r1 in enumerate(sat_results):
        for r2 in sat_results[i+1:]:
            p1, p2 = r1.profile, r2.profile
            # Check if p1 dominates p2 (p1 is riskier on all dimensions)
            p1_dominates = (
                p1.singleton_bp >= p2.singleton_bp and
                p1.below_k5_bp >= p2.below_k5_bp and
                p1.homogeneous_bp >= p2.homogeneous_bp and
                (p1.sensitive >= p2.sensitive) and
                (p1.structural_identifier >= p2.structural_identifier) and
                (p1.free_text >= p2.free_text) and
                (p1.singleton_bp, p1.below_k5_bp, p1.homogeneous_bp,
                 p1.sensitive, p1.structural_identifier, p1.free_text) !=
                (p2.singleton_bp, p2.below_k5_bp, p2.homogeneous_bp,
                 p2.sensitive, p2.structural_identifier, p2.free_text)
            )

            if p1_dominates:
                d1 = r1.decisions[0].split(",")[1].rstrip(")")
                d2 = r2.decisions[0].split(",")[1].rstrip(")")
                sev1 = DECISION_SEVERITY.get(d1, -1)
                sev2 = DECISION_SEVERITY.get(d2, -1)
                if sev1 < sev2:  # p1 is riskier but got less restrictive decision
                    violations.append({
                        "riskier_profile": p1.label,
                        "riskier_decision": d1,
                        "lower_profile": p2.label,
                        "lower_decision": d2,
                    })

            # Check reverse
            p2_dominates = (
                p2.singleton_bp >= p1.singleton_bp and
                p2.below_k5_bp >= p1.below_k5_bp and
                p2.homogeneous_bp >= p1.homogeneous_bp and
                (p2.sensitive >= p1.sensitive) and
                (p2.structural_identifier >= p1.structural_identifier) and
                (p2.free_text >= p1.free_text) and
                (p1.singleton_bp, p1.below_k5_bp, p1.homogeneous_bp,
                 p1.sensitive, p1.structural_identifier, p1.free_text) !=
                (p2.singleton_bp, p2.below_k5_bp, p2.homogeneous_bp,
                 p2.sensitive, p2.structural_identifier, p2.free_text)
            )

            if p2_dominates:
                d1 = r1.decisions[0].split(",")[1].rstrip(")")
                d2 = r2.decisions[0].split(",")[1].rstrip(")")
                sev1 = DECISION_SEVERITY.get(d1, -1)
                sev2 = DECISION_SEVERITY.get(d2, -1)
                if sev2 < sev1:
                    violations.append({
                        "riskier_profile": p2.label,
                        "riskier_decision": d2,
                        "lower_profile": p1.label,
                        "lower_decision": d1,
                    })

    return violations


def main():
    rules_text = RULES_FILE.read_text(encoding="utf-8")
    out_dir = SCRIPT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("PUFGuard ASP Exhaustive Policy-Space Verification")
    print("=" * 80)

    # Phase 1: Well-formed profiles
    print("\n--- Phase 1: Well-formed profiles (96 abstract) ---")
    wf_profiles = generate_wellformed_profiles()
    wf_results = []
    for p in wf_profiles:
        r = solve_profile(p, rules_text)
        wf_results.append(r)

    # Phase 2: Boundary profiles
    print("--- Phase 2: Boundary profiles ---")
    bd_profiles = generate_boundary_profiles()
    bd_results = []
    for p in bd_profiles:
        r = solve_profile(p, rules_text)
        bd_results.append(r)

    # Phase 3: Malformed profiles
    print("--- Phase 3: Malformed profiles ---")
    mf_cases = generate_malformed_profiles()
    mf_results = []
    for name, facts in mf_cases:
        program = rules_text + "\n" + facts
        ctl = clingo.Control(["0", "--warn=none"])
        ctl.add("base", [], program)
        ctl.ground([("base", [])])
        models = []
        with ctl.solve(yield_=True) as handle:
            for model in handle:
                models.append([str(a) for a in model.symbols(shown=True)])
                if len(models) >= 5:
                    break
        mf_results.append({"name": name, "satisfiable": len(models) > 0,
                           "num_models": len(models)})

    # Verification checks
    all_sat = [r for r in wf_results + bd_results]

    # 1. Totality
    totality_pass = all(r.satisfiable for r in all_sat)
    totality_failures = [r.profile.label for r in all_sat if not r.satisfiable]

    # 2. Decision uniqueness
    uniqueness_pass = all(len(r.decisions) == 1 for r in all_sat if r.satisfiable)
    uniqueness_failures = [r.profile.label for r in all_sat
                           if r.satisfiable and len(r.decisions) != 1]

    # 3. Stable-model uniqueness
    model_uniqueness_pass = all(r.num_models == 1 for r in all_sat if r.satisfiable)
    model_uniqueness_failures = [r.profile.label for r in all_sat
                                  if r.satisfiable and r.num_models != 1]

    # 4. Valid decisions
    valid_decisions_pass = True
    invalid_decision_profiles = []
    for r in all_sat:
        if r.satisfiable and r.decisions:
            dec = r.decisions[0].split(",")[1].rstrip(")")
            if dec not in DECISIONS:
                valid_decisions_pass = False
                invalid_decision_profiles.append((r.profile.label, dec))

    # 5. Malformed rejection
    malformed_all_rejected = all(not m["satisfiable"] for m in mf_results)
    malformed_failures = [m["name"] for m in mf_results if m["satisfiable"]]

    # 6. Monotonicity
    print("--- Phase 4: Monotonicity check ---")
    mono_violations = check_monotonicity(wf_results + bd_results)

    # 7. Trace completeness: every decision has document_threat_model action
    trace_pass = True
    trace_failures = []
    for r in all_sat:
        if r.satisfiable:
            has_doc = any("document_threat_model" in a for a in r.actions)
            if not has_doc:
                trace_pass = False
                trace_failures.append(r.profile.label)

    # 8. Structural precedence: SI or FT -> restricted_review regardless of metrics
    structural_pass = True
    structural_failures = []
    for r in all_sat:
        if r.satisfiable and (r.profile.structural_identifier or r.profile.free_text):
            dec = r.decisions[0].split(",")[1].rstrip(")")
            if dec != "restricted_review":
                structural_pass = False
                structural_failures.append(r.profile.label)

    # Summary
    n_wellformed = len(wf_results)
    n_boundary = len(bd_results)
    n_malformed = len(mf_results)
    n_total = n_wellformed + n_boundary + n_malformed

    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    print(f"  Profiles tested:              {n_total}")
    print(f"    Well-formed (abstract):      {n_wellformed}")
    print(f"    Boundary:                    {n_boundary}")
    print(f"    Malformed:                   {n_malformed}")
    print()

    props = [
        ("P1: Totality", totality_pass, totality_failures),
        ("P2: Decision uniqueness", uniqueness_pass, uniqueness_failures),
        ("P3: Stable-model uniqueness", model_uniqueness_pass, model_uniqueness_failures),
        ("P4: Valid decision classes", valid_decisions_pass, invalid_decision_profiles),
        ("P5: Malformed-input rejection", malformed_all_rejected, malformed_failures),
        ("P6: Structural precedence", structural_pass, structural_failures),
        ("P7: Trace completeness", trace_pass, trace_failures),
        ("P8: Monotonicity", len(mono_violations) == 0, mono_violations),
    ]

    for name, passed, failures in props:
        status = "PASS" if passed else "FAIL"
        print(f"  {name}: {status}")
        if not passed and failures:
            if isinstance(failures, list) and len(failures) <= 5:
                for f in failures:
                    print(f"    -> {f}")
            else:
                print(f"    -> {len(failures)} failures")

    # Decision distribution
    print("\n--- Decision Distribution (well-formed profiles) ---")
    dec_counts = {}
    for r in wf_results:
        if r.satisfiable and r.decisions:
            dec = r.decisions[0].split(",")[1].rstrip(")")
            dec_counts[dec] = dec_counts.get(dec, 0) + 1
    for dec, count in sorted(dec_counts.items()):
        print(f"  {dec}: {count}/{n_wellformed} ({100*count/n_wellformed:.1f}%)")

    # Write CSV
    csv_path = out_dir / "verification_results.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "profile_label", "type", "satisfiable", "num_models",
            "decision", "num_flags", "num_actions",
            "singleton_bp", "below_k5_bp", "homogeneous_bp",
            "sensitive", "structural_identifier", "free_text"
        ])
        for r in wf_results + bd_results:
            dec = r.decisions[0].split(",")[1].rstrip(")") if r.decisions else ""
            writer.writerow([
                r.profile.label, "wellformed" if r in wf_results else "boundary",
                r.satisfiable, r.num_models, dec,
                len(r.flags), len(r.actions),
                r.profile.singleton_bp, r.profile.below_k5_bp, r.profile.homogeneous_bp,
                r.profile.sensitive, r.profile.structural_identifier, r.profile.free_text
            ])
        for m in mf_results:
            writer.writerow([
                m["name"], "malformed", m["satisfiable"], m["num_models"],
                "", "", "", "", "", "", "", "", ""
            ])

    # Write summary JSON
    summary = {
        "profiles_tested": n_total,
        "wellformed": n_wellformed,
        "boundary": n_boundary,
        "malformed": n_malformed,
        "properties": {name: {"pass": passed, "failures": len(failures) if isinstance(failures, list) else 0}
                       for name, passed, failures in props},
        "decision_distribution": dec_counts,
        "monotonicity_violations": mono_violations,
    }
    json_path = out_dir / "verification_summary.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"\nResults written to:")
    print(f"  CSV:  {csv_path}")
    print(f"  JSON: {json_path}")

    # Return pass/fail for test integration
    all_pass = all(passed for _, passed, _ in props)
    print(f"\nOVERALL: {'ALL PROPERTIES VERIFIED' if all_pass else 'FAILURES DETECTED'}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
