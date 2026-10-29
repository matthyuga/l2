$ErrorActionPreference='Stop'
$taskRoot='E:\l2-local'
$taskBackup=Join-Path $taskRoot 'backups\direct-threat-2026-10-12'
$taskBuild=Join-Path $taskRoot 'build\direct-threat'
$taskJar=Join-Path $taskRoot 'server\libs\GameServer.jar'
if(Get-NetTCPConnection -LocalPort 7777 -State Established -ErrorAction SilentlyContinue){throw 'Hay clientes conectados; no se reinicia.'}
$taskListener=Get-NetTCPConnection -LocalPort 7777 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
if($taskListener){
    $taskProcess=Get-CimInstance Win32_Process -Filter ('ProcessId='+$taskListener.OwningProcess)
    if($taskProcess.CommandLine -notmatch 'GameServer.jar'){throw 'El proceso no es GameServer.'}
    Stop-Process -Id $taskProcess.ProcessId
    Wait-Process -Id $taskProcess.ProcessId -Timeout 30 -ErrorAction SilentlyContinue
}
if(!(Test-Path -LiteralPath (Join-Path $taskBackup 'GameServer.jar'))){Copy-Item -LiteralPath $taskJar -Destination (Join-Path $taskBackup 'GameServer.jar')}
& (Join-Path $taskRoot 'tools\jdk-25.0.4.1+1\bin\jar.exe') --update --file $taskJar -C $taskBuild org
if($LASTEXITCODE){throw 'Error actualizando JAR.'}
$taskSource=Join-Path $taskRoot 'source\L2J_Mobius_CT_0_Interlude'
$taskCommand='handlers\chat\commands\voiced\ThreatCommand.java'
Copy-Item -LiteralPath (Join-Path $taskSource ('dist\game\data\scripts\'+$taskCommand)) -Destination (Join-Path $taskRoot ('server\game\data\scripts\'+$taskCommand))
# Keep reproducible source overlay in sync; never replace unrelated classes or scripts.
foreach($taskFile in @(
 'java\org\l2jmobius\gameserver\mechanics\DirectThreat.java',
 'java\org\l2jmobius\gameserver\entity\actor\Creature.java',
 'java\org\l2jmobius\gameserver\entity\actor\Player.java',
 'java\org\l2jmobius\gameserver\entity\actor\status\PlayerStatus.java',
 'java\org\l2jmobius\gameserver\entity\actor\tasks\creature\HitTask.java',
 'java\org\l2jmobius\gameserver\entity\actor\tasks\creature\MagicUseTask.java',
 'dist\game\data\scripts\handlers\MasterHandler.java',
 ('dist\game\data\scripts\'+$taskCommand))) {
    $taskDest=Join-Path $taskRoot ('cloud-repo\mobius-overlay\L2J_Mobius_CT_0_Interlude\'+$taskFile)
    New-Item -ItemType Directory -Path (Split-Path $taskDest) -Force | Out-Null
    if(Test-Path -LiteralPath $taskDest){
        $taskDestBackup=Join-Path $taskBackup ('cloud-repo\mobius-overlay\L2J_Mobius_CT_0_Interlude\'+$taskFile)
        New-Item -ItemType Directory -Path (Split-Path $taskDestBackup) -Force | Out-Null
        if(!(Test-Path -LiteralPath $taskDestBackup)){Copy-Item -LiteralPath $taskDest -Destination $taskDestBackup}
    }
    Copy-Item -LiteralPath (Join-Path $taskSource $taskFile) -Destination $taskDest
}
& (Join-Path $taskRoot 'Start-L2Local.ps1')
