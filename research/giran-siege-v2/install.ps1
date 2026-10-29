$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
if(Get-Process -Name L2 -ErrorAction SilentlyContinue){throw 'L2 sigue abierto.'}
if(Get-NetTCPConnection -LocalPort 7777 -State Established -ErrorAction SilentlyContinue){throw 'Jugador conectado.'}
$proof=Get-Content (Join-Path $PSScriptRoot 'core-proof.json') -Raw | ConvertFrom-Json
$jar=Join-Path $root 'server/libs/GameServer.jar'
if((Get-FileHash $jar).Hash -ne $proof.old){throw 'Concurrent core edit: do not overwrite'}
$previous=Get-Content (Join-Path $root 'research/giran-siege/installed.json') -Raw | ConvertFrom-Json
$dest=Join-Path $root 'server/game/data/scripts/custom/GiranSiegeLab'
foreach($name in @('GiranRoster.java','GiranSiegeLab.java','SiegeSquadBrain.java','GiranSiegeVerification.java')){if((Get-FileHash (Join-Path $dest $name)).Hash -ne $previous.$name){throw "Concurrent script edit: $name"}}
foreach($name in @('SiegeAgenda.java','GiranAgendaVerification.java')){if(Test-Path (Join-Path $dest $name)){throw "Unexpected existing V2 file: $name"}}
$backup=Join-Path $root 'backups/giran-siege-v2-2026-10-11'
New-Item -ItemType Directory -Path (Join-Path $backup 'runtime-before') -Force | Out-Null
Copy-Item (Join-Path $dest '*.java') (Join-Path $backup 'runtime-before')
$gameId=[int](Get-Content (Join-Path $root 'run/game.pid'))
$proc=Get-CimInstance Win32_Process | Where-Object ProcessId -eq $gameId
if($proc){if($proc.ExecutablePath -ne (Join-Path $root 'tools/jdk-25.0.4.1+1/bin/java.exe').Replace('/','\') -or $proc.CommandLine -notmatch 'GameServer.jar'){throw 'Unexpected process identity'};Stop-Process -Id $gameId;Wait-Process -Id $gameId -Timeout 30 -ErrorAction SilentlyContinue}
$node=Join-Path $root 'tools/node-portable/node.exe'
& $node (Join-Path $PSScriptRoot 'state.js') state-before
if($LASTEXITCODE -ne 0){throw 'State snapshot failed'}
& $node (Join-Path $PSScriptRoot 'repair-roster.js')
if($LASTEXITCODE -ne 0){throw 'Reserved pilot repair failed'}
Copy-Item (Join-Path $PSScriptRoot 'GameServer-staged.jar') $jar
if((Get-FileHash $jar).Hash -ne $proof.new){throw 'Installed core hash mismatch'}
$state=@{}
foreach($name in @('GiranRoster.java','GiranSiegeLab.java','SiegeSquadBrain.java','SiegeAgenda.java','GiranAgendaVerification.java')){Copy-Item (Join-Path $PSScriptRoot $name) (Join-Path $dest $name);$state[$name]=(Get-FileHash (Join-Path $dest $name)).Hash}
$state['GameServer.jar']=(Get-FileHash $jar).Hash
$state | ConvertTo-Json | Set-Content (Join-Path $PSScriptRoot 'installed.json') -Encoding ascii
& (Join-Path $root 'Start-L2Local.ps1') -VerifyGiranAgenda
Write-Host 'GiranV2 installed; isolated native verification runs after roster readiness.'
