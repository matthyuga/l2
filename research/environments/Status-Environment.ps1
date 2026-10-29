$ErrorActionPreference = 'Stop'
$profile = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'environment.json') -Raw | ConvertFrom-Json
Write-Host ($profile.name + ' | ' + $profile.address + ' | ' + $profile.state)
foreach ($port in @(3307,2106,19014,7777)) {
    $socket = Get-NetTCPConnection -LocalAddress $profile.address -LocalPort $port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
    Write-Host ('{0}:{1} {2}' -f $profile.address,$port,$(if ($socket) {'LISTO PID ' + $socket.OwningProcess} else {'DETENIDO'}))
}
