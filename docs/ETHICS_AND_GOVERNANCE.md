# Ethics and governance plan

## Governing principle

Public availability reduces access barriers; it does not remove duties of
respect, minimization, accurate interpretation, licence compliance, or
institutional oversight. This document is a research-governance plan, not legal
advice or an IRB determination.

## Phase 1 — Public-data software benchmark

Request a written institutional determination of whether secondary analysis of
public, de-identified records is non-human-subject research, exempt, or requires
review. Do not assume that the original investigators' approval automatically
covers this project.

Allowed before determination: aggregate profiling, software testing, threat
modeling, and manuscript drafting without identity lookup. Prohibited: contacting
participants, combining identity sources, quoting free text, or publishing rare
row examples.

## Phase 2 — Expert validation

Privacy, data-governance, and domain experts evaluate:

- variable-role assignments;
- plausibility of auxiliary-knowledge scenarios;
- correctness and usefulness of ASP explanations;
- threshold sensitivity and false reassurance; and
- whether recommended mitigations preserve research utility.

Before recruitment, document the institutional determination, consent or waiver,
eligibility, compensation, conflicts, retention, and whether expert identity is
linked to ratings.

## Phase 3 — CAP-Data user study

Obtain prospective approval and informed consent. Use synthetic Saudi-context
profiles or ephemeral participant-selected attributes. Do not expose raw corpus
records. Collect only treatment assignment, task response, comprehension,
decision time, and pre-specified optional covariates. Separate consent must govern
optional demographics and retention.

## Phase 4 — ReproLogic evaluation

The unit of analysis is a paper-data package, not a person. Apparent disagreement
may result from version mismatch, rounding, weighting, undocumented exclusions,
or depositor error. Contact depositors privately before a public discrepancy
claim and never infer misconduct from an automated result.

## Phase 5 — Policy-aware PPRL

Ground-truth linkage must come from synthetic data or explicitly authorized
benchmark pairs. The public corpus may inform marginal distributions only. Live
identity linkage and incremental disclosure about real respondents are outside
scope.

## Governance roles

| Role | Minimum responsibility |
|---|---|
| Principal investigator | Approves scope, ethics submissions, release, and reporting. |
| Data steward | Maintains access list, hashes, storage, and retention actions. |
| Lead analyst | Runs versioned code and records configuration/output hashes. |
| Privacy reviewer | Reviews QIDs, sensitive fields, threat model, and mitigations. |
| Domain reviewer | Confirms semantic definitions and substantive interpretation. |
| Human-study coordinator | Manages consent, recruitment, compensation, and participant data. |

One person may hold multiple roles, but approval and independent review should be
separated where practicable.

## Reporting safeguards

- report dataset/scenario aggregates;
- do not show raw rows or free-text excerpts;
- suppress or avoid small subgroup tables in manuscripts;
- label sample uniqueness and configuration-dependent decisions accurately;
- cite original datasets and related papers;
- disclose unresolved coding and rounding issues;
- distinguish implemented results from future protocols; and
- include funding, conflicts, author contributions, ethics determination, and
  AI/tool-use disclosure required by the target venue.

## Stop conditions

Pause work and notify the PI/data steward if:

- a generated output unexpectedly contains row values or free text;
- a checksum changes without an authorized source-version update;
- a new dataset includes names, contact details, precise locations, or files not
  covered by the stated licence;
- a participant or depositor requests action requiring institutional review; or
- a planned experiment expands from synthetic/aggregate analysis to real identity
  linkage.

Use `IRB_READINESS_CHECKLIST.md` to record the actual institutional outcome.

