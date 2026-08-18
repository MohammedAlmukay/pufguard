# Reproducibility guide

## Validated environment

| Component | Validated value |
|---|---|
| Operating system | Windows, 64-bit |
| Python | 3.12.13 |
| pandas | 3.0.1 |
| openpyxl | 3.1.5 |
| clingo | 5.8.0 |
| Character encoding | UTF-8 / UTF-8 with BOM for CSV interoperability |

Use `requirements-lock.txt` for the documented environment. The broader
`requirements.txt` permits compatible maintenance updates and therefore should
not be used to claim exact computational reproduction.

## Clean-environment procedure

```powershell
py -3.12 -m venv .venv
./.venv/Scripts/Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-lock.txt
$env:PUFGUARD_PYTHON = (Resolve-Path ./.venv/Scripts/python.exe).Path
./run_all.ps1
```

The project path may contain spaces. All project scripts resolve files relative
to the `--project-root` argument; no source file contains a required absolute
path.

## Expected successful run

The command must:

1. report five datasets with 7,636 total records and 218 columns;
2. write five logic decisions;
3. regenerate aggregate result tables, SVG, report macros, and documentation
   metadata;
4. document all 218 variables;
5. checksum six raw files; and
6. finish the unit-test suite with `OK`.

Current headline rates, rounded for checking, are:

| Dataset | Core singleton | Extended singleton | Extended below k=5 |
|---|---:|---:|---:|
| D1 | 11.5% | 92.1% | 99.9% |
| D2 | 13.8% | 47.2% | 76.2% |
| D3 | 13.5% | 36.5% | 70.4% |
| D4 | 35.5% | 81.7% | 98.6% |

Minor display rounding is expected; the CSV files contain full precision.

## Integrity verification

From the project root:

```powershell
Get-Content data/metadata/checksums.sha256 | ForEach-Object {
    $hash, $path = $_ -split ' \*', 2
    $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $path).Hash.ToLower()
    if ($actual -ne $hash) { throw "Checksum mismatch: $path" }
}
```

The retrieval date was not recorded originally and is therefore not fabricated.
The verification date and current hash establish the baseline for this project
version.

## Determinism

The implemented analysis contains no random sampling or stochastic model. Given
the same raw files, configuration, Python/package behavior, and numeric parsing,
the CSV, logic, and report outputs should be deterministic. Excel-rendered layout
and PDF font embedding may vary across office/TeX engines without changing data.

## Portability notes

- Generated `__pycache__` files are disposable and should not be distributed.
- Google Drive may mark files online-only; ensure raw inputs are available
  offline before running.
- Clingo wheels are Python-version specific. Use the validated 3.12 environment.
- Never point `--project-root` at `data/raw`; it must be the repository root.

## Reproduction record

A reproducer should record:

- date, operating system, Python and package versions;
- Git commit or archived project checksum;
- result-table hashes;
- any configuration changes; and
- whether results matched exactly or only after numeric/display tolerance.

