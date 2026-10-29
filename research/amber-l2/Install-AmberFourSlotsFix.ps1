$ErrorActionPreference='Stop'
$AmberProject=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$AmberClient=Join-Path (Split-Path $AmberProject -Parent) 'l2'
$AmberStage=Join-Path $PSScriptRoot 'exports/mmd-variants-fix4-20261023'
function Get-AmberHash([string]$Path){(Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()}
if(Get-CimInstance Win32_Process | Where-Object {$_.Name -match '^L2.*\.(exe|bin)$'}){throw 'Cerrar L2 y su dialogo Critical Error antes de reemplazar paquetes cargados.'}
$AmberCatalog=Get-Content -LiteralPath (Join-Path $AmberStage 'catalog-verification.json') -Raw | ConvertFrom-Json
if((Get-AmberHash (Join-Path $AmberClient 'system-hud/npcgrp.dat')) -ne $AmberCatalog.before_sha256){throw 'npcgrp cambio desde staging; integrar antes de copiar.'}
$AmberAssetChecks=Get-Content -LiteralPath (Join-Path $AmberStage 'asset-verification.json') -Raw | ConvertFrom-Json
if($AmberAssetChecks.Count -ne 2 -or @($AmberAssetChecks | Where-Object {$_.materials -ne 4 -or -not $_.geometry_coordinates_roundtrip -or $_.texture_pixel_roundtrip_count -ne 6}).Count){throw 'Falta verificacion nativa de cuatro materiales.'}
foreach($AmberLabel in @('v10','v14')){
 $AmberBuild=Get-Content -LiteralPath (Join-Path $AmberStage ($AmberLabel+'/build.json')) -Raw | ConvertFrom-Json
 if($AmberBuild.materials.Count -ne 4){throw 'Modelo excede el limite de GetNpcTexName.'}
}
$AmberProtected=@{}
foreach($AmberRelative in @('animations/L2AmberArcherV2.ukx','animations/L2AmberNPCv5.ukx','animations/L2AmberArcherMotion.ukx','system-hud/Interface.u','system-hud/Interface.xdat','system-hud/skillgrp.dat','system-hud/systemmsg-e.dat','system-hud/NpcName-e.dat','system-hud/l2.ini')){$AmberProtected[(Join-Path $AmberClient $AmberRelative)]=Get-AmberHash (Join-Path $AmberClient $AmberRelative)}
foreach($AmberRelative in @('server/libs/GameServer.jar','server/game/data/scripts/custom/AmberContract/AmberContract.java','server/game/data/scripts/custom/AmberContract/AmberServitor.java','server/game/data/scripts/custom/AmberContract/AmberModelVariants.java')){$AmberProtected[(Join-Path $AmberProject $AmberRelative)]=Get-AmberHash (Join-Path $AmberProject $AmberRelative)}
$AmberCopies=@(@('npcgrp.dat','system-hud/npcgrp.dat'),@('AmberMMD10.ukx','animations/AmberMMD10.ukx'),@('AmberMMD14.ukx','animations/AmberMMD14.ukx'))
foreach($AmberCopy in $AmberCopies){if(-not(Test-Path -LiteralPath (Join-Path $AmberStage $AmberCopy[0]))){throw 'Staging incompleto.'}}
$AmberBackup=Join-Path $AmberProject ('backups/amber-four-slots-'+(Get-Date -Format 'yyyyMMdd-HHmmss'))
$AmberChanged=@();$AmberHashes=@{}
try{
 foreach($AmberCopy in $AmberCopies){
  $AmberSource=Join-Path $AmberStage $AmberCopy[0];$AmberTarget=Join-Path $AmberClient $AmberCopy[1];$AmberSaved=Join-Path $AmberBackup $AmberCopy[1]
  New-Item -ItemType Directory -Path (Split-Path $AmberSaved -Parent) -Force | Out-Null
  Copy-Item -LiteralPath $AmberTarget -Destination $AmberSaved
  $AmberChanged+=,@($AmberTarget,$AmberSaved)
  Copy-Item -LiteralPath $AmberSource -Destination $AmberTarget -Force
  if((Get-AmberHash $AmberSource) -ne (Get-AmberHash $AmberTarget)){throw 'Copia no coincide con staging.'}
  $AmberHashes[$AmberTarget]=Get-AmberHash $AmberTarget
 }
 foreach($AmberPath in $AmberProtected.Keys){if((Get-AmberHash $AmberPath) -ne $AmberProtected[$AmberPath]){throw ('Cambio ajeno a correccion: '+$AmberPath)}}
}catch{foreach($AmberPair in $AmberChanged){Copy-Item -LiteralPath $AmberPair[1] -Destination $AmberPair[0] -Force};throw}
[ordered]@{installed_at=(Get-Date).ToString('o');backup=$AmberBackup;files=$AmberHashes;protected=$AmberProtected;cause='GetNpcTexName assertion index<5 with8 material slots';material_slots=4;client_verification='pending user playtest';server_restart_required=$false}|ConvertTo-Json -Depth 5|Set-Content -LiteralPath (Join-Path $AmberStage 'installed.json') -Encoding UTF8
Write-Host 'Correccion de cuatro materiales instalada; servidor intacto. Probar .ambers2 y .ambers3.'
Write-Host ('Backup: '+$AmberBackup)
