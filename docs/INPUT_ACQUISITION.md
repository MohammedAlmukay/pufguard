# Getting the five source files

The pipeline reads five public survey files. This archive does not include them.
They belong to their original depositors, they stay on their own repositories,
and we do not redistribute them. This page tells you exactly which file to fetch
from where, and how to confirm you got the same bytes we used.

Everything here is checkable. Each file is pinned by a versioned repository DOI
and by a SHA-256 digest, so you never have to guess whether you have the right
version.

## Before you start

You need about 1.5 MB of disk space and a browser. All five files are CC BY 4.0.
Download each one into the exact path shown, keeping the original filename.

## The files

| Dataset | DOI (version-pinned) | File to download | Save to | Bytes |
|---|---|---|---|---|
| D1 | `10.17632/wrwtvtppgd.1` | `Data.xlsx` | `data/raw/D1_BMI_Depression/Data.xlsx` | 764,774 |
| D2 | `10.17632/y7rbxs53g9.1` | `Raw_data_GLPI_weight_mgmt.xlsx` | `data/raw/D2_GLP1/Raw_data_GLPI_weight_mgmt.xlsx` | 285,165 |
| D3 | `10.17632/2v8k7kk9vt.1` | `Dataset.xlsx` | `data/raw/D3_Health_Message/Dataset.xlsx` | 101,719 |
| D4 | `10.17632/6z2hty8php.1` | `Original_Dataset_of_Employee_Attrition.xlsx` | `data/raw/D4_Employee_Attrition/Original_Dataset_of_Employee_Attrition.xlsx` | 191,255 |
| D4 | `10.17632/6z2hty8php.1` | `Dataset_Keys.docx` | `data/raw/D4_Employee_Attrition/Dataset_Keys.docx` | 28,784 |
| D4 | `10.17632/6z2hty8php.1` | `Online_Survey_Questions.docx` | `data/raw/D4_Employee_Attrition/Online_Survey_Questions.docx` | 30,622 |
| D5 | `10.5281/zenodo.21839927` | `Employment_Transition_Dataset.xlsx` | `data/raw/D5_Driving_Employment/Employment_Transition_Dataset.xlsx` | 134,115 |

The SHA-256 digest for every file is in `data/metadata/integrity_manifest.csv`.
That file is the authority, not this page.

D4 contributes three files. The workbook holds the records. The two `.docx`
files are the codebook and the questionnaire; the pipeline does not read them,
but they document what the columns mean, so we verify them too.

### How to download

**Mendeley Data (D1–D4).** Open `https://doi.org/<DOI>` from the table. The DOI
ends in `.1`, which pins version 1 of the deposit, so the link resolves to the
same version we used rather than to a later revision. On the landing page, use
the file list to download each file named above.

**Zenodo (D5).** Open `https://doi.org/10.5281/zenodo.21839927`. This is the
version DOI for the exact release we used. Download
`Employment_Transition_Dataset.xlsx` from the Files section.

Do not rename anything. The pipeline resolves files by the paths in the manifest.

## Check what you downloaded

From the project root:

```bash
python verify_inputs.py --project-root .
```

You want this:

```
OK        data/raw/D1_BMI_Depression/Data.xlsx
...
7/7 verified, 0 missing, 0 mismatched
All declared inputs verified. The pipeline can be run.
```

The script exits 0 only when all seven files match on both size and SHA-256, so
you can use it as a gate in a script.

If a file reports `MISMATCH`, you have a different version, a re-encoded copy,
or a partial download. Delete it and fetch it again from the version-pinned DOI.
Do not run the pipeline on a mismatched file: the reported numbers are tied to
these exact bytes.

## After the files verify

```powershell
python -m pip install -r requirements-lock.txt
./run_all.ps1
```

All 28 tests should now pass. Before the download, two of them fail by design,
because they read the source workbooks. See `docs/TEST_LOG.txt`.

## A note on dates

The manifest records `integrity_verified_on` as 2026-08-10, which is when we
hashed these files inside the project. It records `retrieval_date` as
`not_recorded`, because the files were downloaded before the manifest was
introduced and we will not back-fill a date we did not observe. This does not
weaken reproducibility: identity here rests on the version-pinned DOI and the
SHA-256 digest, both of which are exact, and neither of which depends on knowing
the download date.
