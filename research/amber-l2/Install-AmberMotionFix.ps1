$ErrorActionPreference = 'Stop'
$AmberProject = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$AmberClient = Join-Path (Split-Path $AmberProject -Parent) 'l2'
$AmberTarget = Join-Path $AmberClient 'system-hud'
$AmberStage = Join-Path $PSScriptRoot 'exports\contract\motion-fix'
$AmberBackup = Join-Path $AmberProject 'backups\amber-contract-2026-10-09\motion-fix'
$AmberCodec = Join-Path $AmberProject 'tools\open-l2encdec-1.3.9\l2encdec_win.exe'
if (Get-Process L2 -ErrorAction SilentlyContinue) { throw 'Cerrar L2 antes de instalar.' }
function Get-AmberHash([string]$Path) { (Get-FileHash -LiteralPath $Path).Hash }
$AmberFiles = @{'npcgrp.dat'='npcgrp'; 'LineageNpc.int'='LineageNpc'}
foreach ($AmberName in $AmberFiles.Keys) {
    $AmberBase = $AmberFiles[$AmberName]
    $AmberRead = Join-Path $AmberStage ($AmberBase+'.preflight.raw')
    & $AmberCodec -o $AmberRead (Join-Path $AmberTarget $AmberName) | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "No se pudo leer $AmberName" }
    $AmberHash = Get-AmberHash $AmberRead
    if ($AmberHash -ne (Get-AmberHash (Join-Path $AmberStage ($AmberBase+'.before.raw'))) -and
        $AmberHash -ne (Get-AmberHash (Join-Path $AmberStage ($AmberBase+'.raw')))) {
        throw "$AmberName contiene otros cambios; integrar antes de instalar."
    }
    & $AmberCodec -o $AmberRead (Join-Path $AmberStage $AmberName) | Out-Null
    if ($LASTEXITCODE -ne 0 -or (Get-AmberHash $AmberRead) -ne (Get-AmberHash (Join-Path $AmberStage ($AmberBase+'.raw')))) {
        throw "Archivo preparado invalido: $AmberName"
    }
}
New-Item -ItemType Directory -Path $AmberBackup -Force | Out-Null
foreach ($AmberName in $AmberFiles.Keys) {
    $AmberSaved = Join-Path $AmberBackup $AmberName
    if (-not (Test-Path -LiteralPath $AmberSaved)) {
        Copy-Item -LiteralPath (Join-Path $AmberTarget $AmberName) -Destination $AmberSaved
    }
}
foreach ($AmberAsset in @('L2AmberNPCv5.ukx','L2AmberArcherV2.ukx')) {
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot ('exports\'+$AmberAsset)) -Destination (Join-Path $AmberClient ('animations\'+$AmberAsset)) -Force
}
foreach ($AmberName in $AmberFiles.Keys) {
    Copy-Item -LiteralPath (Join-Path $AmberStage $AmberName) -Destination (Join-Path $AmberTarget $AmberName) -Force
    if ((Get-AmberHash (Join-Path $AmberStage $AmberName)) -ne (Get-AmberHash (Join-Path $AmberTarget $AmberName))) {throw "Copia incompleta: $AmberName"}
}
Write-Host 'Amber: origen Fighter y movimientos de arco instalados en system-hud.'
