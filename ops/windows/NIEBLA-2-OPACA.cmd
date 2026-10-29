@echo off
python "%~dp0research\map-fog-native-v1\control.py" total
if errorlevel 1 pause
