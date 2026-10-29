$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$client = Join-Path (Split-Path $root -Parent) 'l2/system-hud'
$stage = Join-Path $root 'research/client-comfort'
$proof = Get-Content -LiteralPath (Join-Path $stage 'verification.json') -Raw | ConvertFrom-Json
if (Get-Process -Name L2 -ErrorAction SilentlyContinue) { throw 'L2 sigue abierto.' }
if (Get-NetTCPConnection -LocalPort 7777 -State Established -ErrorAction SilentlyContinue) { throw 'Hay un jugador conectado.' }
foreach ($name in @('user.ini','l2.ini','Interface.u','Interface.xdat')) {
    $current = (Get-FileHash -LiteralPath (Join-Path $client $name)).Hash.ToLowerInvariant()
    if ($current -ne $proof.original_hashes.$name) { throw "Cambio concurrente detectado: $name" }
}
$jar = Join-Path $root 'server/libs/GameServer.jar'
if ((Get-FileHash -LiteralPath $jar).Hash.ToLowerInvariant() -ne $proof.original_jar_sha256) { throw 'GameServer.jar cambio en otra sesion.' }
$listener = Get-NetTCPConnection -LocalPort 7777 -State Listen -ErrorAction SilentlyContinue
if ($listener) {
    $gameProcess = Get-CimInstance Win32_Process | Where-Object ProcessId -eq $listener.OwningProcess
    if ($gameProcess.CommandLine -notmatch 'GameServer\.jar') { throw 'El listener no es el GameServer esperado.' }
    if (Get-NetTCPConnection -LocalPort 7777 -State Established -ErrorAction SilentlyContinue) { throw 'Un jugador se conecto; instalacion cancelada.' }
    $logBackup = Join-Path $root 'backups/client-comfort-2026-10-10/logs-before'
    New-Item -ItemType Directory -Path $logBackup -Force | Out-Null
    Copy-Item -LiteralPath (Join-Path $root 'logs/game-stderr.log') -Destination $logBackup
    Stop-Process -Id $gameProcess.ProcessId
    Wait-Process -Id $gameProcess.ProcessId -Timeout 30 -ErrorAction SilentlyContinue
}
foreach ($name in @('user.ini','l2.ini','Interface.u','Interface.xdat')) {
    Copy-Item -LiteralPath (Join-Path $stage $name) -Destination (Join-Path $client $name) -Force
    if ((Get-FileHash -LiteralPath (Join-Path $stage $name)).Hash -ne (Get-FileHash -LiteralPath (Join-Path $client $name)).Hash) { throw "Copia incorrecta: $name" }
}
Copy-Item -LiteralPath (Join-Path $root 'build/client-comfort/GameServer.jar') -Destination $jar -Force
Write-Host 'Catalogo y camara instalados; GameServer listo para iniciar con verificacion.'
