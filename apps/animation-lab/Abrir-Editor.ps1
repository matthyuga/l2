$ErrorActionPreference='Stop'
$taskBlender='D:\BlenderVersions\blender-3.5.1-windows-x64\blender.exe'
if(-not(Test-Path -LiteralPath $taskBlender)){throw 'No se encuentra Blender3.5.1 de esta PC.'}
Start-Process -FilePath $taskBlender -ArgumentList @('--factory-startup','--python',('"'+(Join-Path $PSScriptRoot 'open_lab.py')+'"')) -WorkingDirectory $PSScriptRoot
