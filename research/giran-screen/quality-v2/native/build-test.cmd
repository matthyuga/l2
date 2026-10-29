@echo off
call "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Auxiliary\Build\vcvars32.bat" >nul
cd /d "%~dp0"
cl /nologo /std:c++17 /EHsc /MT /O2 /W4 hd_test.cpp /Fo:build\hd_test.obj /Fe:build\hd_test.exe user32.lib
