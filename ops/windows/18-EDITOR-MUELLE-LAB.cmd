@echo off
setlocal
set "EDITOR_ROOT=%~dp0research\gludio-editor"
if not exist "%EDITOR_ROOT%\Working-v2\24_19.unr" (
  echo Falta la copia de trabajo del muelle. Consultar research\gludio-editor\README.md
  pause
  exit /b 1
)
start "" /D "%EDITOR_ROOT%\System" "%EDITOR_ROOT%\System\UnrealEd.exe" "%EDITOR_ROOT%\Working-v2\24_19.unr" ini=GludioEditor.ini userini=User.ini -log
