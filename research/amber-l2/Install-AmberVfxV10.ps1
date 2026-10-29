$ErrorActionPreference='Stop'
$AmberProject=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$AmberClient=Join-Path (Split-Path $AmberProject -Parent) 'l2'
$AmberStage=Join-Path $PSScriptRoot 'exports/contract/combat-vfx-v10'
$AmberBackup=Join-Path $AmberProject ('backups/amber-vfx-v10-'+(Get-Date -Format 'yyyy-MM-dd-HHmmss'))
if(Get-CimInstance Win32_Process | Where-Object {$_.Name -match '^L2.*\.exe$'}){throw 'Cerrar L2 para recargar skillgrp y no reemplazar archivos cargados.'}
if(Get-CimInstance Win32_Process | Where-Object {$_.Name -match '^java(w)?\.exe$' -and $_.CommandLine -match 'GameServer\.jar'}){throw 'Detener GameServer antes de instalar la notificacion de impactos.'}
function Get-AmberHash([string]$Path){(Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash}
# Preserve the concurrently installed, verified class-catalog core (continuity 20).
if((Get-AmberHash (Join-Path $AmberProject 'server/libs/GameServer.jar')) -ne 'c2f649806ee4248e5d9cc507ea36088d2799d12c6dc4b61c20d0500111d0d888'){throw 'Core diferente del catalogo por clase verificado.'}
$AmberBaseline=Get-Content -LiteralPath (Join-Path $AmberStage 'server-baseline.json') -Raw | ConvertFrom-Json
foreach($AmberProperty in $AmberBaseline.PSObject.Properties){
 if((Get-AmberHash (Join-Path $AmberProject $AmberProperty.Name)) -ne $AmberProperty.Value){throw ('Script cambiado desde staging: '+$AmberProperty.Name)}
}
$AmberCodec=Join-Path $AmberProject 'tools/open-l2encdec-1.3.9/l2encdec_win.exe'
foreach($AmberCatalog in @(@('skillgrp','skillgrp.dat'),@('skillname','skillname-e.dat'),@('systemmsg','systemmsg-e.dat'))){
 $AmberPreflight=Join-Path $AmberStage ($AmberCatalog[0]+'.preflight.raw')
 & $AmberCodec -o $AmberPreflight (Join-Path $AmberClient ('system-hud/'+$AmberCatalog[1])) | Out-Null
 if($LASTEXITCODE -ne 0 -or (Get-AmberHash $AmberPreflight) -ne (Get-AmberHash (Join-Path $AmberStage ($AmberCatalog[0]+'.before.raw')))){throw 'Catalogo cambiado desde staging.'}
}
$AmberCopies=@(
 @('skillgrp.dat','system-hud/skillgrp.dat'),
 @('skillname-e.dat','system-hud/skillname-e.dat'),
 @('systemmsg-e.dat','system-hud/systemmsg-e.dat'),
 @('AmberEffectsV10.usk','animations/AmberEffectsV10.usk'),
 @('AmberParticlesV10.u','system-hud/AmberParticlesV10.u'),
 @('AmberParticlesV10.u','system/AmberParticlesV10.u'),
 @('AmberMaterialsV10.u','system-hud/AmberMaterialsV10.u'),
 @('AmberMaterialsV10.u','system/AmberMaterialsV10.u'),
 @('DamageGlyphsV4.u','system-hud/DamageGlyphsV4.u'),
 @('DamageGlyphsV4.u','system/DamageGlyphsV4.u')
)
foreach($AmberCopy in $AmberCopies){if(-not(Test-Path -LiteralPath (Join-Path $AmberStage $AmberCopy[0]))){throw 'Staging incompleto.'}}
foreach($AmberCopy in $AmberCopies){
 $AmberSource=Join-Path $AmberStage $AmberCopy[0];$AmberTarget=Join-Path $AmberClient $AmberCopy[1]
 if(Test-Path -LiteralPath $AmberTarget){
  $AmberSaved=Join-Path $AmberBackup $AmberCopy[1]
  New-Item -ItemType Directory -Path (Split-Path $AmberSaved -Parent) -Force | Out-Null
  Copy-Item -LiteralPath $AmberTarget -Destination $AmberSaved
 }
 Copy-Item -LiteralPath $AmberSource -Destination $AmberTarget -Force
 if((Get-AmberHash $AmberSource) -ne (Get-AmberHash $AmberTarget)){throw 'Copia no coincide con staging.'}
}
foreach($AmberTree in @('server/game/data/scripts','source/L2J_Mobius_CT_0_Interlude/dist/game/data/scripts','cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/dist/game/data/scripts')){
 foreach($AmberName in @('AmberContract.java','AmberContractVerification.java')){
  $AmberRelative=$AmberTree+'/custom/AmberContract/'+$AmberName
  $AmberSource=Join-Path $AmberStage ('server/custom/AmberContract/'+$AmberName)
  $AmberTarget=Join-Path $AmberProject $AmberRelative
  $AmberSaved=Join-Path $AmberBackup $AmberRelative
  New-Item -ItemType Directory -Path (Split-Path $AmberSaved -Parent) -Force | Out-Null
  Copy-Item -LiteralPath $AmberTarget -Destination $AmberSaved
  Copy-Item -LiteralPath $AmberSource -Destination $AmberTarget -Force
  if((Get-AmberHash $AmberSource) -ne (Get-AmberHash $AmberTarget)){throw 'Copia Java no coincide con staging.'}
 }
}
Set-Content -LiteralPath (Join-Path $AmberStage 'installed-backup.path.txt') -Value $AmberBackup
Write-Host 'V10 cliente y notificacion de impactos instalados. Iniciar GameServer; falta revision visual en juego.'
