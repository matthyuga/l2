@echo off
title Lineage II local - Hacer GM
set /p PERSONAJE=Nombre exacto del personaje: 
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Hacer-GM.ps1" "%PERSONAJE%"
echo.
pause
