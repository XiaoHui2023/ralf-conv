# CI helper: pack ralf-conv on Windows (PyInstaller onefile + release zip).
# Uses setup-python on GitHub Actions; no nested .venv.
$PSNativeCommandUseErrorActionPreference = $false
Set-Location (Split-Path -Parent $PSScriptRoot)

foreach ($dir in @(".venv", "build", "dist")) {
    if (Test-Path $dir) {
        Remove-Item -Recurse -Force $dir
    }
}

function Invoke-Native {
    param([Parameter(Mandatory)][string[]]$Command)
    & @Command
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}

Invoke-Native python,-V
Invoke-Native python,-m,pip,install,-U,pip,setuptools,wheel
Invoke-Native python,-m,pip,install,.
Invoke-Native python,-m,pip,install,"pyinstaller>=6.0",tzdata
Invoke-Native python,-m,PyInstaller,--clean,--noconfirm,ralf-conv-cli.spec

if (-not (Test-Path "dist\ralf-conv.exe")) {
    Write-Error "dist\ralf-conv.exe not found after PyInstaller"
    exit 1
}

Invoke-Native python,tools\bundle_release.py
