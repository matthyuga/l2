$ErrorActionPreference='Stop'
$AmberProject=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$AmberClient=Join-Path (Split-Path $AmberProject -Parent) 'l2'
$AmberStage=Join-Path $PSScriptRoot 'exports/mmd-variants-20261023'
foreach($AmberVariant in @('v10','v14')){
 $AmberBuild=Get-Content -LiteralPath (Join-Path $AmberStage ($AmberVariant+'/build.json')) -Raw | ConvertFrom-Json
 if($AmberBuild.materials.Count -gt 5){throw 'Paquete inicial incompatible: GetNpcTexName admite indices0..4. Usar Install-AmberFourSlotsFix.ps1.'}
}
function Get-AmberHash([string]$Path){(Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()}
if(Get-CimInstance Win32_Process | Where-Object {$_.Name -match '^L2.*\.exe$'}){throw 'Cerrar L2 antes de instalar los catalogos.'}
if(Get-CimInstance Win32_Process | Where-Object {$_.Name -match '^java(w)?\.exe$' -and $_.CommandLine -match 'GameServer\.jar' -and $_.CommandLine -notmatch 'l2-hellgames|l2-academy'}){throw 'GameServer activo: no reemplazar scripts cargados.'}
if(-not(Test-Path -LiteralPath (Join-Path $AmberStage 'asset-verification.json')) -or -not(Test-Path -LiteralPath (Join-Path $AmberStage 'pose-verification.json'))){throw 'Falta verificacion de modelos/poses.'}
$AmberCatalogs=Get-Content -LiteralPath (Join-Path $AmberStage 'catalog-verification.json') -Raw | ConvertFrom-Json
foreach($AmberProperty in $AmberCatalogs.PSObject.Properties){if((Get-AmberHash (Join-Path $AmberClient ('system-hud/'+$AmberProperty.Name))) -ne $AmberProperty.Value.before_sha256){throw ('Catalogo modificado desde staging: '+$AmberProperty.Name)}}
$AmberBaseline=Get-Content -LiteralPath (Join-Path $AmberStage 'server-baseline.json') -Raw | ConvertFrom-Json
foreach($AmberProperty in $AmberBaseline.PSObject.Properties){
 $AmberTarget=Join-Path $AmberProject $AmberProperty.Name
 if($null -eq $AmberProperty.Value){if(Test-Path -LiteralPath $AmberTarget){throw 'Ya existe un nuevo script; revisar colision.'}}
 elseif((Get-AmberHash $AmberTarget) -ne $AmberProperty.Value){throw ('Script cambiado desde staging: '+$AmberProperty.Name)}
}
$AmberCopies=@(
 @('npcgrp.dat',(Join-Path $AmberClient 'system-hud/npcgrp.dat'),'client/system-hud/npcgrp.dat'),
 @('NpcName-e.dat',(Join-Path $AmberClient 'system-hud/NpcName-e.dat'),'client/system-hud/NpcName-e.dat')
)
foreach($AmberPackage in @('AmberMMD10.ukx','AmberMMD14.ukx')){$AmberCopies+=,@($AmberPackage,(Join-Path $AmberClient ('animations/'+$AmberPackage)),('client/animations/'+$AmberPackage))}
foreach($AmberTree in @('server/game/data','source/L2J_Mobius_CT_0_Interlude/dist/game/data','cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/dist/game/data')){
 foreach($AmberName in @('AmberContract.java','AmberServitor.java','AmberModelVariants.java','AmberModelVariantsVerification.java')){
  $AmberRelative=$AmberTree+'/scripts/custom/AmberContract/'+$AmberName
  $AmberCopies+=,@(('server/custom/AmberContract/'+$AmberName),(Join-Path $AmberProject $AmberRelative),$AmberRelative)
 }
 $AmberRelative=$AmberTree+'/stats/npcs/custom/amber_model_variants.xml'
 $AmberCopies+=,@('server/amber_model_variants.xml',(Join-Path $AmberProject $AmberRelative),$AmberRelative)
}
foreach($AmberCopy in $AmberCopies){if(-not(Test-Path -LiteralPath (Join-Path $AmberStage $AmberCopy[0]))){throw ('Staging incompleto: '+$AmberCopy[0])}}
# Preserve originals and unrelated camera/interface/skill changes exactly.
$AmberProtected=@{}
foreach($AmberFile in @('server/libs/GameServer.jar')){$AmberProtected[(Join-Path $AmberProject $AmberFile)]=Get-AmberHash (Join-Path $AmberProject $AmberFile)}
foreach($AmberFile in @('animations/L2AmberNPCv5.ukx','animations/L2AmberArcherV2.ukx','animations/L2AmberArcherMotion.ukx','system-hud/Interface.u','system-hud/Interface.xdat','system-hud/l2.ini','system-hud/skillgrp.dat','system-hud/systemmsg-e.dat')){$AmberProtected[(Join-Path $AmberClient $AmberFile)]=Get-AmberHash (Join-Path $AmberClient $AmberFile)}
$AmberBackup=Join-Path $AmberProject ('backups/amber-three-models-'+(Get-Date -Format 'yyyyMMdd-HHmmss'))
New-Item -ItemType Directory -Path $AmberBackup -Force | Out-Null
$AmberHistory=@();$AmberInstalled=@{}
try{
 foreach($AmberCopy in $AmberCopies){
  $AmberSource=Join-Path $AmberStage $AmberCopy[0];$AmberTarget=$AmberCopy[1];$AmberSaved=Join-Path $AmberBackup $AmberCopy[2];$AmberExisted=Test-Path -LiteralPath $AmberTarget
  if($AmberExisted){New-Item -ItemType Directory -Path (Split-Path $AmberSaved -Parent) -Force | Out-Null;Copy-Item -LiteralPath $AmberTarget -Destination $AmberSaved}
  $AmberHistory+=,@($AmberTarget,$AmberSaved,$AmberExisted)
  New-Item -ItemType Directory -Path (Split-Path $AmberTarget -Parent) -Force | Out-Null
  Copy-Item -LiteralPath $AmberSource -Destination $AmberTarget -Force
  if((Get-AmberHash $AmberSource) -ne (Get-AmberHash $AmberTarget)){throw 'Copia instalada diferente de staging.'}
  $AmberInstalled[$AmberTarget]=Get-AmberHash $AmberTarget
 }
 foreach($AmberFile in $AmberProtected.Keys){if((Get-AmberHash $AmberFile) -ne $AmberProtected[$AmberFile]){throw ('Cambio ajeno a variantes: '+$AmberFile)}}
}catch{
 foreach($AmberEntry in $AmberHistory){if($AmberEntry[2]){Copy-Item -LiteralPath $AmberEntry[1] -Destination $AmberEntry[0] -Force}else{Remove-Item -LiteralPath $AmberEntry[0] -Force}}
 throw
}
[ordered]@{installed_at=(Get-Date).ToString('o');backup=$AmberBackup;files=$AmberInstalled;protected=$AmberProtected;models=@('Actual Koikatsu','MMD1.0','MMD1.4 Amber2.0');in_game_validation='pending'} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $AmberStage 'installed.json') -Encoding UTF8
Write-Host 'Tres modelos instalados. Iniciar GameServer. Selector: .ambers (1 actual, 2 MMD1.0, 3 MMD1.4).'
Write-Host ('Backup: '+$AmberBackup)
