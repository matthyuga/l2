@echo off
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "research\texture-library\Pause-Downloads.ps1"
pause
