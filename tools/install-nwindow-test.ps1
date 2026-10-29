$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$clientRoot = Join-Path (Split-Path $root -Parent) 'l2\system-clean'
$active = Join-Path $clientRoot 'NWindow.dll'
$patched = Join-Path $root 'backups\NWindow.dll.gameguard-disabled-v2'
$expected = '85A3765CC541069DD8EC96823BC903C196421BB07A795B1B65BB80588BE027A3'

if ((Get-FileHash -LiteralPath $patched -Algorithm SHA256).Hash -ne $expected) {
    throw 'Patched NWindow.dll hash mismatch.'
}

Get-Process -Name 'L2','L2-solo' -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2
Copy-Item -LiteralPath $patched -Destination $active -Force
if ((Get-FileHash -LiteralPath $active -Algorithm SHA256).Hash -ne $expected) {
    throw 'Installed NWindow.dll hash mismatch.'
}

$game = Start-Process -FilePath (Join-Path $clientRoot 'L2.exe') -ArgumentList 'L2Protocol' -WorkingDirectory $clientRoot -PassThru
[pscustomobject]@{ ProcessId=$game.Id; NWindowHash=$expected; Started=(Get-Date).ToString('o') } |
    ConvertTo-Json | Set-Content -LiteralPath (Join-Path $root 'nwindow-test-status.json') -Encoding UTF8
