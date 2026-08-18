# Data quality and semantic audit

This audit describes source-file conditions; it does not edit raw data and does not label participants.
The detailed machine-readable findings are in `data/metadata/data_quality_findings.csv`.

## Finding counts

| Dataset | Information | Warning | High |
|---|---:|---:|---:|
| D1 | 2 | 0 | 0 |
| D2 | 3 | 11 | 3 |
| D3 | 0 | 28 | 1 |
| D4 | 32 | 1 | 1 |
| D5 | 1 | 51 | 0 |

## Material findings

- D1 contains a small number of exact duplicate rows; the raw file is preserved and no deduplication is performed.
- D2 contains record-unique timestamps, an operational researcher code, free text, literal spreadsheet-error tokens, and translated category labels requiring clarification.
- D3 contains a participant ID and several coded demographic variables without a local code-to-label map. Aggregate Gain/Loss fields show a small deposited rounding discrepancy (maximum 0.05) relative to visible components.
- D4 contains a participant ID and extensive whitespace/category variants. The included Word files support most semantic definitions, but the numeric allowance code still requires confirmation.

## Handling rule

All normalization occurs in memory for analysis. Corrections belong in a versioned processed-data layer with an explicit transformation log; they must never overwrite `data/raw/`.
