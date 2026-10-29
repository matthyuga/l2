param([switch]$Verify)
$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
if(Get-Process -Name L2 -ErrorAction SilentlyContinue){throw 'L2 sigue abierto.'}
if(Get-NetTCPConnection -LocalPort 7777 -State Established -ErrorAction SilentlyContinue){throw 'Jugador conectado.'}
$listener=Get-NetTCPConnection -LocalPort 7777 -State Listen -ErrorAction Stop
$proc=Get-CimInstance Win32_Process | Where-Object ProcessId -eq $listener.OwningProcess
if($proc.CommandLine -notmatch 'GameServer\.jar'){throw 'Listener no es GameServer.'}
$backup=Join-Path $root 'backups/clan-lab-2026-10-10'
$dest=Join-Path $root 'server/game/data/scripts/custom/ClanLab'
foreach($name in 'ClanLab.java','ClanLabVerification.java'){
 $target=Join-Path $dest $name
 if((Test-Path $target) -and (Test-Path (Join-Path $PSScriptRoot 'installed.json'))){
  $state=Get-Content (Join-Path $PSScriptRoot 'installed.json') -Raw | ConvertFrom-Json
  if((Get-FileHash $target).Hash -ne $state.$name){throw "Concurrent edit: $name"}
 }elseif(Test-Path $target){throw "Untracked existing $name"}
}
if(!(Test-Path (Join-Path $backup 'before.json'))){
 & (Join-Path $root 'tools/node-portable/node.exe') (Join-Path $PSScriptRoot 'snapshot.js') (Join-Path $backup 'before.json')
 if($LASTEXITCODE -ne 0){throw 'Snapshot failed.'}
}
$hash=(Get-FileHash (Join-Path $root 'server/libs/GameServer.jar')).Hash
$stamp=Get-Date -Format 'HHmmss'
Copy-Item (Join-Path $root 'logs/game-stderr.log') (Join-Path $backup "game-before-$stamp.log")
Stop-Process -Id $proc.ProcessId
Wait-Process -Id $proc.ProcessId -Timeout 30 -ErrorAction SilentlyContinue
$state=@{}
try{
 New-Item -ItemType Directory -Path $dest -Force | Out-Null
 foreach($name in 'ClanLab.java','ClanLabVerification.java'){
  Copy-Item (Join-Path $PSScriptRoot $name) (Join-Path $dest $name)
  $state[$name]=(Get-FileHash (Join-Path $dest $name)).Hash
 }
 $state | ConvertTo-Json | Set-Content (Join-Path $PSScriptRoot 'installed.json') -Encoding ascii
}finally{
 $flag=if($Verify){'true'}else{'false'}
 $p=Start-Process -FilePath (Join-Path $root 'tools/jdk-25.0.4.1+1/bin/java.exe') -ArgumentList '-server','-Djava.net.preferIPv4Stack=true','-Dfile.encoding=UTF-8','-Dorg.slf4j.simpleLogger.log.com.zaxxer.hikari=warn','-Dlab.race.verify=false','-Dlab.amber.verify=false','-Dlab.arena.spawn.verify=false','-Dlab.catalog.verify=false','-Dlab.summonbuff.verify=false',"-Dlab.clanlab.verify=$flag",'-XX:+UseZGC','-Xms512m','-Xmx2048m','-jar','../libs/GameServer.jar' -WorkingDirectory (Join-Path $root 'server/game') -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $root 'logs/game-stdout.log') -RedirectStandardError (Join-Path $root 'logs/game-stderr.log')
 Set-Content (Join-Path $root 'run/game.pid') $p.Id
 Write-Host "GameServer iniciado: $($p.Id) verify=$flag"
}
if((Get-FileHash (Join-Path $root 'server/libs/GameServer.jar')).Hash -ne $hash){throw 'Core concurrent edit.'}
