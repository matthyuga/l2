@echo off
title Laboratorio L2
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Abrir-Panel-Laboratorio.ps1"
if errorlevel 1 pause
