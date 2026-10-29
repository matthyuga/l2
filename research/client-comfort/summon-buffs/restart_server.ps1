param([switch]$Install, [switch]$Verify)
$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../../..')).Path
if(Get-Process -Name L2 -ErrorAction SilentlyContinue){throw 'L2 sigue abierto.'}
if(Get-NetTCPConnection -LocalPort 7777 -State Established -ErrorAction SilentlyContinue){throw 'Hay un jugador conectado.'}
$listener=Get-NetTCPConnection -LocalPort 7777 -State Listen -ErrorAction Stop
$gameProcess=Get-CimInstance Win32_Process | Where-Object ProcessId -eq $listener.OwningProcess
if($gameProcess.CommandLine -notmatch 'GameServer\.jar'){throw 'No es GameServer.'}
if($Install){
 $original=Get-Content (Join-Path $root 'backups/summon-buffs-2026-10-10/original-hashes.json') -Raw | ConvertFrom-Json
 $jar=(Join-Path $root 'server/libs/GameServer.jar')
 $expected=$original.$jar
 if(Test-Path -LiteralPath (Join-Path $PSScriptRoot 'installed.json')){$expected=(Get-Content (Join-Path $PSScriptRoot 'installed.json') -Raw | ConvertFrom-Json).core_sha256}
 if((Get-FileHash -LiteralPath $jar -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expected){throw 'Concurrent GameServer edit.'}
}
$stamp=Get-Date -Format 'HHmmss'
Copy-Item -LiteralPath (Join-Path $root 'logs/game-stderr.log') -Destination (Join-Path $root "backups/summon-buffs-2026-10-10/game-before-$stamp.log")
Stop-Process -Id $gameProcess.ProcessId
Wait-Process -Id $gameProcess.ProcessId -Timeout 30 -ErrorAction SilentlyContinue
if($Install){
 Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'GameServer.jar') -Destination (Join-Path $root 'server/libs/GameServer.jar')
 @{core_sha256=(Get-FileHash -LiteralPath (Join-Path $root 'server/libs/GameServer.jar') -Algorithm SHA256).Hash.ToLowerInvariant()} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'installed.json') -Encoding ascii
}
$verifyFlag=if($Verify){'true'}else{'false'}
$process=Start-Process -FilePath (Join-Path $root 'tools/jdk-25.0.4.1+1/bin/java.exe') `
 -ArgumentList '-server','-Djava.net.preferIPv4Stack=true','-Dfile.encoding=UTF-8','-Dorg.slf4j.simpleLogger.log.com.zaxxer.hikari=warn','-Dlab.amber.verify=false','-Dlab.agite.smoke=false','-Dlab.race.verify=false','-Dlab.arena.spawn.verify=false','-Dlab.catalog.verify=false',"-Dlab.summonbuff.verify=$verifyFlag",'-XX:+UseZGC','-Xms512m','-Xmx2048m','-jar','../libs/GameServer.jar' `
 -WorkingDirectory (Join-Path $root 'server/game') -WindowStyle Hidden -PassThru `
 -RedirectStandardOutput (Join-Path $root 'logs/game-stdout.log') -RedirectStandardError (Join-Path $root 'logs/game-stderr.log')
Set-Content -LiteralPath (Join-Path $root 'run/game.pid') -Value $process.Id
Write-Host "GameServer buffs de summon iniciado: $($process.Id); verify=$verifyFlag"
