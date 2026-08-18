# Validation and testing plan

## Validation layers

### 1. File integrity

- SHA-256 for all six raw files.
- Expected row/column dimensions checked after import.
- Source files remain unchanged after a full run.

### 2. Unit tests

The test suite covers normalization, QID availability, equivalence-class sizes,
singleton and below-k rates, homogeneous-sensitive counts, entropy, atom parsing,
decision-row construction, report formatting, semantic coverage, and checksum
format. Run with `run_all.ps1` or:

```powershell
python -m unittest discover -s tests -v
```

### 3. Integration checks

- Five profile rows and fifteen scenario rows.
- Five mutually exclusive logic decisions.
- All configured QIDs resolve to deposited columns unless explicitly documented.
- Dictionary contains exactly the 218 deposited variables.
- Free-text and direct-identifier contents do not appear in the dictionary.
- Seven raw files appear in the integrity manifest.

### 4. Spreadsheet verification

- All sheets have descriptive names, filters, frozen headers, and typed rates.
- Formulas contain no `#REF!`, `#DIV/0!`, `#VALUE!`, `#NAME?`, or unintended
  circular references.
- Dashboard KPIs reconcile to source sheets.
- A visual pass checks clipping, chart placement, and readable wrapped text.

### 5. Manuscript verification

- Generated LaTeX macros match profile CSV values.
- Paper 1 labels findings as preliminary/sample-based.
- Papers 2–4 contain no participant or algorithm results before execution.
- References, dataset DOIs, ethics statements, and contribution boundaries are
  checked before submission.

## Independent human validation required

Automated tests cannot validate privacy appropriateness. Before publication,
obtain at least:

- two independent privacy/data-governance reviews of roles and logic outputs;
- one domain review per dataset for semantic definitions and sensitive outcomes;
- adjudication of disagreements with reasons retained;
- explanation-correctness ratings against the actual ASP trace; and
- threshold sensitivity analysis across pre-specified alternatives.

## Acceptance criteria for Paper 1

1. No unresolved identifier or free-text content in public outputs.
2. Every variable has a documented role, semantic status, and source.
3. Exact environment and source hashes archived.
4. All automated tests pass from a clean Python 3.12 environment.
5. Expert validation and ethics determination recorded.
6. Results reproduce from the frozen manifest.
7. Claims do not equate sample uniqueness with re-identification.

## Known test limitations

- Current tests use small synthetic fixtures and the five-source integration
  corpus; they do not estimate population risk.
- They do not test every Excel/TeX renderer.
- They do not replace code review, privacy review, or IRB oversight.
- D3 missing code labels and D4 allowance coding require depositor confirmation.

