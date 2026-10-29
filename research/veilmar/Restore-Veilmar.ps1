$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$client=(Resolve-Path (Join-Path $root '../l2')).Path
if(Get-Process -Name L2 -ErrorAction SilentlyContinue){throw 'Cierra el cliente L2 antes de restaurar.'}
if(Get-NetTCPConnection -LocalPort 7777 -State Listen -ErrorAction SilentlyContinue){throw 'Deten el GameServer con 5-DETENER-SERVIDOR.cmd antes de restaurar.'}
$manifest=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'installation.json') -Raw | ConvertFrom-Json
# Check every target and original BEFORE making changes. No recursive deletions.
foreach($entry in $manifest.files){
    $target=[IO.Path]::GetFullPath($entry.path)
    if(-not ($target.StartsWith($root+'\',[StringComparison]::OrdinalIgnoreCase) -or $target.StartsWith($client+'\',[StringComparison]::OrdinalIgnoreCase))){throw "Ruta fuera del proyecto: $target"}
    if(-not (Test-Path -LiteralPath $target) -or (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash -ne $entry.after_sha256){throw "Archivo modificado despues de instalar Veilmar: $target"}
    if($entry.existed -and ((Get-FileHash -LiteralPath $entry.backup -Algorithm SHA256).Hash -ne $entry.before_sha256)){throw "Respaldo no valido: $($entry.backup)"}
}
foreach($entry in $manifest.files){
    if($entry.existed){Copy-Item -LiteralPath $entry.backup -Destination $entry.path -Force}
    else{Remove-Item -LiteralPath $entry.path}
}
Set-Content -LiteralPath (Join-Path $PSScriptRoot 'restored.txt') -Value (Get-Date -Format o)
Write-Output 'Veilmar restaurado al estado anterior. Puedes iniciar el servidor normalmente.'
