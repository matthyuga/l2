@echo off
setlocal
call "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Auxiliary\Build\vcvars32.bat" >nul
if errorlevel 1 exit /b 1
cd /d "%~dp0"
if not exist build mkdir build
cl /nologo /std:c++17 /EHsc /MT /O2 /W4 /LD map_fog.cpp /Fo:build\map_fog.obj /link /DEF:map_fog.def /OUT:build\d3d9.dll user32.lib bcrypt.lib crypt32.lib
if errorlevel 1 exit /b 1
cl /nologo /std:c++17 /EHsc /MT /Od /W4 native_test.cpp /Fo:build\native_test.obj /Fe:build\native_test.exe crypt32.lib
if errorlevel 1 exit /b 1
build\native_test.exe
if errorlevel 1 exit /b 1
cl /nologo /std:c++17 /EHsc /MT /O2 /W4 proxy_test.cpp /Fo:build\proxy_test.obj /Fe:build\proxy_test.exe user32.lib
if errorlevel 1 exit /b 1
build\proxy_test.exe "%~dp0build\d3d9.dll"
if errorlevel 1 exit /b 1
build\proxy_test.exe "%~dp0build\d3d9.dll" staged
exit /b %errorlevel%
