"""Adversarial tests for PUFGuard fail-closed ASP policy.

These tests verify that the ASP program:
1. Rejects incomplete profiles (no stable model)
2. Restricts direct identifiers and free text independently of sensitive
3. Produces exactly one decision per dataset
4. Handles borderline threshold values correctly
"""

import unittest
from pathlib import Path

import clingo

RULES_FILE = Path(__file__).resolve().parents[1] / "logic" / "privacy_rules.lp"


def solve(extra_facts: str) -> list[str]:
    """Run the ASP program with extra facts and return shown atoms, or None if UNSAT."""
    ctl = clingo.Control(["0"])
    ctl.load(str(RULES_FILE))
    ctl.add("base", [], extra_facts)
    ctl.ground([("base", [])])

    results = []
    with ctl.solve(yield_=True) as handle:
        for model in handle:
            results.append(sorted(str(s) for s in model.symbols(shown=True)))
    return results


def get_decision(atoms: list[str], dataset: str = "d_test") -> str | None:
    """Extract the decision for a dataset from shown atoms."""
    for atom in atoms:
        if atom.startswith(f"decision({dataset},"):
            return atom.split(",", 1)[1].rstrip(")")
    return None


# Standard thresholds used in all tests
THRESHOLDS = (
    "threshold(singleton_high,1000). "
    "threshold(singleton_medium,100). "
    "threshold(below_k5_high,2500). "
    "threshold(homogeneous_high,2500)."
)

# A complete, non-restricted profile (low risk, no identifiers)
COMPLETE_LOW_RISK = (
    f"{THRESHOLDS} "
    "dataset(d_test). "
    "singleton_bp(d_test,50). "      # 0.5% — below medium
    "below_k5_bp(d_test,500). "      # 5% — below threshold
    "homogeneous_bp(d_test,100)."     # 1% — below threshold
)


