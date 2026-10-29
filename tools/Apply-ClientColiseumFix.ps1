param([switch]$VerifyArenaSpawns)
$ErrorActionPreference = 'Stop'
$TaskRoot = Split-Path $PSScriptRoot -Parent
$TaskClient = Join-Path (Split-Path $TaskRoot -Parent) 'l2'
$TaskBackup = Join-Path $TaskRoot 'backups/client-coliseum-2026-10-10'
$TaskStatus = Join-Path $TaskRoot 'run/client-coliseum-fix-status.txt'
function Set-TaskStatus([string]$Message) {
    Set-Content -LiteralPath $TaskStatus -Value ('{0:yyyy-MM-dd HH:mm:ss} {1}' -f (Get-Date), $Message) -Encoding UTF8
}
try {
    Set-TaskStatus 'Cerrando el cliente averiado para aplicar los archivos.'
    foreach ($TaskGame in Get-Process L2 -ErrorAction SilentlyContinue) {
        if (-not $TaskGame.Path) { throw 'Windows no permite acceder a L2: cerrar el juego o ejecutar este reparador como administrador.' }
        if (-not $TaskGame.Path.StartsWith($TaskClient + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Hay otro cliente L2 abierto; no se cierra.' }
        $TaskGame.CloseMainWindow() | Out-Null
        if (-not $TaskGame.WaitForExit(10000)) { Stop-Process -Id $TaskGame.Id -Force }
    }
    $TaskDeadline = (Get-Date).AddSeconds(30)
    while (Get-NetTCPConnection -LocalPort 7777 -State Established -ErrorAction SilentlyContinue) {
        if ((Get-Date) -ge $TaskDeadline) { throw 'Queda un cliente conectado; no se reinicia el GameServer.' }
        Start-Sleep -Milliseconds 500
    }
    & (Join-Path $TaskRoot 'research/amber-l2/Build-AmberClientIcons.ps1')
    & (Join-Path $TaskRoot 'research/amber-l2/Install-AmberVisualV3.ps1')
    Set-TaskStatus 'Iconos corregidos. Reiniciando GameServer sin clientes conectados.'
    $TaskListener = Get-NetTCPConnection -LocalPort 7777 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($TaskListener) {
        $TaskServer = Get-Process -Id $TaskListener.OwningProcess
        if ($TaskServer.Path -ne (Join-Path $TaskRoot 'tools\jdk-25.0.4.1+1\bin\java.exe')) { throw 'El puerto 7777 pertenece a otro proceso.' }
        Copy-Item -LiteralPath (Join-Path $TaskRoot 'logs/game-stderr.log') -Destination (Join-Path $TaskBackup 'game-before-restart.log') -Force
        Stop-Process -Id $TaskServer.Id -Force
        Wait-Process -Id $TaskServer.Id -Timeout 15 -ErrorAction SilentlyContinue
    }
    & (Join-Path $TaskRoot 'Start-L2Local.ps1') -VerifyArenaSpawns:$VerifyArenaSpawns
    Set-TaskStatus 'READY: iconos 121 instalados, servidor actualizado; cliente cerrado.'
}
catch { Set-TaskStatus ('ERROR: ' + $_.Exception.Message); throw }
