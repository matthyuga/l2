$ErrorActionPreference = 'Stop'

$root = Split-Path $PSScriptRoot -Parent
$clientRoot = Join-Path (Split-Path $root -Parent) 'l2\system-clean'
$coreSource = Join-Path $root 'quarantine\lin2-il-w10-system\system\Core.dll'
$nwindowSource = Join-Path $root 'backups\NWindow.dll.before-gameguard-disable.bak'
$coreActive = Join-Path $clientRoot 'Core.dll'
$nwindowActive = Join-Path $clientRoot 'NWindow.dll'
$coreExpected = 'D83449B1CDF0AC717A98BE9289CAAB03CB507324A696EF449E31369E28416639'
$nwindowExpected = 'CB85F7A5DE375F1E9156EC6559AAE2A0A809B3ABAC4150142AAFB14BBF02B47B'

if ((Get-FileHash -LiteralPath $coreSource -Algorithm SHA256).Hash -ne $coreExpected) {
    throw 'El Core.dll limpio no coincide con el archivo verificado.'
}
if ((Get-FileHash -LiteralPath $nwindowSource -Algorithm SHA256).Hash -ne $nwindowExpected) {
    throw 'El NWindow.dll limpio no coincide con el archivo verificado.'
}

Get-Process -Name 'L2','L2-solo' -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

$corePatchedBackup = Join-Path $root 'backups\Core.dll.gameguard-flag-zero.bak'
if (-not (Test-Path -LiteralPath $corePatchedBackup)) {
    Copy-Item -LiteralPath $coreActive -Destination $corePatchedBackup
}

Copy-Item -LiteralPath $coreSource -Destination $coreActive -Force
Copy-Item -LiteralPath $nwindowSource -Destination $nwindowActive -Force

if ((Get-FileHash -LiteralPath $coreActive -Algorithm SHA256).Hash -ne $coreExpected) {
    throw 'Fallo al instalar Core.dll.'
}
if ((Get-FileHash -LiteralPath $nwindowActive -Algorithm SHA256).Hash -ne $nwindowExpected) {
    throw 'Fallo al instalar NWindow.dll.'
}

$game = Start-Process -FilePath (Join-Path $clientRoot 'L2.exe') -ArgumentList 'L2Protocol' -WorkingDirectory $clientRoot -PassThru
[pscustomobject]@{
    ProcessId = $game.Id
    CoreHash = $coreExpected
    NWindowHash = $nwindowExpected
    Started = (Get-Date).ToString('o')
} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $root 'clean-bypass-status.json') -Encoding UTF8
