@echo off
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0research\model-catalog\Open-L2Gallery.ps1"
if errorlevel 1 pause
