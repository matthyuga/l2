@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0lab-panel\Abrir-Lab-Oficina.ps1"
if errorlevel 1 pause

