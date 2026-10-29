@echo off
setlocal
set "ROOT=%~dp0"
for %%I in ("%ROOT%..\l2\system-hud") do set "CLIENT_ROOT=%%~fI"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%ROOT%Start-L2Local.ps1"
if errorlevel 1 (
  echo No se pudo iniciar el servidor. Revisa la carpeta logs.
  pause
  exit /b 1
)
if not exist "%CLIENT_ROOT%\L2.exe" (
  echo Falta el perfil system-hud. Revisa la instalacion del cliente.
  pause
  exit /b 1
)
echo Amber arquera: arco Infinity Bow, fuego y lluvia de flechas. Perfil HUD actualizado.
echo Entra con Hellkevin y abre .amber. Su contrato ya esta firmado.
echo Invocar - atacar objetivo - fuego - lluvia. La lluvia requiere 3 Beast Soulshots.
echo Si falta el contrato: habla con Amber en el Coliseo y firma.
start "Lineage II - Amber Lab" /D "%CLIENT_ROOT%" "%CLIENT_ROOT%\L2.exe" L2Protocol
