# PUFGuard

PUFGuard reads a public-use survey file and checks it for disclosure risk. It
measures how many records stand out as unique or nearly unique, looks for direct
identifiers and free-text fields, and then runs a small set of logic rules that
sort the file into one of three outcomes: it looks ready for release, it needs
cleaning first, or it needs a restricted review. Every decision comes with the
rules and the numbers that produced it.

This is a research prototype. It works on aggregate risk signals only. It does
not identify anyone, and it must never be used to link or re-identify real
people.

We test it on five public Saudi survey datasets.

## What is in this repository

- `src/pufguard/` — the pipeline. It reads the file, computes the risk signals,
  runs the rules, and writes the report.
- `logic/` — the policy rules (`privacy_rules.lp`) and the facts generated for
  the five datasets.
- `configs/` — which columns count as quasi-identifiers, the thresholds, and the
  sensitive fields.
- `experiments/` — the checks reported in the paper: the sdcMicro cross-check,
  the ARX-equivalent risk measures, the exhaustive rule verification, the
  robustness and mutation tests, and the post-cleanup re-assessment.
- `results/tables/` — the numbers the paper reports, in machine-readable form,
  with `output_checksums.csv`.
- `tests/` — the automated test suite.
- `docs/` — the methods, the rule book, the threat model, ethics, and the
  reproduction notes.

## Get the data first

This archive does not include the survey files. They belong to their original
authors and stay on their own repositories. Download the five files from the
DOIs below into `data/raw/`, using the paths in
`data/metadata/integrity_manifest.csv`, then check their SHA-256 hashes against
that file. All five are CC BY 4.0.

| Dataset | DOI |
|---|---|
| D1 | 10.17632/wrwtvtppgd.1 |
| D2 | 10.17632/y7rbxs53g9.1 |
| D3 | 10.17632/2v8k7kk9vt.1 |
| D4 | 10.17632/6z2hty8php.1 |
| D5 | 10.5281/zenodo.21839927 |

`data/metadata/dataset_lineage.csv` lists the raw and analytic size of each file
and the one filter the pipeline applies, which is dropping rows that are blank in
every column.

## Run it

The exact toolchain is recorded in `docs/ENVIRONMENT.md` (Python 3.14.0,
pandas 3.0.3, clingo 5.8.1, with all pins in `requirements-lock.txt`). Running
the pipeline on it reproduces `results/tables/paper1_macros.tex` byte-for-byte.

```powershell
python -m pip install -r requirements-lock.txt
./run_all.ps1
```

The pipeline reads `data/raw/` without changing it, computes the risk signals,
generates the ASP facts, runs the solver, writes the report and result tables,
and runs the tests. A correct run matches the hashes in
`results/output_checksums.csv`.

Before you download the data, 26 of the 28 tests pass. The other two need the
survey files present. See `docs/TEST_LOG.txt`.

## Cross-check with sdcMicro

`experiments/sdcmicro/` holds an independent check against the R package
sdcMicro. It is a separate step and is not part of `run_all.ps1`:

```powershell
Rscript experiments/sdcmicro/run_sdcmicro.R
python experiments/sdcmicro/compare_results.py
```

The recorded run used R 4.6.1 with sdcMicro 5.8.2. It covers dataset D1 under
its seven core quasi-identifiers, not the whole corpus. It reports a singleton
rate of 0.115097 and a below-k=5 rate of 0.283152, which match the PUFGuard
pipeline to six decimal places.

## The main result

Across the five datasets, the mean share of records that are unique on the
quasi-identifiers is 14.9% with the core column sets and 51.8% with the extended
sets. These are sample-level signals under the configured attacker-knowledge
scenarios. They are not population estimates, re-identification probabilities, or
legal safe-harbor determinations.

## What PUFGuard is not

- It does not look up names, contact people, search social media, or recover
  identities.
- It does not quote or redistribute any record-level data or free text.
- Its decision is not a release authorization. A person still has to review it.
- It does not replace an ethics determination for any study involving people.

## License and citation

The code is MIT licensed. Each dataset keeps its own license and must be cited on
its own. See `CITATION.cff` and `data/metadata/integrity_manifest.csv`.
