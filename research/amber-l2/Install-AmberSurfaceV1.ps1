$ErrorActionPreference = 'Stop'
$SurfaceRoot = $PSScriptRoot
$SurfaceProject = Split-Path (Split-Path $SurfaceRoot -Parent) -Parent
$SurfaceClient = Join-Path (Split-Path $SurfaceProject -Parent) 'l2'
$SurfaceStage = Join-Path $SurfaceRoot 'exports\surface-v1'
if (Get-Process l2 -ErrorAction SilentlyContinue) { throw 'Cerrá L2 antes de instalar materiales; no se cambiarán archivos cargados.' }
$SurfaceProof = Get-Content (Join-Path $SurfaceStage 'native-proof.json') -Raw | ConvertFrom-Json
if (-not $SurfaceProof.mask_pixels_exact -or $SurfaceProof.packages.Count -ne 2) { throw 'Falta la verificación nativa de materiales.' }
$SurfaceMaskBytes = [IO.File]::ReadAllBytes((Join-Path $SurfaceStage 'AmberSurfaceV1.utx'))
if ([Text.Encoding]::Unicode.GetString($SurfaceMaskBytes,0,28) -ne 'Lineage2Ver121' -or -not $SurfaceProof.texture_wrapper.roundtrip -or -not $SurfaceProof.texture_wrapper.crc32) { throw 'Falta envoltura cliente 121 validada.' }
if ((Get-FileHash -LiteralPath (Join-Path $SurfaceStage 'AmberSurfaceV1.utx')).Hash.ToLower() -ne $SurfaceProof.texture_wrapper.sha256) { throw 'Máscaras modificadas después de la validación.' }
$SurfaceAlreadyInstalled = $true
foreach ($SurfacePackage in $SurfaceProof.packages) {
    if ((Get-FileHash -LiteralPath (Join-Path $SurfaceClient ('animations\'+$SurfacePackage.package+'.ukx'))).Hash.ToLower() -ne $SurfacePackage.staged_sha256) { $SurfaceAlreadyInstalled=$false }
}
$SurfaceMaskTarget=Join-Path $SurfaceClient 'systextures\AmberSurfaceV1.utx'
if (-not (Test-Path -LiteralPath $SurfaceMaskTarget)) { $SurfaceAlreadyInstalled=$false }
elseif ((Get-FileHash -LiteralPath $SurfaceMaskTarget).Hash.ToLower() -ne $SurfaceProof.texture_wrapper.sha256) { $SurfaceAlreadyInstalled=$false }
if ($SurfaceAlreadyInstalled) { Write-Host 'Amber V1 ya instalada y validada; no se cambió nada.'; exit 0 }
$SurfaceFiles = @()
foreach ($SurfacePackage in $SurfaceProof.packages) {
    if (-not $SurfacePackage.native_shader_load -or -not $SurfacePackage.native_psk_unchanged) { throw 'Paquete sin validar.' }
    $SurfaceRel = 'animations\'+$SurfacePackage.package+'.ukx'
    $SurfaceInstalled = Join-Path $SurfaceClient $SurfaceRel
    $SurfaceCompiled = Join-Path $SurfaceStage ($SurfacePackage.package+'.ukx')
    if ((Get-FileHash -LiteralPath $SurfaceInstalled).Hash.ToLower() -ne $SurfacePackage.source_sha256) { throw "Otro proceso modificó $SurfaceRel. No sobrescribir." }
    if ((Get-FileHash -LiteralPath $SurfaceCompiled).Hash.ToLower() -ne $SurfacePackage.staged_sha256) { throw 'El paquete preparado cambió después de validarlo.' }
    $SurfaceFiles += [pscustomobject]@{ relative=$SurfaceRel; source=$SurfaceCompiled }
}
$SurfaceFiles += [pscustomobject]@{relative='systextures\AmberSurfaceV1.utx'; source=(Join-Path $SurfaceStage 'AmberSurfaceV1.utx')}
$SurfaceBackup = Join-Path $SurfaceProject ('backups\amber-surface-v1-'+(Get-Date -Format 'yyyyMMdd-HHmmss'))
New-Item -ItemType Directory -Path $SurfaceBackup | Out-Null
$SurfaceManifest = @()
foreach ($SurfaceFile in $SurfaceFiles) {
    $SurfaceTarget = Join-Path $SurfaceClient $SurfaceFile.relative
    $SurfaceSaved = Join-Path $SurfaceBackup $SurfaceFile.relative
    $SurfaceExists = Test-Path -LiteralPath $SurfaceTarget
    $SurfaceOldHash = $null
    if ($SurfaceExists) {
        New-Item -ItemType Directory -Path (Split-Path $SurfaceSaved -Parent) -Force | Out-Null
        Copy-Item -LiteralPath $SurfaceTarget -Destination $SurfaceSaved
        $SurfaceOldHash = (Get-FileHash -LiteralPath $SurfaceSaved).Hash
    }
    $SurfaceManifest += [pscustomobject]@{ relative=$SurfaceFile.relative; existed=$SurfaceExists; before_sha256=$SurfaceOldHash; installed_sha256=(Get-FileHash -LiteralPath $SurfaceFile.source).Hash }
}
try {
    foreach ($SurfaceFile in $SurfaceFiles) {
        Copy-Item -LiteralPath $SurfaceFile.source -Destination (Join-Path $SurfaceClient $SurfaceFile.relative) -Force
        if ((Get-FileHash -LiteralPath $SurfaceFile.source).Hash -ne (Get-FileHash -LiteralPath (Join-Path $SurfaceClient $SurfaceFile.relative)).Hash) { throw 'Hash instalado incorrecto.' }
    }
} catch {
    foreach ($SurfaceEntry in $SurfaceManifest | Where-Object existed) { Copy-Item -LiteralPath (Join-Path $SurfaceBackup $SurfaceEntry.relative) -Destination (Join-Path $SurfaceClient $SurfaceEntry.relative) -Force }
    throw
}
@{client=$SurfaceClient;backup=$SurfaceBackup;files=$SurfaceManifest;installed=(Get-Date -Format o);ingame_verified=$false} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $SurfaceStage 'installation.json') -Encoding UTF8
$SurfaceManifest | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $SurfaceBackup 'manifest.json') -Encoding UTF8
@'
$ErrorActionPreference='Stop'
if(Get-Process l2 -ErrorAction SilentlyContinue){throw 'Cerrá L2 antes de restaurar.'}
$RestoreProject=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$RestoreClient=Join-Path (Split-Path $RestoreProject -Parent) 'l2'
$RestoreEntries=Get-Content (Join-Path $PSScriptRoot 'manifest.json') -Raw | ConvertFrom-Json
foreach($RestoreEntry in $RestoreEntries){
 $RestoreTarget=Join-Path $RestoreClient $RestoreEntry.relative
 if((Get-FileHash -LiteralPath $RestoreTarget).Hash -ne $RestoreEntry.installed_sha256){throw "Archivo modificado después: $RestoreTarget"}
 if($RestoreEntry.existed -and (Get-FileHash -LiteralPath (Join-Path $PSScriptRoot $RestoreEntry.relative)).Hash -ne $RestoreEntry.before_sha256){throw 'Backup no coincide.'}
}
foreach($RestoreEntry in $RestoreEntries | Where-Object existed){Copy-Item -LiteralPath (Join-Path $PSScriptRoot $RestoreEntry.relative) -Destination (Join-Path $RestoreClient $RestoreEntry.relative) -Force}
Write-Host 'Materiales anteriores restaurados. La máscara nueva queda sin uso; no hace falta reiniciar el servidor.'
'@ | Set-Content -LiteralPath (Join-Path $SurfaceBackup 'Restore.ps1') -Encoding UTF8
Write-Host "Amber: materiales V1 instalados para NPC y summon. Backup: $SurfaceBackup"
Write-Host 'No se reinició el servidor ni se modificaron catálogos, IA o estadísticas. Falta valoración visual dentro de L2.'
