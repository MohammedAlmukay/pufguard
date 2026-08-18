# ASP logic rulebook

## Purpose

The Answer Set Programming layer converts aggregate empirical facts into a
single explainable research recommendation per dataset. It provides traceable
policy support; it is not a legal compliance engine and does not authorize data
release.

## Files

- `logic/privacy_rules.lp`: hand-authored rules and decision precedence.
- `logic/generated_facts.lp`: generated dataset facts and thresholds.
- `configs/policy_thresholds.json`: editable benchmark thresholds.
- `src/pufguard/run_logic.py`: Clingo execution and CSV/JSON serialization.
- `results/tables/logic_model.json`: complete shown atoms for audit.

`generated_facts.lp` is overwritten by the analysis pipeline and must not be
edited manually.

## Fact vocabulary

| Predicate | Meaning |
|---|---|
| `dataset(D)` | D is a benchmark dataset. |
| `rows(D,N)` / `columns(D,N)` | Deposited dimensions after import. |
| `singleton_bp(D,P)` | Extended-scenario singleton rate in basis points. |
| `below_k5_bp(D,P)` | Extended-scenario below-k=5 rate in basis points. |
| `homogeneous_bp(D,P)` | Extended homogeneous-sensitive rate in basis points. |
| `sensitive(D)` | At least one configured sensitive variable resolved. |
| `structural_identifier(D)` | At least one configured identifier-like field resolved. |
| `free_text(D)` | At least one configured free-text field resolved. |
| `threshold(Name,T)` | Configured research boundary in basis points. |

## Derived flags

- `high_linkability`: singleton basis points meet/exceed the high threshold.
- `medium_linkability`: singleton rate is between medium and high boundaries.
- `high_small_group_exposure`: below-k=5 rate meets/exceeds its threshold.
- `high_attribute_disclosure`: homogeneous-sensitive rate meets/exceeds its threshold.
- `structural_identifier_present` and `free_text_present`: structural field flags.

Flags record why a recommendation occurred. Absence of a flag is not proof of
safety.

## Recommended actions

| Trigger | Action atom | Human interpretation |
|---|---|---|
| Structural identifier | `remove_structural_identifiers` | Exclude or transform identifier-like fields in a derived release candidate. |
| Free text | `redact_or_model_free_text` | Apply a separately approved redaction/feature protocol; do not quote raw text. |
| High linkability | `generalize_quasi_identifiers` | Test broader bins or fewer QIDs and quantify utility loss. |
| High linkability | `compare_auxiliary_knowledge` | Review whether the extended attacker knowledge is plausible. |
| High attribute exposure | `enforce_sensitive_value_diversity` | Consider diversity-oriented protections with expert review. |
| Every dataset | `document_threat_model` | Record purpose, attacker, auxiliary data, and residual risk. |

## Decision precedence

The rule program produces one of three decisions:

1. `restricted_review` has priority when a sensitive dataset contains a structural
   identifier or free text, or combines high linkability with high homogeneous
   sensitive exposure.
2. `remediate_before_release` applies when restricted review did not trigger but
   high linkability, small-group exposure, or attribute exposure did.
3. `public_candidate_after_documented_review` applies only when neither of the
   above triggers. It still requires documented human review.

Negation-as-failure in the remediation and public-candidate rules creates this
precedence. The parser writes all shown `decision`, `flag`, and `action` atoms to
`logic_model.json` so the recommendation can be reconstructed.

## Current configuration

| Threshold | Basis points | Rate |
|---|---:|---:|
| `singleton_high` | 1000 | 10% |
| `singleton_medium` | 100 | 1% |
| `below_k5_high` | 2500 | 25% |
| `homogeneous_high` | 2500 | 25% |

These values are study parameters. A publication-ready evaluation must report a
threshold sensitivity grid and obtain expert ratings of rule appropriateness and
explanation correctness.

## Current trace summary

- D1: `remediate_before_release` because of high linkability and high
  small-group exposure.
- D2: `restricted_review` because identifier-like and free-text fields are
  present, in addition to linkability/small-group flags.
- D3 and D4: `restricted_review` because identifier-like fields are present in
  configured sensitive datasets.

These statements describe the checked-in configuration and generated facts,
not an institutional release decision.

