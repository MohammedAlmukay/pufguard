# Reproduction environment

This file records the toolchain under which the deposited outputs were
regenerated and the automated tests pass. Re-running the pipeline on this
toolchain reproduces `results/tables/paper1_macros.tex` byte-for-byte.

## Python pipeline

| Component | Version |
|---|---|
| OS | Windows 11 (64-bit) |
| Python | 3.14.0 |
| pandas | 3.0.3 |
| numpy | 2.4.6 |
| openpyxl | 3.1.5 |
| clingo | 5.8.1 |
| pytest | 9.1.1 |

Exact pins are in `requirements-lock.txt`. `pyproject.toml` records the broader
supported ranges; the versions above are the specific ones exercised here.

> Note: an earlier validation was performed on Python 3.12.13. The outputs
> reproduce identically on the 3.14.0 toolchain above. Use `requirements-lock.txt`
> to reproduce the recorded run exactly.

## Cross-tool check (R / sdcMicro)

| Component | Version |
|---|---|
| R | 4.6.1 (2026-06-24 ucrt) |
| sdcMicro | 5.8.2 |

The R and sdcMicro versions are also recorded in-line in
`experiments/sdcmicro/sdcmicro_results.csv`. The sdcMicro step is independent of
the Python pipeline and is invoked separately (see README).
