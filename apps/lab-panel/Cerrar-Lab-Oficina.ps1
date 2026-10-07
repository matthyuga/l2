$ErrorActionPreference = 'SilentlyContinue'

$panelRoot = $PSScriptRoot
$root = Split-Path $panelRoot -Parent
$runtimeDir = Join-Path $panelRoot 'office-runtime'
$panelPidFile = Join-Path $runtimeDir 'panel.pid'
$databasePidFile = Join-Path $runtimeDir 'mariadb.pid'

if (Test-Path -LiteralPath $panelPidFile) {
    $panelProcessId = [int](Get-Content -LiteralPath $panelPidFile -Raw)
    $process = Get-Process -Id $panelProcessId -ErrorAction SilentlyContinue
    if ($process -and $process.ProcessName -eq 'node') { Stop-Process -Id $panelProcessId }
    Remove-Item -LiteralPath $panelPidFile -ErrorAction SilentlyContinue
}

if (Test-Path -LiteralPath $databasePidFile) {
    $databaseProcessId = [int](Get-Content -LiteralPath $databasePidFile -Raw)
    $process = Get-Process -Id $databaseProcessId -ErrorAction SilentlyContinue
    if ($process) {
        $admin = Join-Path $root 'tools\mariadb-11.8.9-winx64\bin\mariadb-admin.exe'
        $databaseRootPassword = $env:L2_DB_ROOT_PASSWORD
        if ($databaseRootPassword) {
            & $admin --host=127.0.0.1 --port=3307 --user=root "--password=$databaseRootPassword" shutdown 2>$null
        }
        Start-Sleep -Milliseconds 700
        $process = Get-Process -Id $databaseProcessId -ErrorAction SilentlyContinue
        if ($process) { Stop-Process -Id $databaseProcessId }
    }
    Remove-Item -LiteralPath $databasePidFile -ErrorAction SilentlyContinue
}
