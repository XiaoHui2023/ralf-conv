@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  call "%~dp0update.bat"
  if errorlevel 1 exit /b %ERRORLEVEL%
)
".venv\Scripts\python.exe" -m pip install -q -e "..\python-library\packages\ralf_model"
if errorlevel 1 exit /b %ERRORLEVEL%
".venv\Scripts\python.exe" -m pytest
exit /b %ERRORLEVEL%
