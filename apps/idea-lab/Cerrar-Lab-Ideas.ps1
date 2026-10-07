$ErrorActionPreference = 'SilentlyContinue'

$runtimeDir = Join-Path $PSScriptRoot 'runtime'
$pidFile = Join-Path $runtimeDir 'server.pid'

try {
    Invoke-WebRequest -UseBasicParsing -Method POST -Uri 'http://127.0.0.1:3212/api/shutdown' -TimeoutSec 2 | Out-Null
}
catch {}

Start-Sleep -Milliseconds 400
if (Test-Path -LiteralPath $pidFile) {
    $serverProcessId = [int](Get-Content -LiteralPath $pidFile -Raw)
    $process = Get-Process -Id $serverProcessId -ErrorAction SilentlyContinue
    if ($process -and $process.ProcessName -eq 'powershell') {
        Stop-Process -Id $serverProcessId
    }
    Remove-Item -LiteralPath $pidFile -ErrorAction SilentlyContinue
}

