@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0research\rifle-lab\Abrir-RifleLab.ps1"
if errorlevel 1 pause
