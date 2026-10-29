$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
if(Get-Process -Name L2 -ErrorAction SilentlyContinue){throw 'L2 sigue abierto.'}
if(Get-NetTCPConnection -LocalPort 7777 -State Established -ErrorAction SilentlyContinue){throw 'Jugador conectado.'}
$baseline=Get-Content (Join-Path $PSScriptRoot 'baseline.json') -Raw | ConvertFrom-Json
foreach($entry in $baseline.PSObject.Properties){if((Get-FileHash (Join-Path $root $entry.Name)).Hash -ne $entry.Value){throw "Concurrent edit: $($entry.Name)"}}
$backup=Join-Path $root 'backups/giran-siege-v3-2026-10-11'
New-Item -ItemType Directory -Path $backup -Force | Out-Null
foreach($pkg in @('GiranSiegeLab','AmberContract')){$old=Join-Path $root ('server/game/data/scripts/custom/'+$pkg);$save=Join-Path $backup $pkg;New-Item -ItemType Directory -Path $save -Force | Out-Null;Copy-Item (Join-Path $old '*.java') $save}
Copy-Item (Join-Path $root 'Start-L2Local.ps1') (Join-Path $backup 'Start-L2Local.ps1')
Copy-Item (Join-Path $root 'logs/game-stdout.log') (Join-Path $backup 'game-before.out.log')
Copy-Item (Join-Path $root 'logs/game-stderr.log') (Join-Path $backup 'game-before.err.log')
$gameId=[int](Get-Content (Join-Path $root 'run/game.pid'))
$proc=Get-CimInstance Win32_Process | Where-Object ProcessId -eq $gameId
if($proc){if($proc.ExecutablePath -ne (Join-Path $root 'tools/jdk-25.0.4.1+1/bin/java.exe').Replace('/','\') -or $proc.CommandLine -notmatch 'GameServer.jar'){throw 'Unexpected process identity'};Stop-Process -Id $gameId;Wait-Process -Id $gameId -Timeout 30 -ErrorAction SilentlyContinue}
& (Join-Path $root 'tools/node-portable/node.exe') (Join-Path $PSScriptRoot 'state.js') before
if($LASTEXITCODE -ne 0){throw 'State snapshot failed'}
$state=@{}
foreach($pkg in @('GiranSiegeLab','AmberContract')){foreach($src in Get-ChildItem (Join-Path $PSScriptRoot ($pkg+'/*.java'))){$dest=Join-Path $root ('server/game/data/scripts/custom/'+$pkg+'/'+$src.Name);if((Test-Path $dest) -and (Get-FileHash $dest).Hash -eq (Get-FileHash $src.FullName).Hash){continue};Copy-Item $src.FullName $dest;$state[$pkg+'/'+$src.Name]=(Get-FileHash $dest).Hash}}
Copy-Item (Join-Path $PSScriptRoot 'Start-L2Local.ps1') (Join-Path $root 'Start-L2Local.ps1')
$state['GameServer.jar']=(Get-FileHash (Join-Path $root 'server/libs/GameServer.jar')).Hash
$state | ConvertTo-Json | Set-Content (Join-Path $PSScriptRoot 'installed.json') -Encoding ascii
& (Join-Path $root 'Start-L2Local.ps1') -VerifyGiranDefense
Write-Host 'GiranV3 installed; isolated owned-defense verification runs after roster readiness.'
