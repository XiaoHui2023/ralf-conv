@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  python -m venv .venv
  if errorlevel 1 exit /b 1
)
".venv\Scripts\python.exe" -m pip install -q -e "..\python-library\packages\ralf_model"
if errorlevel 1 exit /b 1
".venv\Scripts\python.exe" -m pip install -q -e .
if errorlevel 1 exit /b 1

if not exist "example\output\" mkdir "example\output"

".venv\Scripts\python.exe" -m ralf_conv -i "%~dp0example\demo_soc.ralf" -o "%~dp0example\output\demo_soc_flat.json"
if errorlevel 1 exit /b 1
".venv\Scripts\python.exe" -m ralf_conv --format hierarchical -i "%~dp0example\demo_soc.ralf" -o "%~dp0example\output\demo_soc_hierarchical.json"
exit /b %ERRORLEVEL%
