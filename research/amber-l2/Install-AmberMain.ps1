$ErrorActionPreference = 'Stop'
$AmberLab = $PSScriptRoot
$AmberProject = Split-Path (Split-Path $AmberLab -Parent) -Parent
$AmberClient = Join-Path (Split-Path $AmberProject -Parent) 'l2'
$AmberMain = Join-Path $AmberClient 'system-hud'
$AmberCodec = Join-Path $AmberProject 'tools\open-l2encdec-1.3.9\l2encdec_win.exe'
$AmberScratch = Join-Path $AmberLab 'exports\main-client-setup'
New-Item -ItemType Directory -Path $AmberScratch -Force | Out-Null

function Decode-AmberCatalog([string]$CatalogSource, [string]$DecodedTarget) {
    & $AmberCodec -o $DecodedTarget $CatalogSource | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "No se pudo leer $CatalogSource" }
}
function Get-AmberHash([string]$CatalogPath) {
    (Get-FileHash -LiteralPath $CatalogPath -Algorithm SHA256).Hash
}

foreach ($AmberAsset in @('L2AmberNPCv4.ukx', 'L2AmberMotionv3.ukx')) {
    if ((Get-AmberHash (Join-Path $AmberClient ('animations\'+$AmberAsset))) -ne
        (Get-AmberHash (Join-Path $AmberLab ('exports\'+$AmberAsset)))) {
        throw "El recurso instalado no coincide con la version validada: $AmberAsset"
    }
}

$AmberCatalogs = @(
    @{ Name='npcgrp.dat'; Base='npcgrp.raw'; Patched='npcgrp-amber.raw' },
    @{ Name='NpcName-e.dat'; Base='npcname.raw'; Patched='npcname-amber.raw' }
)
# Preflight both catalogs before changing either. Do not overwrite unrelated custom rows.
foreach ($AmberCatalog in $AmberCatalogs) {
    $AmberTarget = Join-Path $AmberMain $AmberCatalog.Name
    $AmberDecoded = Join-Path $AmberScratch ($AmberCatalog.Name+'.before.raw')
    Decode-AmberCatalog $AmberTarget $AmberDecoded
    $AmberBeforeHash = Get-AmberHash $AmberDecoded
    $AmberBaseHash = Get-AmberHash (Join-Path $AmberLab ('exports\'+$AmberCatalog.Base))
    $AmberPatchedHash = Get-AmberHash (Join-Path $AmberLab ('exports\'+$AmberCatalog.Patched))
    if ($AmberBeforeHash -ne $AmberBaseHash -and $AmberBeforeHash -ne $AmberPatchedHash) {
        throw "El catalogo $AmberTarget contiene otros cambios. Integrar la fila de Amber antes de instalar."
    }
    $AmberSourceDecoded = Join-Path $AmberScratch ($AmberCatalog.Name+'.source.raw')
    Decode-AmberCatalog (Join-Path $AmberLab ('exports\'+$AmberCatalog.Name)) $AmberSourceDecoded
    if ((Get-AmberHash $AmberSourceDecoded) -ne $AmberPatchedHash) {
        throw "El catalogo cifrado de Amber no coincide con el contenido validado."
    }
}

$AmberHudHashes = @{}
foreach ($AmberHudFile in @('Interface.u','Interface.xdat')) {
    $AmberHudPath = Join-Path $AmberMain $AmberHudFile
    if (Test-Path -LiteralPath $AmberHudPath) { $AmberHudHashes[$AmberHudFile] = Get-AmberHash $AmberHudPath }
}
$AmberBackup = Join-Path $AmberLab ('backups\main-client-before-amber-'+(Get-Date -Format 'yyyyMMdd-HHmmss'))
New-Item -ItemType Directory -Path $AmberBackup | Out-Null
foreach ($AmberCatalog in $AmberCatalogs) {
    Copy-Item -LiteralPath (Join-Path $AmberMain $AmberCatalog.Name) -Destination (Join-Path $AmberBackup $AmberCatalog.Name)
}
try {
    foreach ($AmberCatalog in $AmberCatalogs) {
        $AmberTarget = Join-Path $AmberMain $AmberCatalog.Name
        Copy-Item -LiteralPath (Join-Path $AmberLab ('exports\'+$AmberCatalog.Name)) -Destination $AmberTarget -Force
        $AmberVerified = Join-Path $AmberScratch ($AmberCatalog.Name+'.installed.raw')
        Decode-AmberCatalog $AmberTarget $AmberVerified
        if ((Get-AmberHash $AmberVerified) -ne (Get-AmberHash (Join-Path $AmberLab ('exports\'+$AmberCatalog.Patched)))) {
            throw "La verificacion del catalogo instalado fallo: $AmberTarget"
        }
    }
} catch {
    foreach ($AmberCatalog in $AmberCatalogs) {
        Copy-Item -LiteralPath (Join-Path $AmberBackup $AmberCatalog.Name) -Destination (Join-Path $AmberMain $AmberCatalog.Name) -Force
    }
    throw
}
foreach ($AmberHudFile in $AmberHudHashes.Keys) {
    if ((Get-AmberHash (Join-Path $AmberMain $AmberHudFile)) -ne $AmberHudHashes[$AmberHudFile]) {
        throw "El archivo del HUD cambio durante la instalacion: $AmberHudFile"
    }
}
$AmberReport = [ordered]@{
    profile=$AmberMain; launcher=(Join-Path $AmberProject '2-JUGAR.cmd'); revision=4; display_id=59001
    modified_files=@($AmberCatalogs | ForEach-Object { Join-Path $AmberMain $_.Name })
    original_rows_preserved=$true; installed_decryption_verified=$true; hud_unchanged=$true
    backup=$AmberBackup; client_restart_required=$true; in_game_validation_main_profile=$false
}
$AmberReport | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $AmberLab 'reports\main-client-installation.json') -Encoding UTF8
Write-Host 'Amber v4 integrada en system-hud. Abrir 2-JUGAR.cmd despues de cerrar el cliente anterior.'
Write-Host "Copia de los catalogos anteriores: $AmberBackup"
