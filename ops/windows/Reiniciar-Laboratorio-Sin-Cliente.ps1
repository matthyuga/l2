$ErrorActionPreference = 'Stop'

$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = [Security.Principal.WindowsPrincipal]::new($identity)
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    $arguments = '-NoProfile -ExecutionPolicy Bypass -File "' + $PSCommandPath + '"'
    Start-Process -FilePath 'powershell.exe' -Verb RunAs -ArgumentList $arguments -Wait
    exit
}

$root = $PSScriptRoot
$clientRoot = Join-Path (Split-Path $root -Parent) 'l2\system-hud'
$statusFile = Join-Path $root 'lab-restart-status.txt'

function Set-Status([string]$message) {
    Set-Content -LiteralPath $statusFile -Value ('{0:yyyy-MM-dd HH:mm:ss}  {1}' -f (Get-Date), $message) -Encoding UTF8
}

try {
    Set-Status 'Reinicio del laboratorio iniciado.'

    $connections = Get-NetTCPConnection -LocalPort 7777 -State Established -ErrorAction SilentlyContinue
    if ($connections) {
        throw 'Hay un cliente conectado al GameServer; se cancelo el reinicio para no expulsarlo.'
    }

    $listener = Get-NetTCPConnection -LocalPort 7777 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($listener) {
        Stop-Process -Id $listener.OwningProcess -Force
        Wait-Process -Id $listener.OwningProcess -Timeout 15 -ErrorAction SilentlyContinue
    }

    Set-Status 'Servidor anterior detenido. Iniciando la nueva version.'
    & (Join-Path $root 'Start-L2Local.ps1') | Out-Null
    Set-Status 'Servidor del laboratorio iniciado. Abriendo cliente HUD.'
    if (-not (Get-Process -Name 'L2' -ErrorAction SilentlyContinue)) {
        Start-Process -FilePath (Join-Path $clientRoot 'L2.exe') -ArgumentList 'L2Protocol' -WorkingDirectory $clientRoot
    }
    $panelStateFile = Join-Path $root 'lab-panel\state.json'
    if (Test-Path -LiteralPath $panelStateFile) {
        $panelState = Get-Content -LiteralPath $panelStateFile -Raw | ConvertFrom-Json
        $panelState.requiresRestart = $false
        $panelState | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $panelStateFile -Encoding UTF8
    }
    Set-Status 'LISTO: servidor actualizado y cliente HUD abierto.'
}
catch {
    Set-Status ('ERROR: ' + $_.Exception.Message)
    throw
}
