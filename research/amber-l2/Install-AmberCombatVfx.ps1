$ErrorActionPreference='Stop'
$AmberProject=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$AmberClient=Join-Path (Split-Path $AmberProject -Parent) 'l2'
$AmberStage=Join-Path $PSScriptRoot 'exports/contract/combat-vfx-v2'
$AmberBackup=Join-Path $AmberProject 'backups/amber-combat-vfx-2026-10-10'
$AmberCodec=Join-Path $AmberProject 'tools/open-l2encdec-1.3.9/l2encdec_win.exe'
if(Get-Process L2 -ErrorAction SilentlyContinue){throw 'Cerrar L2 antes de instalar los efectos.'}
function Get-AmberHash([string]$Path){(Get-FileHash -LiteralPath $Path).Hash}
$AmberCatalogs=@{'npcgrp.dat'='npcgrp';'skillgrp.dat'='skillgrp';'skillname-e.dat'='skillname'}
foreach($AmberName in $AmberCatalogs.Keys){
 $AmberBase=$AmberCatalogs[$AmberName];$AmberRead=Join-Path $AmberStage ($AmberBase+'.preflight.raw')
 & $AmberCodec -o $AmberRead (Join-Path $AmberClient ('system-hud/'+$AmberName)) | Out-Null
 if($LASTEXITCODE -ne 0){throw "No se pudo leer $AmberName"}
 if((Get-AmberHash $AmberRead) -notin @((Get-AmberHash (Join-Path $AmberStage ($AmberBase+'.before.raw'))),(Get-AmberHash (Join-Path $AmberStage ($AmberBase+'.raw'))))){throw "Cambios desconocidos en $AmberName"}
}
$AmberAssets=@{
 (Join-Path $AmberStage 'AmberAnchorsV1.u')=@((Join-Path $AmberClient 'system-hud/AmberAnchorsV1.u'),(Join-Path $AmberClient 'system/AmberAnchorsV1.u'))
 (Join-Path $AmberStage 'AmberEffectsV2.usk')=@((Join-Path $AmberClient 'animations/AmberEffectsV2.usk'))
 (Join-Path $PSScriptRoot 'tools/l2editor/L2Editor/AmberParticlesV2.u')=@((Join-Path $AmberClient 'system-hud/AmberParticlesV2.u'),(Join-Path $AmberClient 'system/AmberParticlesV2.u'))
}
foreach($AmberSource in $AmberAssets.Keys){foreach($AmberDestination in $AmberAssets[$AmberSource]){
 if((Test-Path -LiteralPath $AmberDestination) -and (Get-AmberHash $AmberDestination) -ne (Get-AmberHash $AmberSource)){throw "Otra version en $AmberDestination"}
}}
New-Item -ItemType Directory -Path $AmberBackup -Force | Out-Null
foreach($AmberName in $AmberCatalogs.Keys){
 $AmberDestination=Join-Path $AmberClient ('system-hud/'+$AmberName);$AmberSaved=Join-Path $AmberBackup $AmberName
 if(-not(Test-Path -LiteralPath $AmberSaved)){Copy-Item -LiteralPath $AmberDestination -Destination $AmberSaved}
 Copy-Item -LiteralPath (Join-Path $AmberStage $AmberName) -Destination $AmberDestination -Force
}
foreach($AmberSource in $AmberAssets.Keys){foreach($AmberDestination in $AmberAssets[$AmberSource]){Copy-Item -LiteralPath $AmberSource -Destination $AmberDestination -Force}}
Write-Host 'Amber combat VFX V2 instalado: carga en arco, trazas de fuego y lluvia con marcador valido.'
