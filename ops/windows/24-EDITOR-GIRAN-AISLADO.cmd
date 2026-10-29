@echo off
setlocal
set "EDITOR_ROOT=%~dp0research\giran-editor"
if not exist "%EDITOR_ROOT%\Working\23_22.unr" (
  echo Falta la copia de trabajo aislada de Giran.
  echo Ejecutar primero research\giran-editor\prepare.py
  pause
  exit /b 1
)
start "Giran - editor aislado" /D "%EDITOR_ROOT%\System" "%EDITOR_ROOT%\System\UnrealEd.exe" "%EDITOR_ROOT%\Working\23_22.unr" ini=GiranEditor.ini userini=GiranUser.ini -log
