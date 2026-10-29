param([switch]$CreateClans,[switch]$Verify)
$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
if(Get-Process -Name L2 -ErrorAction SilentlyContinue){throw 'L2 sigue abierto.'}
if(Get-NetTCPConnection -LocalPort 7777 -State Established -ErrorAction SilentlyContinue){throw 'Jugador conectado.'}
$listener=Get-NetTCPConnection -LocalPort 7777 -State Listen -ErrorAction Stop
$proc=Get-CimInstance Win32_Process | Where-Object ProcessId -eq $listener.OwningProcess
if($proc.CommandLine -notmatch 'GameServer\.jar'){throw 'Listener no es GameServer.'}
$backup=Join-Path $root 'backups/giran-siege-2026-10-10'
$dest=Join-Path $root 'server/game/data/scripts/custom/GiranSiegeLab'
$files=@('GiranRoster.java','GiranSiegeLab.java','SiegeSquadBrain.java','GiranSiegeVerification.java')
$previous=$null
if(Test-Path (Join-Path $PSScriptRoot 'installed.json')){$previous=Get-Content (Join-Path $PSScriptRoot 'installed.json') -Raw | ConvertFrom-Json}
foreach($name in $files){$target=Join-Path $dest $name;if(Test-Path $target){if(!$previous -or (Get-FileHash $target).Hash -ne $previous.$name){throw "Concurrent edit: $name"}}}
$npc=Join-Path $root 'server/game/data/stats/npcs/custom/giran_lab_guardians.xml'
if((Test-Path $npc) -and (!$previous -or (Get-FileHash $npc).Hash -ne $previous.'giran_lab_guardians.xml')){throw 'Concurrent boss XML'}
$geo=Join-Path $root 'server/game/data/geodata/23_22.l2j'
$geoHash='AEDAA9A4E2BC1B82957CA5610109C550930ECDF18BCB80F1F1064AEB26B1FA46'
if((Get-FileHash (Join-Path $PSScriptRoot '23_22.l2j')).Hash -ne $geoHash){throw 'Staged Giran geodata hash mismatch'}
if((Test-Path $geo) -and (Get-FileHash $geo).Hash -ne $geoHash){throw 'Existing unrelated Giran geodata: not overwritten'}
if(!(Test-Path (Join-Path $backup 'before.json'))){& (Join-Path $root 'tools/node-portable/node.exe') (Join-Path $PSScriptRoot 'snapshot.js') (Join-Path $backup 'before.json');if($LASTEXITCODE -ne 0){throw 'Snapshot failed'}}
$core=(Get-FileHash (Join-Path $root 'server/libs/GameServer.jar')).Hash
Copy-Item (Join-Path $root 'logs/game-stderr.log') (Join-Path $backup ('game-before-'+(Get-Date -Format 'HHmmss')+'.log'))
Stop-Process -Id $proc.ProcessId
Wait-Process -Id $proc.ProcessId -Timeout 30 -ErrorAction SilentlyContinue
$state=@{}
try{
 New-Item -ItemType Directory -Path $dest -Force | Out-Null
 foreach($name in $files){Copy-Item (Join-Path $PSScriptRoot $name) (Join-Path $dest $name);$state[$name]=(Get-FileHash (Join-Path $dest $name)).Hash}
 Copy-Item (Join-Path $PSScriptRoot 'giran_lab_guardians.xml') $npc
 $state['giran_lab_guardians.xml']=(Get-FileHash $npc).Hash
 if(!(Test-Path $geo)){Copy-Item (Join-Path $PSScriptRoot '23_22.l2j') $geo}
 $state['23_22.l2j']=$geoHash
 $assets=Join-Path $root 'server/game/data/lab/giran';New-Item -ItemType Directory -Path $assets -Force | Out-Null
 foreach($key in 'fury','waves'){foreach($kind in 'clan','ally'){$name="$key-$kind.dds";Copy-Item (Join-Path $root "crest/prepared/$name") (Join-Path $assets $name)}}
 $state | ConvertTo-Json | Set-Content (Join-Path $PSScriptRoot 'installed.json') -Encoding ascii
}finally{
 $install=if($CreateClans){'true'}else{'false'};$verifyFlag=if($Verify){'true'}else{'false'}
 $p=Start-Process -FilePath (Join-Path $root 'tools/jdk-25.0.4.1+1/bin/java.exe') -ArgumentList '-server','-Djava.net.preferIPv4Stack=true','-Dfile.encoding=UTF-8','-Dorg.slf4j.simpleLogger.log.com.zaxxer.hikari=warn','-Dlab.race.verify=false','-Dlab.amber.verify=false','-Dlab.arena.spawn.verify=false','-Dlab.catalog.verify=false','-Dlab.summonbuff.verify=false','-Dlab.clanlab.verify=false',"-Dlab.giran.install=$install","-Dlab.giran.verify=$verifyFlag",'-XX:+UseZGC','-Xms512m','-Xmx2048m','-jar','../libs/GameServer.jar' -WorkingDirectory (Join-Path $root 'server/game') -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $root 'logs/game-stdout.log') -RedirectStandardError (Join-Path $root 'logs/game-stderr.log')
 Set-Content (Join-Path $root 'run/game.pid') $p.Id
 Write-Host "GameServer iniciado: $($p.Id); crear=$install verificar=$verifyFlag. No se inicia siege."
}
if((Get-FileHash (Join-Path $root 'server/libs/GameServer.jar')).Hash -ne $core){throw 'Core concurrent edit'}
