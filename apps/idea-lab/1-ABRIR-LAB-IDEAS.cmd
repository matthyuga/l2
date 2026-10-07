@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Abrir-Lab-Ideas.ps1"
if errorlevel 1 pause

