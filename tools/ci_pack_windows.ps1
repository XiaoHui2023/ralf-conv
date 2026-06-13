# CI helper: pack ralf-conv on Windows (PyInstaller onefile + release zip).
# Uses setup-python on GitHub Actions; no nested .venv (avoids editable/PyInstaller issues).
$ErrorActionPreference = "Stop"
# pip/PyInstaller write progress to stderr; do not treat as terminating errors on GHA pwsh.
$PSNativeCommandUseErrorActionPreference = $false
Set-Location (Split-Path -Parent $PSScriptRoot)

foreach ($dir in @(".venv", "build", "dist")) {
    if (Test-Path $dir) {
        Remove-Item -Recurse -Force $dir
    }
}

python -V
python -m pip install -U pip setuptools wheel
python -m pip install .
python -m pip install "pyinstaller>=6.0" tzdata

python -m PyInstaller --clean --noconfirm "ralf-conv-cli.spec"
if (-not (Test-Path "dist\ralf-conv.exe")) {
    throw "dist\ralf-conv.exe not found after PyInstaller"
}

python tools\bundle_release.py
$zip = Get-ChildItem "dist\ralf-conv-*-windows.zip" -ErrorAction Stop | Select-Object -First 1
if (-not $zip) {
    throw "dist\ralf-conv-*-windows.zip not found after bundle_release"
}
