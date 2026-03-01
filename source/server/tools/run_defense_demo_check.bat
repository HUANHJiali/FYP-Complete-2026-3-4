@echo off
setlocal

REM One-click defense demo check (Windows)
REM Usage: double-click this file, or run it in terminal

cd /d "%~dp0.."

echo.
echo [1/1] Running defense demo check...
python tools\run_defense_demo_check.py
set EXIT_CODE=%ERRORLEVEL%

echo.
if %EXIT_CODE% EQU 0 (
    echo [PASS] Defense demo check passed.
) else (
    echo [FAIL] Defense demo check failed with exit code %EXIT_CODE%.
)

exit /b %EXIT_CODE%
