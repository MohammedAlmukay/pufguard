"""Conventional Python rule engine implementing the same policy semantics as
PUFGuard's 39-rule ASP program.

This baseline is designed to be fair and competent:
- Same three decision classes.
- Same input facts.
- Reports ALL applicable reasons, not only the first match.
- Explicit input validation (rejects malformed profiles).
- Comparable trace mechanism (flags + actions).
- Comparable automated tests.

Used for head-to-head comparison with the ASP implementation.
"""

from dataclasses import dataclass, field


@dataclass
class PolicyTrace:
    """Complete trace of a policy evaluation."""
    decision: str | None = None
    flags: list[str] = field(default_factory=list)
    actions: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)
    valid: bool = True
    validation_errors: list[str] = field(default_factory=list)


def validate_inputs(
    singleton_bp: int | None,
    below_k5_bp: int | None,
    homogeneous_bp: int | None,
    thresholds: dict,
) -> list[str]:
    """Validate inputs. Return list of errors (empty = valid)."""
    errors = []

    if singleton_bp is None:
        errors.append("missing singleton_bp")
    if below_k5_bp is None:
        errors.append("missing below_k5_bp")
    if homogeneous_bp is None:
        errors.append("missing homogeneous_bp")

    required_thresholds = [
        "singleton_high", "singleton_medium",
        "below_k5_high", "homogeneous_high"
    ]
    for t in required_thresholds:
        if t not in thresholds:
            errors.append(f"missing threshold: {t}")

    if "singleton_medium" in thresholds and "singleton_high" in thresholds:
        if thresholds["singleton_medium"] >= thresholds["singleton_high"]:
            errors.append(
                f"invalid threshold ordering: singleton_medium "
                f"({thresholds['singleton_medium']}) >= singleton_high "
                f"({thresholds['singleton_high']})"
            )

    return errors


def evaluate_policy(
    singleton_bp: int | None,
    below_k5_bp: int | None,
    homogeneous_bp: int | None,
    sensitive: bool = False,
    structural_identifier: bool = False,
    free_text: bool = False,
    thresholds: dict | None = None,
) -> PolicyTrace:
    """Evaluate the disclosure-risk policy and return a complete trace.

    Returns a PolicyTrace with decision, flags, actions, reasons, and
    validation status. Returns decision=None and valid=False if inputs
    are malformed.
    """
    if thresholds is None:
        thresholds = {
            "singleton_high": 1000,
            "singleton_medium": 100,
            "below_k5_high": 2500,
            "homogeneous_high": 2500,
        }

    trace = PolicyTrace()

    # Input validation (fail-closed)
    errors = validate_inputs(singleton_bp, below_k5_bp, homogeneous_bp, thresholds)
    if errors:
        trace.valid = False
        trace.validation_errors = errors
        return trace

    # Stratum 1: Risk-level classification
    s_high = thresholds["singleton_high"]
    s_med = thresholds["singleton_medium"]
    b_high = thresholds["below_k5_high"]
    h_high = thresholds["homogeneous_high"]

    high_linkability = singleton_bp >= s_high
    medium_linkability = s_med <= singleton_bp < s_high
    high_small_group = below_k5_bp >= b_high
    high_attribute = sensitive and homogeneous_bp >= h_high

    # Stratum 2: Flag generation
    if structural_identifier:
        trace.flags.append("structural_identifier_present")
    if free_text:
        trace.flags.append("free_text_present")
    if high_linkability:
        trace.flags.append("high_linkability")
    if medium_linkability:
        trace.flags.append("medium_linkability")
    if high_small_group:
        trace.flags.append("high_small_group_exposure")
    if high_attribute:
        trace.flags.append("high_attribute_disclosure")

    # Stratum 3: Recommended actions
    if structural_identifier:
        trace.actions.append("remove_structural_identifiers")
    if free_text:
        trace.actions.append("redact_or_model_free_text")
    if high_linkability:
        trace.actions.append("generalize_quasi_identifiers")
        trace.actions.append("compare_auxiliary_knowledge")
    if high_attribute:
        trace.actions.append("enforce_sensitive_value_diversity")
    trace.actions.append("document_threat_model")  # universal action

    # Stratum 4: Decision synthesis with precedence
    is_restricted = False

    if structural_identifier:
        is_restricted = True
        trace.reasons.append("structural_identifier triggers restricted_review")
    if free_text:
        is_restricted = True
        trace.reasons.append("free_text triggers restricted_review")
    if sensitive and high_linkability and high_attribute:
        is_restricted = True
        trace.reasons.append(
            "sensitive + high_linkability + high_attribute_disclosure "
            "triggers restricted_review"
        )

    if is_restricted:
        trace.decision = "restricted_review"
        return trace

    needs_remediation = False

    if high_linkability:
        needs_remediation = True
        trace.reasons.append("high_linkability triggers remediation")
    if high_small_group:
        needs_remediation = True
        trace.reasons.append("high_small_group_exposure triggers remediation")
    if high_attribute:
        needs_remediation = True
        trace.reasons.append("high_attribute_disclosure triggers remediation")

    if needs_remediation:
        trace.decision = "remediate_before_release"
        return trace

    trace.decision = "public_candidate_after_documented_review"
    trace.reasons.append(
        "no restriction or remediation triggered; public candidate by default"
    )
    return trace
