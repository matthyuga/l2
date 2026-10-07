$ErrorActionPreference = 'Stop'

$panelRoot = Join-Path $PSScriptRoot 'lab-panel'
$pidFile = Join-Path $panelRoot 'panel.pid'

if (Test-Path -LiteralPath $pidFile) {
    $panelProcessId = [int](Get-Content -LiteralPath $pidFile -Raw)
    $process = Get-Process -Id $panelProcessId -ErrorAction SilentlyContinue
    if ($process -and $process.ProcessName -eq 'node') {
        Stop-Process -Id $panelProcessId
    }
    Remove-Item -LiteralPath $pidFile -ErrorAction SilentlyContinue
}
