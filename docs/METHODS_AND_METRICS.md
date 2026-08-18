# Methods and metrics reference

## Analysis unit

Each worksheet row is treated as one deposited record. The project does not
assert that a row necessarily corresponds to a unique real-world person. All
metrics are computed inside each dataset; no row-level cross-dataset linkage is
performed.

## Import and normalization

`normalized_frame` performs an analysis-only normalization:

1. non-breaking spaces are converted to ordinary spaces;
2. replacement-character artifacts and repeated whitespace are collapsed;
3. column names and string values are stripped at both ends; and
4. raw source files remain byte-for-byte unchanged.

For equivalence grouping, string QIDs are case-folded and stripped, numeric QIDs
are rounded to six decimal places, and missing QID values are represented by the
literal category `<MISSING>`. This makes missingness part of the attacker-view
scenario rather than silently dropping records.

## Variable roles

- **Direct identifier:** row/operational field that should not appear unchanged
  in a derived public release candidate.
- **Quasi-identifier (QID):** attribute that may contribute to singling out when
  combined with plausible auxiliary knowledge.
- **Sensitive:** health, psychological, employment, or outcome variable used in
  the attribute-disclosure check.
- **Free text:** unstructured response with unpredictable disclosure content.
- **Item level:** fine-grained survey response contributing to a distinctive
  response vector.
- **Other:** not selected by the present threat-model configuration.

Roles are contextual judgments in `configs/datasets.json`, not intrinsic labels.
Every assignment and its rationale appears in the data dictionary. Independent
expert review is still required before a release decision.

## QID scenarios

- **Coarse:** a reduced set intended to approximate data minimization.
- **Core:** demographics plausibly available to an ordinary attacker.
- **Extended:** additional detail representing stronger auxiliary knowledge.

Scenario membership is fixed before inspecting the uniqueness result and is
listed variable-by-variable in `data/metadata/data_dictionary.csv`. The
`qid_retention_fraction` is a structural utility proxy: number of scenario QIDs
divided by the number of extended QIDs. It is not predictive-model utility.

## Equivalence classes

For a dataset with records \(i=1,\ldots,n\) and QID set \(Q\), records belong to
the same equivalence class when their normalized values agree on every variable
in \(Q\). Let \(g(i,Q)\) be the size of record \(i\)'s class.

### Sample singleton rate

\[
U_Q = \frac{1}{n}\sum_{i=1}^{n}\mathbf{1}[g(i,Q)=1].
\]

This is sample uniqueness under the chosen QIDs. It is not population uniqueness,
match probability, or evidence that identity recovery occurred.

### Records below k=5

\[
B_{Q,5}=\frac{1}{n}\sum_{i=1}^{n}\mathbf{1}[g(i,Q)<5].
\]

The value five is a benchmark parameter. It is not presented as a statutory or
universal safe-harbor threshold.

### Minimum and median k

`minimum_k` is the smallest observed class size. `median_k` is the unweighted
median across equivalence classes, not the record-weighted median.

### Homogeneous-sensitive rate

For a configured primary sensitive variable \(S\), a non-singleton class is
flagged when it contains fewer than two normalized values of \(S\). The reported
rate is the number of records in such classes divided by all records. Singleton
classes are excluded from the numerator. Missing sensitive values are treated as
a category; therefore this is a conservative structural signal, not formal
\(l\)-diversity certification.

## Other descriptors

- `unique_rate_nonmissing`: distinct nonmissing values divided by nonmissing
  values for one column.
- `entropy_bits`: Shannon entropy after representing missing as a category.
- `item_pattern_unique_rate`: distinct rows across configured item-level columns
  divided by all records.
- `maximum_structural_identifier_uniqueness`: largest nonmissing unique rate among
  configured identifier-like columns.
- `maximum_free_text_nonempty_rate`: largest nonempty proportion among configured
  free-text columns.
- `exact_duplicate_records_involved`: number of rows belonging to any exact
  full-row duplicate group; it is not the number of duplicate groups.

The full machine-readable metric dictionary is
`data/metadata/metric_dictionary.csv`.

## Thresholds and rounding

Rates are multiplied by 10,000 and rounded to integer basis points before being
passed to ASP. The default research configuration flags:

- extended singleton rate at or above 10% as high linkability;
- 1% to below 10% as medium linkability;
- records-below-k=5 at or above 25% as high small-group exposure; and
- homogeneous-sensitive rate at or above 25% as high attribute exposure.

Thresholds are stored once in `configs/policy_thresholds.json`. Sensitivity to
alternative values must be reported before publication; current decisions are
configuration-dependent.

## Missingness, duplicates, and errors

No records are deleted and no source value is corrected. Spreadsheet error tokens
such as `#VALUE!` remain literal categories after import. Data-quality findings
identify these conditions so that any future processed layer can specify a
versioned transformation and justification.

## Interpretation hierarchy

1. A metric describes a deposited sample under a stated scenario.
2. A flag applies a configurable research threshold to that metric.
3. An ASP decision combines flags and structural field types.
4. A human reviewer considers context, purpose, population information, and
   governance requirements.
5. Only an authorized institutional process can approve a release or study.

