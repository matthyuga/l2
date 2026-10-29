$ErrorActionPreference = 'Stop'
$atmosphereRoot = $PSScriptRoot
$atmosphereStatePath = Join-Path $atmosphereRoot 'run.json'
if (-not (Test-Path -LiteralPath $atmosphereStatePath)) { Write-Host 'No hay gestor registrado.'; exit }
$atmosphereRun = Get-Content -LiteralPath $atmosphereStatePath -Raw | ConvertFrom-Json
$atmosphereIds = @($atmosphereRun.pid) + @($atmosphereRun.workers | ForEach-Object { $_.pid })
foreach ($atmosphereProcessId in $atmosphereIds) {
    $atmosphereProcess = Get-CimInstance Win32_Process -Filter "ProcessId = $atmosphereProcessId"
    if ($atmosphereProcess -and $atmosphereProcess.Name -match '^python(w)?\.exe$' -and $atmosphereProcess.CommandLine.Contains($atmosphereRoot)) {
        Stop-Process -Id $atmosphereProcessId
    }
}
$atmosphereRun.status = 'paused'
$atmosphereJson = $atmosphereRun | ConvertTo-Json -Depth 8
[System.IO.File]::WriteAllText($atmosphereStatePath, $atmosphereJson, [System.Text.UTF8Encoding]::new($false))
Write-Host 'Descargas pausadas. Los archivos parciales se conservan. Usar REANUDAR.cmd para continuar.'
