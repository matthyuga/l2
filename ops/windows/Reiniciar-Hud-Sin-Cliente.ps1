$ErrorActionPreference = 'Stop'

$root = $PSScriptRoot
$clientRoot = Join-Path (Split-Path $root -Parent) 'l2\system-hud'
$statusFile = Join-Path $root 'hud-restart-status.txt'

function Set-Status([string]$message) {
    Set-Content -LiteralPath $statusFile -Value ('{0:yyyy-MM-dd HH:mm:ss}  {1}' -f (Get-Date), $message) -Encoding UTF8
}

Set-Status 'Reinicio elevado iniciado.'

$connections = Get-NetTCPConnection -LocalPort 7777 -State Established -ErrorAction SilentlyContinue
if ($connections) {
    throw 'Hay un cliente conectado al GameServer; se cancelo el cierre forzado.'
}

$listener = Get-NetTCPConnection -LocalPort 7777 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
if ($listener) {
    Stop-Process -Id $listener.OwningProcess -Force
    Wait-Process -Id $listener.OwningProcess -Timeout 15 -ErrorAction SilentlyContinue
}

Set-Status 'Servidor anterior detenido sin clientes conectados.'
& (Join-Path $root 'Start-L2Local.ps1') | Out-Null
Set-Status 'Servidor HUD listo; abriendo el cliente.'
Start-Process -FilePath (Join-Path $clientRoot 'L2.exe') -ArgumentList 'L2Protocol' -WorkingDirectory $clientRoot
Set-Status 'LISTO: servidor HUD iniciado y cliente system-hud abierto.'
