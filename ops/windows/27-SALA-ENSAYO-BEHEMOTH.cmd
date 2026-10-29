@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0research\mounts\behemoth-v2\Open-BehemothLab.ps1"
if errorlevel 1 pause
