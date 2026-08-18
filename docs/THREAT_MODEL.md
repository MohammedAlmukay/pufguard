# Threat model

## Objective

Assess structural linkability and attribute-disclosure signals in deposited
samples without attempting identity recovery. The protected interest is the
privacy and dignity of respondents represented by the files.

## Protected entities and assets

- survey respondents and employees represented by records;
- health, psychological, employment, and treatment-experience attributes;
- free-text comments and unusual response patterns;
- dataset integrity, licence metadata, and institutional trust; and
- researchers who could be harmed by overclaiming or unsafe disclosure.

## Release surface

The benchmark considers a hypothetical derived public-use table assembled from
selected columns. It does not assume the deposited file is currently safe or
unsafe. Risk depends on fields retained, population knowledge, purpose, access,
and controls.

## Adversary models

1. **Prosecutor-style attacker:** knows a target appears in the dataset and knows
   some QID values.
2. **Journalist-style attacker:** searches for any unusual record without a
   predetermined target.
3. **Attribute-inference attacker:** seeks a sensitive attribute from a
   homogeneous QID class without requiring an exact identity match.
4. **Cross-dataset attacker:** combines public demographic categories or summary
   knowledge across datasets.
5. **Insider or accidental discloser:** has legitimate file access but exports
   identifier-like fields, free text, or small cells unintentionally.

## Attacker capabilities

The extended QID scenario assumes stronger knowledge than the core scenario but
does not define a real external registry. The attacker can normalize categories,
observe missingness, and compare exact QID tuples. The benchmark does not grant
access to names, phone numbers, private institutional systems, or illegal data.

## Attack paths considered

- singling out from a unique or small equivalence class;
- learning a sensitive value from a homogeneous non-singleton class;
- recognizing an identifier-like field or record-unique timestamp;
- extracting identity clues from free text;
- fingerprinting a respondent through a fine-grained item-response vector; and
- increasing uniqueness by combining additional auxiliary attributes.

## Explicit exclusions

- name lookup, contact attempts, social-media searches, or live identity recovery;
- publication of raw rows, rare text excerpts, or small-cell examples;
- population-uniqueness estimation without an external population model;
- claims that sample uniqueness equals successful re-identification;
- real-world record linkage in Paper 4; and
- automated authorization of a data release.

## Controls implemented

- aggregate-only reporting;
- suppression of free-text and identifier values in generated documentation;
- immutable raw-source policy and SHA-256 manifest;
- configurable QID sets with coarse/core/extended scenarios;
- separate empirical metrics and normative ASP thresholds;
- rule traces containing flags, decisions, and recommended actions;
- explicit semantic uncertainty labels; and
- ethics and expert-validation gates.

## Residual risks

- QID selection may omit auxiliary knowledge available to a real attacker.
- Sample metrics may overstate or understate population risk.
- Category normalization may merge distinctions or treat missingness too simply.
- A public repository licence does not guarantee that every deposited variable
  is ethically suitable for redistribution.
- Logic thresholds are unvalidated study parameters.
- Documentation itself can create risk if it enumerates rare text; therefore
  the generated dictionary suppresses free-text and identifier contents.

## Review questions before a release decision

1. What exact release purpose and minimum fields are required?
2. Which auxiliary information is realistically available?
3. Are QID and sensitive roles independently reviewed?
4. How do risk signals change under alternative generalization and thresholds?
5. Does analytical utility remain adequate after mitigation?
6. Are licence, IRB, privacy-law, and institutional requirements satisfied?
7. Who approves the decision and where is the rationale recorded?

