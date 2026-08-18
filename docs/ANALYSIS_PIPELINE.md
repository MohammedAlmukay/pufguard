# Analysis pipeline and file lineage

## End-to-end flow

| Stage | Inputs | Producer | Outputs |
|---|---|---|---|
| Corpus profiling | Raw XLSX files, `configs/datasets.json`, thresholds | `analyze_corpus.py` | Dataset/column/scenario CSVs, SVG, LaTeX macros, ASP facts |
| Logic reasoning | `privacy_rules.lp`, `generated_facts.lp` | `run_logic.py` | `logic_decisions.csv`, `logic_model.json` |
| Narrative report | Profiles and logic decisions | `build_report.py` | `preliminary_findings.md` |
| Documentation metadata | Raw files, configs, semantic annotations | `generate_documentation.py` | Dictionary, quality audit, checksums, manifest, coverage docs |
| Verification | Source functions and generated metadata | `unittest` suite | Pass/fail console record |

## Detailed products

### `analyze_corpus.py`

- `results/tables/dataset_privacy_profiles.csv`: dataset dimensions and
  aggregate privacy descriptors.
- `data/processed/dataset_level_profiles.csv`: synchronized aggregate copy for
  data-oriented workflows.
- `results/tables/column_inventory.csv`: column completeness, cardinality,
  unique rate, entropy, and configured role.
- `results/tables/privacy_utility_scenarios.csv`: coarse/core/extended QID
  scenario results.
- `logic/generated_facts.lp`: integer basis-point facts for ASP.
- `results/figures/singleton_rates.svg`: aggregate extended-scenario chart.
- `results/tables/paper1_macros.tex` and `paper1_profile_rows.tex`: generated
  LaTeX values used by the lead paper.

### `run_logic.py`

- `logic_decisions.csv`: one decision, flag list, and action list per dataset.
- `logic_model.json`: shown ASP atoms plus serialized decision rows.

### `build_report.py`

- `results/reports/preliminary_findings.md`: aggregate results and mandatory
  interpretation limits.

### `generate_documentation.py`

- `data_dictionary.csv` and `DATA_DICTIONARY.md`.
- `data_quality_findings.csv` and `DATA_QUALITY.md`.
- `integrity_manifest.csv` and `checksums.sha256`.
- `metric_dictionary.csv` and `DOCUMENTATION_COVERAGE.md`.

## Immutability and overwrite policy

Only generated outputs listed above are overwritten by `run_all.ps1`. Raw XLSX
and DOCX files are read-only inputs. Hand-authored governance documents,
`privacy_rules.lp`, `datasets.json`, and `semantic_annotations.json` are not
generated and require normal version review.

## Failure behavior

`run_all.ps1` checks the native exit code after every stage and throws on the
first failure. Tests execute from the project root so package imports are stable.
Partial outputs from a failed run should not be interpreted as a complete result;
rerun after correcting the error and retain the console log for publication
reproduction.

