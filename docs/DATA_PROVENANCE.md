# Data provenance and integrity

## Corpus scope

The corpus contains five openly deposited Saudi-context survey datasets. They
were selected as a heterogeneous software benchmark spanning health, mental
health, health communication, and employment. Selection does not make the
corpus statistically representative of Saudi Arabia or of all public-use data.

## D1 — BMI and depression

- Repository: https://data.mendeley.com/datasets/wrwtvtppgd/1
- DOI/version: 10.17632/wrwtvtppgd.1, version 1
- Related article: https://doi.org/10.1371/journal.pone.0293799
- Local input: `data/raw/D1_BMI_Depression/Data.xlsx`
- Licence recorded by repository: CC BY 4.0
- Deposited analytic dimensions: 4,683 rows, 35 columns
- Repository description supports demographics, self-reported height/weight,
  BMI, chronic disease, smoking, and 21 BDI-II items scored 0–3 with a 0–63 sum.

## D2 — GLP-1 knowledge, attitudes, and treatment experience

- Repository: https://data.mendeley.com/datasets/y7rbxs53g9/1
- DOI/version: 10.17632/y7rbxs53g9.1, version 1
- Local input: `data/raw/D2_GLP1/Raw_data_GLPI_weight_mgmt.xlsx`
- Licence recorded by repository: CC BY 4.0
- Deposited dimensions: 513 rows, 38 columns
- Full survey questions are used as most column headers. The file contains a
  record-unique timestamp, operational researcher code, free text, and literal
  spreadsheet-error tokens. The project does not repeat free-text contents.

## D3 — Health message framing

- Repository: https://data.mendeley.com/datasets/2v8k7kk9vt/1
- DOI/version: 10.17632/2v8k7kk9vt.1, version 1
- Related article: https://doi.org/10.31470/2309-1797-2021-29-1-30-58
- Local input: `data/raw/D3_Health_Message/Dataset.xlsx`
- Licence recorded by repository: CC BY 4.0
- Deposited dimensions: 348 rows, 67 columns
- The repository and article support the constructs: demographics, depression,
  state anxiety, and 1–6 affect ratings for gain/loss, less/more severe, and
  desirable/undesirable message frames.
- The local workbook does not include a complete numeric code-to-label map for
  demographics or item-to-question mapping. These gaps are not filled by
  inference in the dictionary.

## D4 — Saudi employee attrition

- Repository: https://data.mendeley.com/datasets/6z2hty8php/1
- DOI/version: 10.17632/6z2hty8php.1, version 1
- Local inputs: the main XLSX plus `Dataset_Keys.docx` and
  `Online_Survey_Questions.docx`
- Licence recorded by repository: CC BY 4.0
- Deposited analytic dimensions: 1,191 rows, 35 columns
- Variable meanings come from the bilingual survey document; encoding guidance
  comes from `Dataset_Keys.docx`. The allowance field's single numeric code is
  still marked for depositor confirmation.

## Integrity controls

Every raw file has a current byte size and SHA-256 digest in
`data/metadata/integrity_manifest.csv`. Standard checksum lines are in
`data/metadata/checksums.sha256`. The verification date establishes the current
project baseline.

The initial download dates were not recorded. This is represented as
`not_recorded`; file-system timestamps are not treated as evidence of retrieval.

## Transformation lineage

Raw files are never overwritten. Import normalization occurs in memory. Current
processed outputs are aggregate profiles only. Any future row-level processed
layer must have:

1. a new versioned path outside `data/raw/`;
2. a deterministic transformation script;
3. before/after row and column counts;
4. a variable-level change log; and
5. an ethics and licence review before sharing.

## Citation rule

An article using the corpus must cite each dataset it analyzes, not merely this
project. Repository URLs and DOIs should be retained in the methods supplement.

