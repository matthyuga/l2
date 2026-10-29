$ErrorActionPreference='Stop'
$taskRoot=$PSScriptRoot
$taskSystem=Join-Path $taskRoot 'client-lab\system'
$taskGame='E:\l2-local\tools\node-portable\node.exe'
if(Get-Process -Name L2 -ErrorAction SilentlyContinue){throw 'Cierra el cliente L2 antes de abrir esta prueba aislada.'}
$taskOriginal='E:\l2\animations\Fighter.ukx'
if((Get-FileHash -LiteralPath $taskOriginal -Algorithm SHA256).Hash.ToLowerInvariant() -ne '8a22d41ceaa78d52a10b856b923462eb8eb08d61b203d0d7904e464857ae988c'){throw 'Fighter original cambio desde la preparacion; revisar compatibilidad antes de probar.'}
$taskPatched=Join-Path $taskRoot 'client-lab\animations\Fighter.ukx'
if((Get-FileHash -LiteralPath $taskPatched -Algorithm SHA256).Hash.ToLowerInvariant() -ne 'fca90fac4df83e0bcc2af47f74b83cf64edd6625f3670f4230dbeeafaafcc892'){throw 'La animacion de prueba no coincide con el archivo verificado.'}
Write-Host 'Prueba de animacion: humana Fighter mujer, accion Reverencia (/socialbow). No hay mecanica de bomba instalada.'
Start-Process -FilePath (Join-Path $taskSystem 'L2.exe') -ArgumentList 'L2Protocol' -WorkingDirectory $taskSystem
