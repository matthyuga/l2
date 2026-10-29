$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
Write-Host 'Cierra solamente el servidor del editor. Guarda la version desde el navegador ANTES de usarlo.'
$nodePaths = @(
    (Join-Path $root 'tools/node-v24.22.0-win-x64/node.exe'),
    (Join-Path $root 'tools/node-portable/node.exe')
)
Get-CimInstance Win32_Process | Where-Object {
    $_.Name -eq 'node.exe' -and $nodePaths -contains $_.ExecutablePath -and
    $_.CommandLine -match 'research[/\\]scene-editor[/\\]server\.js'
} | ForEach-Object {
    Stop-Process -Id $_.ProcessId -Force -ErrorAction Stop
    Write-Host ('Editor cerrado, PID ' + $_.ProcessId)
}
