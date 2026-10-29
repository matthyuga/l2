$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$prefix = ($PSScriptRoot -replace '\\','/').ToLowerInvariant() + '/'
$owned = @(Get-CimInstance Win32_Process | Where-Object {
    $_.Name -match '^python(w)?\.exe$' -and
    (($_.CommandLine -replace '\\','/').ToLowerInvariant().Contains($prefix)) -and
    $_.CommandLine -match '(run_all|download|download_providers)\.py'
})
# Stop the manager first so it cannot restart a worker.
$owned | Sort-Object @{Expression={if($_.CommandLine -match 'run_all\.py'){0}else{1}}} | ForEach-Object {
    Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
    Wait-Process -Id $_.ProcessId -ErrorAction SilentlyContinue
    Write-Host ('Pausado PID ' + $_.ProcessId)
}
$file = Join-Path $PSScriptRoot 'run.json'
if (Test-Path -LiteralPath $file) {
    $state = Get-Content -LiteralPath $file -Raw -Encoding UTF8 | ConvertFrom-Json
    $state.state = 'stopped-for-transfer'
    $state.running = @{}
    $state | Add-Member -NotePropertyName stoppedUtc -NotePropertyValue ([DateTime]::UtcNow.ToString('o')) -Force
    $temp = $file + '.pause.tmp'
    [IO.File]::WriteAllText($temp, ($state | ConvertTo-Json -Depth 12), (New-Object Text.UTF8Encoding($false)))
    Move-Item -LiteralPath $temp -Destination $file -Force
}
Write-Host 'Descargas pausadas. Los archivos completos se conservan; 20-DESCARGAR-TEXTURAS-L2.cmd reanuda los pendientes.'
