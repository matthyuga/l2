@echo off
setlocal
set "ROOT=%~dp0"
for %%I in ("%ROOT%..\l2\system-hud") do set "CLIENT_ROOT=%%~fI"

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%ROOT%Start-L2Local.ps1"
if errorlevel 1 (
  echo.
  echo No se pudo iniciar el servidor local. Revisa "%ROOT%logs".
  pause
  exit /b 1
)
if not exist "%CLIENT_ROOT%\L2.exe" (
  echo No se encontro el cliente en "%CLIENT_ROOT%\L2.exe".
  pause
  exit /b 1
)
start "Lineage II Interlude local" /D "%CLIENT_ROOT%" "%CLIENT_ROOT%\L2.exe" L2Protocol
