@echo off
setlocal
call "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Auxiliary\Build\vcvars32.bat" >nul
if errorlevel 1 exit /b 1
cd /d "%~dp0"
if not exist build mkdir build
cl /nologo /std:c++17 /EHsc /MT /O2 /W4 /LD hair_ingame.cpp /Fo:build\hair_ingame.obj /link /DEF:hair_ingame.def /OUT:stage\NexusHairHslGame.dll user32.lib gdi32.lib
if errorlevel 1 exit /b 1
cl /nologo /std:c++17 /EHsc /MT /O2 /W4 native_test.cpp /Fo:build\native_test.obj /Fe:build\native_test.exe user32.lib
if errorlevel 1 exit /b 1
build\native_test.exe
exit /b %errorlevel%
