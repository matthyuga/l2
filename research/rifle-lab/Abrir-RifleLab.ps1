$ErrorActionPreference='Stop'
$taskLab=Join-Path $PSScriptRoot '..\dust2-animation-study\client-lab\system'
$taskLab=(Resolve-Path -LiteralPath $taskLab).Path
if(Get-Process -Name L2 -ErrorAction SilentlyContinue){throw 'Cierra L2 desde el juego antes de abrir el laboratorio de rifles.'}
Write-Host 'M4A1 Prototipo32580: cliente aislado. Todavia conserva reglas de arco.'
Start-Process -FilePath (Join-Path $taskLab 'L2.exe') -ArgumentList 'L2Protocol' -WorkingDirectory $taskLab
