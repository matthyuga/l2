$ErrorActionPreference='Stop'
$AmberProject=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
if(Get-CimInstance Win32_Process | Where-Object {$_.Name -match '^L2.*\.exe$'}){throw 'Cliente abierto; no instalar.'}
if(Get-NetTCPConnection -LocalPort 7777 -State Established -ErrorAction SilentlyContinue){throw 'Jugador conectado; no reiniciar.'}
$AmberGame=Get-CimInstance Win32_Process -Filter 'ProcessId = 13144'
if(-not $AmberGame -or $AmberGame.ExecutablePath -ne (Join-Path $AmberProject 'tools/jdk-25.0.4.1+1/bin/java.exe') -or $AmberGame.CommandLine -notmatch 'GameServer\.jar'){throw 'Otra sesion cambio GameServer; revisar antes de reiniciar.'}
$AmberReport=Join-Path $PSScriptRoot 'reports/vfx-v10-structure.log'
if(-not(Select-String -LiteralPath $AmberReport -SimpleMatch 'PASS: 11868 package/catalog checks')){throw 'Falta validacion de paquetes.'}
Copy-Item -LiteralPath (Join-Path $AmberProject 'logs/game-stderr.log') -Destination (Join-Path $PSScriptRoot 'reports/v10-before-restart.log') -Force
Stop-Process -Id $AmberGame.ProcessId -Force
& (Join-Path $PSScriptRoot 'Install-AmberVfxV10.ps1')
& (Join-Path $AmberProject 'Start-L2Local.ps1') -VerifyAmberContract
