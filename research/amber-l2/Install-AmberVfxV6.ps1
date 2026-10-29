$ErrorActionPreference='Stop'
$AmberProject=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$AmberClient=Join-Path (Split-Path $AmberProject -Parent) 'l2'
$AmberStage=Join-Path $PSScriptRoot 'exports/contract/combat-vfx-v6'
$AmberBackup=Join-Path $AmberProject ('backups/amber-vfx-v6-'+(Get-Date -Format 'yyyy-MM-dd-HHmmss'))
if(Get-CimInstance Win32_Process | Where-Object {$_.Name -match '^L2.*\.exe$'}){throw 'Cerrar L2 antes de reemplazar paquetes cargados.'}
if(Get-CimInstance Win32_Process | Where-Object {$_.Name -match '^java(w)?\.exe$' -and $_.CommandLine -match 'GameServer\.jar'}){throw 'Detener GameServer antes de instalar scripts.'}
function Get-AmberHash([string]$Path){(Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()}
$AmberCore='2e35d88f6050eb22619adf00ee0070494126ae0ed535dc33b0e4c1e18bc99349'
if((Get-AmberHash (Join-Path $AmberProject 'server/libs/GameServer.jar')) -ne $AmberCore){throw 'Core diferente del verificado; no instalar.'}
$AmberBaseline=Get-Content -LiteralPath (Join-Path $AmberStage 'server-baseline.json') -Raw | ConvertFrom-Json
foreach($AmberProperty in $AmberBaseline.PSObject.Properties){
 if((Get-AmberHash (Join-Path $AmberProject $AmberProperty.Name)) -ne $AmberProperty.Value){throw ('Script cambiado desde staging: '+$AmberProperty.Name)}
}
$AmberCodec=Join-Path $AmberProject 'tools/open-l2encdec-1.3.9/l2encdec_win.exe'
foreach($AmberCatalog in @(@('skillgrp','skillgrp.dat'),@('skillname','skillname-e.dat'))){
 $AmberPreflight=Join-Path $AmberStage ($AmberCatalog[0]+'.preflight.raw')
 & $AmberCodec -o $AmberPreflight (Join-Path $AmberClient ('system-hud/'+$AmberCatalog[1])) | Out-Null
 if($LASTEXITCODE -ne 0 -or (Get-AmberHash $AmberPreflight) -ne (Get-AmberHash (Join-Path $AmberStage ($AmberCatalog[0]+'.before.raw')))){throw 'Catalogo cambiado desde staging.'}
}
$AmberPalette=[IO.File]::ReadAllBytes((Join-Path $AmberClient 'systextures/AmberVfxMaterialsV4.utx'))
if([Text.Encoding]::Unicode.GetString($AmberPalette,0,28) -ne 'Lineage2Ver121'){throw 'Paleta V4 debe conservar formato cliente 121.'}
$AmberCopies=@(
 @('skillgrp.dat',(Join-Path $AmberClient 'system-hud/skillgrp.dat'),'client/system-hud/skillgrp.dat'),
 @('skillname-e.dat',(Join-Path $AmberClient 'system-hud/skillname-e.dat'),'client/system-hud/skillname-e.dat'),
 @('AmberEffectsV6.usk',(Join-Path $AmberClient 'animations/AmberEffectsV6.usk'),'client/animations/AmberEffectsV6.usk')
)
foreach($AmberPackage in @('AmberParticlesV6.u','DamageGlyphsV1.u')){
 foreach($AmberSystem in @('system-hud','system')){$AmberCopies+=,@($AmberPackage,(Join-Path $AmberClient ($AmberSystem+'/'+$AmberPackage)),('client/'+$AmberSystem+'/'+$AmberPackage))}
}
foreach($AmberTree in @('server/game/data/scripts','source/L2J_Mobius_CT_0_Interlude/dist/game/data/scripts','cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/dist/game/data/scripts')){
 foreach($AmberScript in @('custom/AmberContract/AmberContract.java','custom/AmberContract/AmberServitor.java','custom/WorldDamageNumbers/WorldDamageNumbers.java')){
  $AmberCopies+=,@(('server/'+$AmberScript),(Join-Path $AmberProject ($AmberTree+'/'+$AmberScript)),($AmberTree+'/'+$AmberScript))
 }
}
foreach($AmberCopy in $AmberCopies){if(-not(Test-Path -LiteralPath (Join-Path $AmberStage $AmberCopy[0]))){throw ('Archivo faltante: '+$AmberCopy[0])}}
New-Item -ItemType Directory -Path $AmberBackup -Force | Out-Null
foreach($AmberCopy in $AmberCopies){
 $AmberSource=Join-Path $AmberStage $AmberCopy[0]
 $AmberSaved=Join-Path $AmberBackup $AmberCopy[2]
 if(Test-Path -LiteralPath $AmberCopy[1]){
  New-Item -ItemType Directory -Path (Split-Path $AmberSaved -Parent) -Force | Out-Null
  Copy-Item -LiteralPath $AmberCopy[1] -Destination $AmberSaved
 }
 New-Item -ItemType Directory -Path (Split-Path $AmberCopy[1] -Parent) -Force | Out-Null
 Copy-Item -LiteralPath $AmberSource -Destination $AmberCopy[1] -Force
 if((Get-AmberHash $AmberSource) -ne (Get-AmberHash $AmberCopy[1])){throw 'Copia no coincide con staging.'}
}
Set-Content -LiteralPath (Join-Path $AmberStage 'installed-backup.path.txt') -Value $AmberBackup
Write-Host 'V6 instalado; falta comprobar visualmente .vfx prueba y skills de Amber.'
