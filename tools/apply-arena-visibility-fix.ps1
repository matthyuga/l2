$ErrorActionPreference = 'Stop'

$root = Split-Path $PSScriptRoot -Parent
$clientRoot = Join-Path (Split-Path $root -Parent) 'l2\system-clean'
$db = Join-Path $root 'tools\mariadb-11.8.9-winx64\bin\mariadb.exe'

Get-Process -Name 'L2','L2-solo' -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 4

$gamePidFile = Join-Path $root 'run\game.pid'
if (Test-Path -LiteralPath $gamePidFile) {
    $gamePid = [int](Get-Content -LiteralPath $gamePidFile -Raw)
    Stop-Process -Id $gamePid -Force -ErrorAction SilentlyContinue
}
for ($i = 0; $i -lt 30; $i++) {
    if (-not (Get-NetTCPConnection -LocalAddress '127.0.0.1' -LocalPort 7777 -State Listen -ErrorAction SilentlyContinue)) { break }
    Start-Sleep -Milliseconds 500
}

& $db --protocol=TCP -h 127.0.0.1 -P 3307 -u l2j -pl2local -D l2jmobiusinterlude --execute "UPDATE items i JOIN characters c ON c.charId=i.owner_id SET i.count=5000 WHERE c.char_name='Hellkevin' AND i.item_id=1467; UPDATE characters SET x=149500,y=46700,z=-3400,heading=32768,online=0 WHERE char_name='Hellkevin';"
if ($LASTEXITCODE -ne 0) { throw 'No se pudo ajustar el inventario y la posicion.' }

& (Join-Path $root 'Start-L2Local.ps1')
$game = Start-Process -FilePath (Join-Path $clientRoot 'L2.exe') -ArgumentList 'L2Protocol' -WorkingDirectory $clientRoot -PassThru

[pscustomobject]@{
    Soulshots = 5000
    PlayerLocation = '149500 46700 -3400'
    OpponentLocation = '149500 46100 -3400'
    GmDietMode = $true
    ClientProcessId = $game.Id
    Completed = (Get-Date).ToString('o')
} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $root 'arena-fix-status.json') -Encoding UTF8
