@echo off
echo 1. L2 Lab
echo 2. L2 Hellgames
echo 3. L2 Academy
choice /C 123 /N /M "Elegir version: "
if errorlevel 3 goto academy
if errorlevel 2 goto hellgames
call "%~dp02-JUGAR.cmd"
exit /b
:hellgames
call "E:\l2-hellgames\2-JUGAR.cmd"
exit /b
:academy
call "E:\l2-academy\2-JUGAR.cmd"
