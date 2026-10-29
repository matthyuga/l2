@echo off
setlocal
set "__COMPAT_LAYER=RunAsInvoker"
set "ROOT=%~dp0"
for %%I in ("%ROOT%..\l2\system-camera-online") do set "CAMERA_CLIENT=%%~fI"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%ROOT%Start-L2Local.ps1"
if errorlevel 1 goto failed
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%ROOT%Wait-L2LabReady.ps1"
if errorlevel 1 goto failed
if not exist "%CAMERA_CLIENT%\l2.ini" goto failed
if not exist "%CAMERA_CLIENT%\L2.exe" goto failed
start "L2 Observer Live" /D "%CAMERA_CLIENT%" "%CAMERA_CLIENT%\L2.exe" L2Protocol
exit /b 0
:failed
echo No se pudo abrir el observador. Revisa el estado del servidor y la copia de camara.
pause
exit /b 1
