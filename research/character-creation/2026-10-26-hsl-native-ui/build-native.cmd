@echo off
setlocal
call "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Auxiliary\Build\vcvars32.bat" >nul
if errorlevel 1 exit /b 1
cd /d "%~dp0"
if not exist build mkdir build
cl /nologo /std:c++17 /utf-8 /EHsc /MT /O2 /W4 /DUNICODE /D_UNICODE /LD hsl_picker.cpp /Fo:build\hsl_picker.obj /link /DEF:hsl_picker.def /OUT:build\NexusHairHslUi.dll user32.lib gdi32.lib
if errorlevel 1 exit /b 1
cl /nologo /std:c++17 /utf-8 /EHsc /MT /O2 /W4 /DUNICODE /D_UNICODE demo.cpp build\hsl_picker.obj /Fo:build\demo.obj /Fe:build\NexusHairHslDemo.exe /link /SUBSYSTEM:WINDOWS user32.lib gdi32.lib gdiplus.lib
if errorlevel 1 exit /b 1
build\NexusHairHslDemo.exe --selftest
if errorlevel 1 exit /b 1
cl /nologo /std:c++17 /utf-8 /EHsc /MT /O2 /W4 /DUNICODE /D_UNICODE dll_test.cpp /Fo:build\dll_test.obj /Fe:build\dll_test.exe user32.lib
if errorlevel 1 exit /b 1
build\dll_test.exe "%~dp0build\NexusHairHslUi.dll"
exit /b %errorlevel%
