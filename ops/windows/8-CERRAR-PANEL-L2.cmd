@echo off
title Cerrar Laboratorio L2
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Cerrar-Panel-Laboratorio.ps1"
if errorlevel 1 pause
