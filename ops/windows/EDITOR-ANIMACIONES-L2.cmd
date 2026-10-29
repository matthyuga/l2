@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0animation-lab\Abrir-Editor.ps1"
if errorlevel 1 pause
