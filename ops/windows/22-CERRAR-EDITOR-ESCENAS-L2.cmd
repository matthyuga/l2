@echo off
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "research\scene-editor\Close-SceneEditor.ps1"
pause
