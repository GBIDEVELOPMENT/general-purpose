@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Start-ChatGPT-RTorrent.ps1" -Reset
if errorlevel 1 pause
