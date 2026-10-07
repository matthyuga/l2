@echo off
title Lineage II local - Detener
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Stop-L2Local.ps1"
echo.
pause
