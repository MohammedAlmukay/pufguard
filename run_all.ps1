$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = if ($env:PUFGUARD_PYTHON) { $env:PUFGUARD_PYTHON } else { 'python' }

& $Python "$ProjectRoot\src\pufguard\analyze_corpus.py" --project-root $ProjectRoot
if ($LASTEXITCODE -ne 0) { throw 'Corpus analysis failed.' }
& $Python "$ProjectRoot\src\pufguard\run_logic.py" --project-root $ProjectRoot
if ($LASTEXITCODE -ne 0) { throw 'Logic execution failed.' }
& $Python "$ProjectRoot\src\pufguard\build_report.py" --project-root $ProjectRoot
if ($LASTEXITCODE -ne 0) { throw 'Report generation failed.' }
& $Python "$ProjectRoot\src\pufguard\generate_documentation.py" --project-root $ProjectRoot
if ($LASTEXITCODE -ne 0) { throw 'Documentation metadata generation failed.' }
Push-Location $ProjectRoot
try {
    & $Python -m unittest discover -s tests -v
    if ($LASTEXITCODE -ne 0) { throw 'Tests failed.' }
}
finally {
    Pop-Location
}

Write-Host "PUFGuard analysis and tests completed. See results/reports/."
