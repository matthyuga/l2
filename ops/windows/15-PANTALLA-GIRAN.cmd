@echo off
setlocal
set "__COMPAT_LAYER=RunAsInvoker"
set "ROOT=%~dp0"
for %%I in ("%ROOT%..\l2\system-screen-lab") do set "VIEWER_CLIENT=%%~fI"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%ROOT%Start-L2Local.ps1"
if errorlevel 1 goto failed
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%ROOT%Wait-L2LabReady.ps1"
if errorlevel 1 goto failed
if not exist "%VIEWER_CLIENT%\d3d9.dll" goto failed
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%ROOT%nexus-tv\Apply-HDClient.ps1"
if errorlevel 1 goto failed
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%ROOT%nexus-tv\Start-NexusTV.ps1" -NoBrowser
if errorlevel 1 goto failed
start "Nexus TV Viewer" /D "%VIEWER_CLIENT%" "%VIEWER_CLIENT%\L2.exe" L2Protocol
exit /b 0
:failed
echo No se pudo abrir el cliente espectador de Nexus TV.
pause
exit /b 1
