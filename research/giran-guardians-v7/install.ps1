param([switch]$Verify)
$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
if(Get-Process L2 -ErrorAction SilentlyContinue){throw 'L2 abierto'}
if(Get-NetTCPConnection -LocalPort 7777 -State Established -ErrorAction SilentlyContinue){throw 'Jugador conectado'}
$manifest=Join-Path $PSScriptRoot 'installed.json'
if(-not(Test-Path $manifest)){$manifest=Join-Path $PSScriptRoot 'baseline.json'}
$expected=Get-Content $manifest -Raw | ConvertFrom-Json
foreach($entry in $expected.PSObject.Properties){$rel=if($entry.Name -eq 'GameServer.jar'){'server/libs/GameServer.jar'}elseif($entry.Name.StartsWith('npcs/')){'server/game/data/stats/npcs/custom/'+$entry.Name.Substring(5)}elseif($entry.Name.StartsWith('geodata/')){'server/game/data/'+$entry.Name}else{'server/game/data/scripts/custom/'+$entry.Name};if((Get-FileHash (Join-Path $root $rel)).Hash -ne $entry.Value){throw "Concurrent edit $rel"}}
$backup=Join-Path $root ('backups/giran-guardians-v7-2026-10-11/run-'+(Get-Date -Format 'HHmmss'))
New-Item -ItemType Directory -Path $backup -Force | Out-Null
Copy-Item (Join-Path $root 'logs/game-stderr.log') (Join-Path $backup 'game.err.log')
Copy-Item (Join-Path $root 'logs/game-stdout.log') (Join-Path $backup 'game.out.log')
$gameId=[int](Get-Content (Join-Path $root 'run/game.pid'));$proc=Get-CimInstance Win32_Process | Where-Object ProcessId -eq $gameId
if($proc){if($proc.CommandLine -notmatch 'GameServer.jar'){throw 'Unexpected process'};Stop-Process -Id $gameId;Wait-Process -Id $gameId -Timeout 30 -ErrorAction SilentlyContinue}
$state=@{}
foreach($src in Get-ChildItem (Join-Path $PSScriptRoot 'GiranSiegeLab/*.java')){$dest=Join-Path $root ('server/game/data/scripts/custom/GiranSiegeLab/'+$src.Name);Copy-Item $src.FullName $dest;$state['GiranSiegeLab/'+$src.Name]=(Get-FileHash $dest).Hash}
$geo=Join-Path $root 'server/game/data/geodata/23_22.l2j';$state['geodata/23_22.l2j']=(Get-FileHash $geo).Hash
$state['npcs/giran_lab_guardians.xml']=(Get-FileHash (Join-Path $root 'server/game/data/stats/npcs/custom/giran_lab_guardians.xml')).Hash
$state['GameServer.jar']=(Get-FileHash (Join-Path $root 'server/libs/GameServer.jar')).Hash
$state | ConvertTo-Json | Set-Content (Join-Path $PSScriptRoot 'installed.json') -Encoding ascii
& (Join-Path $root 'Start-L2Local.ps1') -VerifyGiranDefense:$Verify
