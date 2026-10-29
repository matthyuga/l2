@echo off
call "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Auxiliary\Build\vcvars32.bat" >nul
cd /d E:\l2-local\research\map-fog-live-v8-20261027
link /nologo /DLL build\map_fog.obj /DEF:map_fog.def /OUT:E:\l2-local\research\map-fog-performance-20261027\analysis.dll /MAP:E:\l2-local\research\map-fog-performance-20261027\analysis.map user32.lib bcrypt.lib crypt32.lib
