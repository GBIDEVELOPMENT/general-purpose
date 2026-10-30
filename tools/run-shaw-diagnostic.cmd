@echo off
setlocal
cd /d "%~dp0.."
where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
  py -3 tools\shaw_pc_diagnose.py
) else (
  where python >nul 2>nul
  if %ERRORLEVEL% EQU 0 (
    python tools\shaw_pc_diagnose.py
  ) else (
    echo Python 3 is required. Install it from python.org, then run this file again.
  )
)
echo.
echo Copy the JSON RESULT shown above back into ChatGPT. No email was sent.
pause
endlocal
