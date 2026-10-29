@echo off
setlocal
call "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Auxiliary\Build\vcvars32.bat" >nul
if errorlevel 1 exit /b 1
cd /d "%~dp0"
cl /nologo /std:c++17 /EHsc /MT /O2 /W4 cloud_test.cpp /Fo:build\cloud_test.obj /Fe:build\cloud_test.exe crypt32.lib
if errorlevel 1 exit /b 1
build\cloud_test.exe
exit /b %errorlevel%
