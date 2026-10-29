@echo off
setlocal
cd /d "%~dp0"
echo VISOR 3D DE MODELOS L2
echo.
echo 1 - Monstruos: paquete 1
echo 2 - Monstruos: paquete 2
echo 3 - Monstruos: paquete 3
echo 4 - NPC: paquete 1
echo 5 - NPC: paquete 2
echo 6 - NPC: eventos
echo 7 - Personajes humanos guerreros y equipamiento
echo 8 - Personajes humanos magos y equipamiento
echo 9 - Elfos y equipamiento
echo A - Elfos oscuros y equipamiento
echo B - Enanos y equipamiento
echo C - Orcos guerreros y equipamiento
echo D - Orcos magos y equipamiento
echo.
echo Controles: H ayuda, PgUp/PgDown modelo, [ y ] animacion,
echo X reproduce en bucle, F centra, Ctrl+S guarda captura.
echo Raton izquierdo gira; derecho acerca; central desplaza.
echo.
choice /c 123456789ABCD /n /m "Elegi el paquete: "
set "pick=%errorlevel%"
if "%pick%"==1 set "package=LineageMonsters"
if "%pick%"==2 set "package=LineageMonsters2"
if "%pick%"==3 set "package=LineageMonsters3"
if "%pick%"==4 set "package=LineageNpcs"
if "%pick%"==5 set "package=LineageNPCs2"
if "%pick%"==6 set "package=lineagenpcsev"
if "%pick%"==7 set "package=Fighter"
if "%pick%"==8 set "package=Magic"
if "%pick%"==9 set "package=Elf"
if "%pick%"==10 set "package=DarkElf"
if "%pick%"==11 set "package=Dwarf"
if "%pick%"==12 set "package=Orc"
if "%pick%"==13 set "package=Shaman"
if not defined package exit /b 0
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0research\model-catalog\Open-L2Models.ps1" -Package "%package%"
if errorlevel 1 (
    echo No se pudo iniciar el visor. El mensaje anterior indica el motivo.
    pause
    exit /b 1
)
echo Si la ventana del visor no aparece, revisa research\model-catalog\logs.
pause
