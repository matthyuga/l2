@echo off
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 goto usepy
python -c "import sys; assert sys.version_info >= (3,10); import PIL" >nul 2>nul
if errorlevel 1 goto usepy
python -u research\texture-library\run_all.py
goto end
:usepy
py -3 -c "import sys; assert sys.version_info >= (3,10); import PIL" >nul 2>nul
if errorlevel 1 goto useportable
py -3 -u research\texture-library\run_all.py
goto end
:useportable
set "PORTABLE_PYTHON=%~dp0tools\blender-portable\blender-5.0.1-windows-x64\5.0\python\bin\python.exe"
if not exist "%PORTABLE_PYTHON%" goto missing
"%PORTABLE_PYTHON%" -c "import sys; assert sys.version_info >= (3,10); import PIL" >nul 2>nul
if errorlevel 1 goto missing
"%PORTABLE_PYTHON%" -u research\texture-library\run_all.py
goto end
:missing
echo Se necesita Python 3.10 o superior y Pillow para continuar.
echo Con Python instalado: python -m pip install Pillow
echo El editor 19-EDITOR-ESCENAS-L2.cmd funciona sin Python.
:end
pause
