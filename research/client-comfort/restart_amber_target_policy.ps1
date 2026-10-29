param([switch]$TargetsOnly)
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
if (Get-Process -Name L2 -ErrorAction SilentlyContinue) { throw 'L2 sigue abierto.' }
if (Get-NetTCPConnection -LocalPort 7777 -State Established -ErrorAction SilentlyContinue) { throw 'Hay un jugador conectado.' }
$listener = Get-NetTCPConnection -LocalPort 7777 -State Listen -ErrorAction Stop
$gameProcess = Get-CimInstance Win32_Process | Where-Object ProcessId -eq $listener.OwningProcess
if ($gameProcess.CommandLine -notmatch 'GameServer\.jar') { throw 'No es GameServer.' }
Copy-Item -LiteralPath (Join-Path $root 'logs/game-stderr.log') -Destination (Join-Path $root 'backups/amber-target-policy-2026-10-10/game-before.log')
Stop-Process -Id $gameProcess.ProcessId
Wait-Process -Id $gameProcess.ProcessId -Timeout 30 -ErrorAction SilentlyContinue
if ($TargetsOnly) {
    $process = Start-Process -FilePath (Join-Path $root 'tools/jdk-25.0.4.1+1/bin/java.exe') `
        -ArgumentList '-server','-Djava.net.preferIPv4Stack=true','-Dfile.encoding=UTF-8','-Dorg.slf4j.simpleLogger.log.com.zaxxer.hikari=warn','-Dlab.amber.verify=true','-Dlab.amber.targets.only=true','-Dlab.race.verify=false','-Dlab.arena.spawn.verify=false','-Dlab.catalog.verify=false','-XX:+UseZGC','-Xms512m','-Xmx2048m','-jar','../libs/GameServer.jar' `
        -WorkingDirectory (Join-Path $root 'server/game') -WindowStyle Hidden -PassThru `
        -RedirectStandardOutput (Join-Path $root 'logs/game-stdout.log') `
        -RedirectStandardError (Join-Path $root 'logs/game-stderr.log')
    Set-Content -LiteralPath (Join-Path $root 'run/game.pid') -Value $process.Id
    Write-Host "GameServer targets-only iniciado: $($process.Id)"
} else {
    & (Join-Path $root 'Start-L2Local.ps1') -VerifyAmberContract
}
