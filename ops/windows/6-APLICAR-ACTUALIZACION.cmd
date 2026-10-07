@echo off
title Aplicar actualizacion de Lineage II local
echo.
echo Se reiniciara el servidor y se abrira el cliente actualizado.
echo Acepta SI en la ventana de Control de cuentas de usuario.
echo.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Reiniciar-Laboratorio-Sin-Cliente.ps1"
echo.
type "%~dp0lab-restart-status.txt"
echo.
pause
