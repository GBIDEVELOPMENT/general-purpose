@echo off
setlocal
cd /d "%~dp0"
RTorrentBridge.exe setup --extend
if errorlevel 1 echo Configuration not changed. Review the error above.
pause
