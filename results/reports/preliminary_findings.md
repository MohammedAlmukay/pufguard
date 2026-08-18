# PUFGuard preliminary benchmark report

This report describes aggregate, sample-based signals. It does not claim that any person is identifiable.

## Dataset-level findings

| Dataset | Rows | Columns | Core singleton | Extended singleton | Below k=5 | Logic decision |
|---|---:|---:|---:|---:|---:|---|
| D1: BMI_Depression | 4,683 | 35 | 11.5% | 92.1% | 99.9% | remediate_before_release |
| D2: GLP1 | 513 | 38 | 13.8% | 47.2% | 76.2% | restricted_review |
| D3: Health_Message | 348 | 67 | 13.5% | 36.5% | 70.4% | restricted_review |
| D4: Employee_Attrition | 1,191 | 35 | 35.5% | 81.7% | 98.6% | restricted_review |
| D5: Driving_Employment | 901 | 43 | 0.1% | 1.3% | 5.5% | public_candidate_after_documented_review |

## Interpretation limits

- Direct identifiers and free text are structural release concerns, but their presence does not prove disclosure.
- Sample uniqueness is an upper-layer warning signal; population uniqueness requires external population information.
- The logic thresholds are research configuration values and are not legal safe-harbor thresholds.
- Results must be validated by domain and privacy experts before any release decision.
