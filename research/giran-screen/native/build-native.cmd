@echo off
setlocal
call "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Auxiliary\Build\vcvars32.bat" >nul
if errorlevel 1 exit /b 1
cd /d "%~dp0"
if not exist build mkdir build
cl /nologo /std:c++17 /EHsc /MT /O2 /W4 /LD nexus_tv.cpp /Fo:build\nexus_tv.obj /link /DEF:nexus_tv.def /OUT:build\d3d9.dll user32.lib
if errorlevel 1 exit /b 1
cl /nologo /std:c++17 /EHsc /MT /O2 /W4 relay_test.cpp /Fo:build\relay_test.obj /Fe:build\relay_test.exe user32.lib
exit /b %errorlevel%
