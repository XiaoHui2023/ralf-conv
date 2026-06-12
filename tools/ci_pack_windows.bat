@echo off
setlocal EnableExtensions
cd /d "%~dp0\.."

if not exist ".venv\Scripts\python.exe" (
    python -m venv .venv
    if errorlevel 1 exit /b 1
)

set "PY=%CD%\.venv\Scripts\python.exe"
if not exist "%PY%" exit /b 1

"%PY%" -m pip install -U pip setuptools wheel
if errorlevel 1 exit /b 1
"%PY%" -m pip install --upgrade --force-reinstall -e .
if errorlevel 1 exit /b 1
"%PY%" -m pip install --upgrade --force-reinstall "pyinstaller>=6.0" tzdata
if errorlevel 1 exit /b 1

if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

"%PY%" -m PyInstaller --clean --noconfirm "ralf-conv-cli.spec"
if errorlevel 1 exit /b 1
if not exist "dist\ralf-conv.exe" exit /b 1

"%PY%" tools\bundle_release.py
if errorlevel 1 exit /b 1

exit /b 0
