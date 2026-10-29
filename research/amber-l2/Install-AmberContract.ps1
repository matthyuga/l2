$ErrorActionPreference = 'Stop'
$AmberProject = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$AmberClient = Join-Path (Split-Path $AmberProject -Parent) 'l2'
$AmberTarget = Join-Path $AmberClient 'system-hud'
$AmberExport = Join-Path $PSScriptRoot 'exports\contract'
$AmberBackup = Join-Path $AmberProject 'backups\amber-contract-2026-10-09'
$AmberCodec = Join-Path $AmberProject 'tools\open-l2encdec-1.3.9\l2encdec_win.exe'
if (Get-Process L2 -ErrorAction SilentlyContinue) { throw 'Cerrar L2 antes de instalar.' }
$AmberCatalogs = @{
    'npcgrp.dat'='npcgrp'; 'NpcName-e.dat'='npcname'
    'skillgrp.dat'='skillgrp'; 'skillname-e.dat'='skillname'
}
function Get-AmberHash([string]$Path) { (Get-FileHash -LiteralPath $Path).Hash }
$AmberMotionStage = Join-Path $AmberExport 'motion-fix'
if (Test-Path -LiteralPath (Join-Path $AmberMotionStage 'npcgrp.dat')) {
    $AmberConfigRead = Join-Path $AmberMotionStage 'LineageNpc.preflight.raw'
    & $AmberCodec -o $AmberConfigRead (Join-Path $AmberTarget 'LineageNpc.int') | Out-Null
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo leer LineageNpc.int' }
    $AmberConfigHash = Get-AmberHash $AmberConfigRead
    if ($AmberConfigHash -ne (Get-AmberHash (Join-Path $AmberMotionStage 'LineageNpc.before.raw')) -and
        $AmberConfigHash -ne (Get-AmberHash (Join-Path $AmberMotionStage 'LineageNpc.raw'))) {
        throw 'LineageNpc.int contiene otros cambios; integrar antes de instalar.'
    }
}
# Validate every catalog before mutating any of them. Unknown edits need integration.
foreach ($AmberName in $AmberCatalogs.Keys) {
    $AmberBase = $AmberCatalogs[$AmberName]
    $AmberRead = Join-Path $AmberExport ($AmberBase+'.preflight.raw')
    & $AmberCodec -o $AmberRead (Join-Path $AmberTarget $AmberName) | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "No se pudo leer $AmberName" }
    $AmberHash = Get-AmberHash $AmberRead
    $AmberMotionRaw = Join-Path $AmberExport 'motion-fix\npcgrp.raw'
    $AmberMotionInstalled = $AmberBase -eq 'npcgrp' -and (Test-Path -LiteralPath $AmberMotionRaw) -and $AmberHash -eq (Get-AmberHash $AmberMotionRaw)
    if ($AmberHash -ne (Get-AmberHash (Join-Path $AmberBackup ($AmberBase+'.raw'))) -and
        $AmberHash -ne (Get-AmberHash (Join-Path $AmberExport ($AmberBase+'.raw'))) -and -not $AmberMotionInstalled) {
        throw "$AmberName contiene otros cambios; integrar antes de instalar."
    }
    & $AmberCodec -o $AmberRead (Join-Path $AmberExport $AmberName) | Out-Null
    if ($LASTEXITCODE -ne 0 -or (Get-AmberHash $AmberRead) -ne (Get-AmberHash (Join-Path $AmberExport ($AmberBase+'.raw')))) {
        throw "Catalogo nuevo invalido: $AmberName"
    }
}
foreach ($AmberAsset in @('L2AmberArcher.ukx','L2AmberArcherMotion.ukx')) {
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot ('exports\'+$AmberAsset)) -Destination (Join-Path $AmberClient ('animations\'+$AmberAsset)) -Force
}
Copy-Item -LiteralPath (Join-Path $AmberExport 'AmberEffects.usk') -Destination (Join-Path $AmberClient 'animations\AmberEffects.usk') -Force
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'tools\l2editor\L2Editor\AmberParticles.u') -Destination (Join-Path $AmberTarget 'AmberParticles.u') -Force
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'tools\l2editor\L2Editor\AmberParticles.u') -Destination (Join-Path $AmberClient 'system\AmberParticles.u') -Force
foreach ($AmberName in $AmberCatalogs.Keys) {
    Copy-Item -LiteralPath (Join-Path $AmberExport $AmberName) -Destination (Join-Path $AmberTarget $AmberName) -Force
}
if (Test-Path -LiteralPath (Join-Path $AmberExport 'motion-fix\npcgrp.dat')) {
    & (Join-Path $PSScriptRoot 'Install-AmberMotionFix.ps1')
}
Write-Host 'Contrato Amber instalado en system-hud. Usar 2-JUGAR.cmd.'
