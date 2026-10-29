$ErrorActionPreference = 'Stop'
$AmberProject = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$AmberClient = Join-Path (Split-Path $AmberProject -Parent) 'l2'
$AmberTarget = Join-Path $AmberClient 'system-hud'
$AmberStage = Join-Path $PSScriptRoot 'exports\contract\visual-v3'
$AmberCodec = Join-Path $AmberProject 'tools\open-l2encdec-1.3.9\l2encdec_win.exe'
$AmberBackup = Join-Path $AmberProject 'backups\amber-visual-v3-2026-10-10'
if (Get-Process L2 -ErrorAction SilentlyContinue) { throw 'Cerrar L2 antes de instalar.' }
New-Item -ItemType Directory -Path $AmberBackup -Force | Out-Null
function Get-AmberHash([string]$Path) { (Get-FileHash -LiteralPath $Path).Hash }
$AmberCatalogs = @{'npcgrp.dat'='npcgrp'; 'skillgrp.dat'='skillgrp'; 'LineageNpc.int'='LineageNpc'}
foreach ($AmberName in $AmberCatalogs.Keys) {
    $AmberBase = $AmberCatalogs[$AmberName]
    $AmberRead = Join-Path $AmberStage ($AmberBase+'.preflight.raw')
    & $AmberCodec -o $AmberRead (Join-Path $AmberTarget $AmberName) | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "No se pudo leer $AmberName" }
    $AmberHash = Get-AmberHash $AmberRead
    if ($AmberHash -ne (Get-AmberHash (Join-Path $AmberStage ($AmberBase+'.before.raw'))) -and
        $AmberHash -ne (Get-AmberHash (Join-Path $AmberStage ($AmberBase+'.raw')))) {
        throw "$AmberName contiene otros cambios: integrar antes de instalar."
    }
    & $AmberCodec -o $AmberRead (Join-Path $AmberStage $AmberName) | Out-Null
    if ($LASTEXITCODE -ne 0 -or (Get-AmberHash $AmberRead) -ne (Get-AmberHash (Join-Path $AmberStage ($AmberBase+'.raw')))) {
        throw "Catalogo nuevo invalido: $AmberName"
    }
}
$AmberAssets = @{
    (Join-Path $AmberStage 'AmberActorsV1.u') = @((Join-Path $AmberTarget 'AmberActorsV1.u'),(Join-Path $AmberClient 'system\AmberActorsV1.u'))
    (Join-Path $AmberStage 'AmberIconsV1.client.utx') = @((Join-Path $AmberClient 'systextures\AmberIconsV1.utx'))
    (Join-Path $PSScriptRoot 'tools\l2editor\L2Editor\AmberParticles.u') = @((Join-Path $AmberTarget 'AmberParticles.u'),(Join-Path $AmberClient 'system\AmberParticles.u'))
}
foreach ($AmberSource in $AmberAssets.Keys) {
    if (-not (Test-Path -LiteralPath $AmberSource)) { throw "Falta $AmberSource" }
    foreach ($AmberDestination in $AmberAssets[$AmberSource]) {
        $AmberKnownRawIcons = $AmberSource -eq (Join-Path $AmberStage 'AmberIconsV1.client.utx') -and
            (Test-Path -LiteralPath $AmberDestination) -and
            (Get-AmberHash $AmberDestination) -eq (Get-AmberHash (Join-Path $AmberStage 'AmberIconsV1.utx'))
        if ((Test-Path -LiteralPath $AmberDestination) -and (Get-AmberHash $AmberDestination) -ne (Get-AmberHash $AmberSource) -and -not $AmberKnownRawIcons) {
            throw "$AmberDestination contiene otra version: integrar antes de instalar."
        }
    }
}
foreach ($AmberName in $AmberCatalogs.Keys) {
    $AmberSaved = Join-Path $AmberBackup $AmberName
    if (-not (Test-Path -LiteralPath $AmberSaved)) { Copy-Item -LiteralPath (Join-Path $AmberTarget $AmberName) -Destination $AmberSaved }
    Copy-Item -LiteralPath (Join-Path $AmberStage $AmberName) -Destination (Join-Path $AmberTarget $AmberName) -Force
}
foreach ($AmberSource in $AmberAssets.Keys) {
    foreach ($AmberDestination in $AmberAssets[$AmberSource]) {
        $AmberSaved = Join-Path $AmberBackup ([IO.Path]::GetFileName($AmberDestination))
        if ((Test-Path -LiteralPath $AmberDestination) -and -not (Test-Path -LiteralPath $AmberSaved)) {
            Copy-Item -LiteralPath $AmberDestination -Destination $AmberSaved
        }
        Copy-Item -LiteralPath $AmberSource -Destination $AmberDestination -Force
    }
}
Write-Host 'Amber visual V3 instalada: clase aislada, iconos propios y particulas en las rutas de carga del cliente.'
