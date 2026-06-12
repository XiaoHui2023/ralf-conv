# CI helper: pack ralf-conv on Windows (PyInstaller onefile + release zip).
$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        py -3 -m venv .venv
    }
}

$py = Join-Path (Get-Location) ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) {
    throw "venv python not found: $py"
}

& $py -m pip install -U pip setuptools wheel
& $py -m pip install --upgrade --force-reinstall -e .
& $py -m pip install --upgrade --force-reinstall "pyinstaller>=6.0"

if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }

& $py -m PyInstaller --clean --noconfirm "ralf-conv-cli.spec"
if (-not (Test-Path "dist\ralf-conv.exe")) {
    throw "dist\ralf-conv.exe not found after PyInstaller"
}

& $py tools\bundle_release.py
