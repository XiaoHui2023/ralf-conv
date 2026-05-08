@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" python -m venv .venv
".venv\Scripts\python.exe" -m pip install -e "..\python-library\packages\ralf_model"
if errorlevel 1 exit /b %ERRORLEVEL%
".venv\Scripts\python.exe" -m pip install -e ".[dev]"
exit /b %ERRORLEVEL%
