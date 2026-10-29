$ErrorActionPreference = 'Stop'
$atmosphereRoot = $PSScriptRoot
$atmosphereStatePath = Join-Path $atmosphereRoot 'run.json'
if (Test-Path -LiteralPath $atmosphereStatePath) {
    $atmosphereRun = Get-Content -LiteralPath $atmosphereStatePath -Raw | ConvertFrom-Json
    $atmosphereIds = @($atmosphereRun.pid) + @($atmosphereRun.workers | ForEach-Object { $_.pid })
    foreach ($atmosphereProcessId in $atmosphereIds) {
        $atmosphereProcess = Get-CimInstance Win32_Process -Filter "ProcessId = $atmosphereProcessId"
        if ($atmosphereProcess -and $atmosphereProcess.Name -match '^python(w)?\.exe$' -and $atmosphereProcess.CommandLine.Contains($atmosphereRoot)) {
            Write-Host 'El gestor o un trabajador de esta biblioteca ya esta activo. Usar ESTADO.cmd.'
            exit
        }
    }
}
$atmospherePython = (Get-Command python).Source
Start-Process -FilePath $atmospherePython -ArgumentList ('"' + (Join-Path $atmosphereRoot 'manager.py') + '"') -WorkingDirectory $atmosphereRoot -WindowStyle Hidden
Write-Host 'Descarga iniciada. Usar ESTADO.cmd para consultar.'
