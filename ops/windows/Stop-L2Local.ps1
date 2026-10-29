$ErrorActionPreference = 'SilentlyContinue'
$Root = $PSScriptRoot
$RunDir = Join-Path $Root 'run'

foreach ($name in @('game','login')) {
    $pidFile = Join-Path $RunDir "$name.pid"
    if (Test-Path -LiteralPath $pidFile) {
        $processId = [int](Get-Content -LiteralPath $pidFile -Raw)
        Stop-Process -Id $processId -ErrorAction SilentlyContinue
    }
}

Start-Sleep -Seconds 2

$admin = Join-Path $Root 'tools\mariadb-11.8.9-winx64\bin\mariadb-admin.exe'
if (Get-NetTCPConnection -LocalAddress '127.0.0.1' -LocalPort 3307 -State Listen -ErrorAction SilentlyContinue) {
    & $admin --host=127.0.0.1 --port=3307 --user=root --password=l2localroot shutdown 2>$null
}

Write-Host 'Servidor local detenido.' -ForegroundColor Green
Write-Host 'Consejo: sal del personaje antes de detenerlo para asegurar el guardado.'
