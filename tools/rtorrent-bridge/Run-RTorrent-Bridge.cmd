@echo off
setlocal
cd /d "%~dp0"
if not exist "RTorrentBridge.exe" (
  echo RTorrentBridge.exe is missing. Download the complete Windows ZIP from GitHub Actions.
  pause
  exit /b 1
)
"%~dp0RTorrentBridge.exe" setup
if errorlevel 1 (pause & exit /b 1)
"%~dp0RTorrentBridge.exe" serve
if errorlevel 1 pause