class TestFailClosed(unittest.TestCase):
    """Test that the ASP policy fails closed on incomplete or adversarial inputs."""

    def test_dataset_fact_only_is_unsatisfiable(self):
        """RF-02 case 1: dataset fact with no metrics → no stable model."""
        facts = f"{THRESHOLDS} dataset(d_test)."
        results = solve(facts)
        self.assertEqual(len(results), 0, "Should be UNSAT when metric facts are missing")

    def test_missing_singleton_bp_is_unsatisfiable(self):
        """RF-02 case 4: missing singleton_bp → no stable model."""
        facts = (
            f"{THRESHOLDS} "
            "dataset(d_test). "
            "below_k5_bp(d_test,5000). "
            "homogeneous_bp(d_test,100)."
        )
        results = solve(facts)
        self.assertEqual(len(results), 0, "Should be UNSAT when singleton_bp is missing")

    def test_missing_below_k5_bp_is_unsatisfiable(self):
        """RF-02 case 4: missing below_k5_bp → no stable model."""
        facts = (
            f"{THRESHOLDS} "
            "dataset(d_test). "
            "singleton_bp(d_test,5000). "
            "homogeneous_bp(d_test,100)."
        )
        results = solve(facts)
        self.assertEqual(len(results), 0, "Should be UNSAT when below_k5_bp is missing")

    def test_missing_homogeneous_bp_is_unsatisfiable(self):
        """RF-02 case 4: missing homogeneous_bp → no stable model."""
        facts = (
            f"{THRESHOLDS} "
            "dataset(d_test). "
            "singleton_bp(d_test,5000). "
            "below_k5_bp(d_test,5000)."
        )
        results = solve(facts)
        self.assertEqual(len(results), 0, "Should be UNSAT when homogeneous_bp is missing")

    def test_structural_identifier_without_sensitive_triggers_restricted(self):
        """RF-02 case 2: structural_identifier without sensitive(D) → restricted_review."""
        facts = (
            f"{COMPLETE_LOW_RISK} "
            "structural_identifier(d_test)."
            # No sensitive(d_test).
        )
        results = solve(facts)
        self.assertEqual(len(results), 1, "Should produce exactly one stable model")
        decision = get_decision(results[0])
        self.assertEqual(decision, "restricted_review",
                         "Direct identifier must trigger restricted_review even without sensitive")

    def test_free_text_without_sensitive_triggers_restricted(self):
        """RF-02 case 3: free_text without sensitive(D) → restricted_review."""
        facts = (
            f"{COMPLETE_LOW_RISK} "
            "free_text(d_test)."
            # No sensitive(d_test).
        )
        results = solve(facts)
        self.assertEqual(len(results), 1, "Should produce exactly one stable model")
        decision = get_decision(results[0])
        self.assertEqual(decision, "restricted_review",
                         "Free text must trigger restricted_review even without sensitive")

    def test_complete_low_risk_is_public_candidate(self):
        """A complete profile with all metrics below threshold → public_candidate."""
        results = solve(COMPLETE_LOW_RISK)
        self.assertEqual(len(results), 1, "Should produce exactly one stable model")
        decision = get_decision(results[0])
        self.assertEqual(decision, "public_candidate_after_documented_review")

    def test_exactly_one_decision_per_dataset(self):
        """RF-02 case 6: integrity constraint ensures mutual exclusivity."""
        # High risk profile that triggers remediation
        facts = (
            f"{THRESHOLDS} "
            "dataset(d_test). "
            "singleton_bp(d_test,5000). "   # 50% — high
            "below_k5_bp(d_test,5000). "    # 50% — high
            "homogeneous_bp(d_test,100)."    # 1% — low
        )
        results = solve(facts)
        self.assertEqual(len(results), 1)
        decisions = [a for a in results[0] if a.startswith("decision(d_test,")]
        self.assertEqual(len(decisions), 1, "Exactly one decision per dataset")

    def test_borderline_at_singleton_threshold(self):
        """RF-02 case 5: singleton rate exactly at 10% threshold → high_linkability."""
        facts = (
            f"{THRESHOLDS} "
            "dataset(d_test). "
            "singleton_bp(d_test,1000). "    # Exactly 10% — at threshold
            "below_k5_bp(d_test,500). "      # Below threshold
            "homogeneous_bp(d_test,100)."
        )
        results = solve(facts)
        self.assertEqual(len(results), 1)
        decision = get_decision(results[0])
        self.assertEqual(decision, "remediate_before_release",
                         "Singleton at threshold (>=) should trigger high_linkability → remediation")

    def test_borderline_just_below_singleton_threshold(self):
        """RF-02 case 5: singleton rate at 999 bp (9.99%) → medium, not high."""
        facts = (
            f"{THRESHOLDS} "
            "dataset(d_test). "
            "singleton_bp(d_test,999). "     # Just below 10%
            "below_k5_bp(d_test,500). "
            "homogeneous_bp(d_test,100)."
        )
        results = solve(facts)
        self.assertEqual(len(results), 1)
        decision = get_decision(results[0])
        self.assertEqual(decision, "public_candidate_after_documented_review",
                         "Singleton just below threshold should not trigger remediation")

    def test_multiple_datasets_each_get_one_decision(self):
        """Two datasets with different profiles each get exactly one decision."""
        facts = (
            f"{THRESHOLDS} "
            "dataset(d1). singleton_bp(d1,9000). below_k5_bp(d1,9000). homogeneous_bp(d1,50). "
            "dataset(d2). singleton_bp(d2,50). below_k5_bp(d2,200). homogeneous_bp(d2,50). "
            "structural_identifier(d2)."
        )
        results = solve(facts)
        self.assertEqual(len(results), 1)
        d1_dec = get_decision(results[0], "d1")
        d2_dec = get_decision(results[0], "d2")
        self.assertEqual(d1_dec, "remediate_before_release")
        self.assertEqual(d2_dec, "restricted_review")


    # --- RF5-04: Input-validation constraint tests ---

    def test_duplicate_metric_value_is_unsatisfiable(self):
        """Duplicate singleton_bp values for same dataset → UNSAT."""
        facts = (
            f"{THRESHOLDS} "
            "dataset(d_test). "
            "singleton_bp(d_test,500). singleton_bp(d_test,600). "
            "below_k5_bp(d_test,500). "
            "homogeneous_bp(d_test,100)."
        )
        results = solve(facts)
        self.assertEqual(len(results), 0, "Duplicate metric values should be UNSAT")

    def test_duplicate_threshold_value_is_unsatisfiable(self):
        """Duplicate threshold for same parameter → UNSAT."""
        facts = (
            "threshold(singleton_high,1000). threshold(singleton_high,2000). "
            "threshold(singleton_medium,100). "
            "threshold(below_k5_high,2500). "
            "threshold(homogeneous_high,2500). "
            "dataset(d_test). "
            "singleton_bp(d_test,500). "
            "below_k5_bp(d_test,500). "
            "homogeneous_bp(d_test,100)."
        )
        results = solve(facts)
        self.assertEqual(len(results), 0, "Duplicate threshold values should be UNSAT")

    def test_invalid_threshold_ordering_is_unsatisfiable(self):
        """singleton_medium >= singleton_high → UNSAT."""
        facts = (
            "threshold(singleton_high,100). "
            "threshold(singleton_medium,200). "  # medium > high — invalid
            "threshold(below_k5_high,2500). "
            "threshold(homogeneous_high,2500). "
            "dataset(d_test). "
            "singleton_bp(d_test,500). "
            "below_k5_bp(d_test,500). "
            "homogeneous_bp(d_test,100)."
        )
        results = solve(facts)
        self.assertEqual(len(results), 0, "Invalid threshold ordering should be UNSAT")

    # --- RF5-06: high_attribute_disclosure requires sensitive ---

    def test_high_homogeneous_without_sensitive_no_remediation(self):
        """High homogeneous_bp without sensitive(D) should NOT trigger remediation."""
        facts = (
            f"{THRESHOLDS} "
            "dataset(d_test). "
            "singleton_bp(d_test,50). "       # Low — no linkability
            "below_k5_bp(d_test,200). "       # Low — no small group
            "homogeneous_bp(d_test,5000)."     # 50% — would be high, but no sensitive
            # No sensitive(d_test).
        )
        results = solve(facts)
        self.assertEqual(len(results), 1)
        decision = get_decision(results[0])
        self.assertEqual(decision, "public_candidate_after_documented_review",
                         "High homogeneous without sensitive should not trigger remediation")


if __name__ == "__main__":
    unittest.main()
