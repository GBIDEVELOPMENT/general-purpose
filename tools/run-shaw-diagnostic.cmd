@echo off
setlocal
cd /d "%~dp0.."
where py >nul 2>nul
if not errorlevel 1 goto use_py
where python >nul 2>nul
if not errorlevel 1 goto use_python
echo Python 3.10 or newer is required. Install it, then try again.
goto done
:use_py
py -3 tools\shaw_pc_diagnose.py
goto done
:use_python
python tools\shaw_pc_diagnose.py
:done
echo.
echo If a JSON RESULT was printed, copy that into ChatGPT.
echo No email was sent.
pause
endlocal
