$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$client=(Resolve-Path (Join-Path $root '../l2')).Path
if(Get-Process -Name L2 -ErrorAction SilentlyContinue){throw 'Cierra L2 antes de restaurar la precarga.'}
$manifest=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'installation.json') -Raw | ConvertFrom-Json
foreach($entry in $manifest.files){
    $target=[IO.Path]::GetFullPath($entry.target)
    if(-not $target.StartsWith($client+'\',[StringComparison]::OrdinalIgnoreCase)){throw "Ruta fuera del cliente: $target"}
    if(-not (Test-Path -LiteralPath $target) -or (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash -ne $entry.installed_sha256){throw "Archivo modificado despues de instalar: $target"}
    if($entry.backup -and (Get-FileHash -LiteralPath $entry.backup -Algorithm SHA256).Hash -ne $entry.before_sha256){throw "Respaldo no valido: $($entry.backup)"}
}
foreach($entry in $manifest.files){
    if($entry.backup){Copy-Item -LiteralPath $entry.backup -Destination $entry.target -Force}
    else{Remove-Item -LiteralPath $entry.target}
}
Set-Content -LiteralPath (Join-Path $PSScriptRoot 'restored.txt') -Value (Get-Date -Format o)
Write-Output 'Panel de precarga y pantalla de carga restaurados. No se modifico el servidor.'
