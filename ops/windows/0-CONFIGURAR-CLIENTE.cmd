@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Configurar-Cliente.ps1"
if errorlevel 1 pause
