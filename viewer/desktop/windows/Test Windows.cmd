@echo off
cd /d "%~dp0"
"resources\runtime\python.exe" "resources\desktop\smoke_test.py"
if errorlevel 1 (
  echo Windows backend smoke test FAILED. Please send the error text.
) else (
  echo Windows backend smoke test PASSED. Please also follow the GUI checks in README.txt.
)
pause
