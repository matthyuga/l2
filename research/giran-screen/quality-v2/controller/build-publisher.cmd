@echo off
setlocal
call "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Auxiliary\Build\vcvars64.bat" >nul
if errorlevel 1 exit /b 1
cd /d "%~dp0"
cl /nologo /LD /MT /O2 /W4 publisher.cpp /Fe:publisher_hd.dll
exit /b %errorlevel%
