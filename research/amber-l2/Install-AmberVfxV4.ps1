$ErrorActionPreference='Stop'
$AmberProject=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$AmberClient=Join-Path (Split-Path $AmberProject -Parent) 'l2'
$AmberStage=Join-Path $PSScriptRoot 'exports/contract/combat-vfx-v4'
$AmberBackup=Join-Path $AmberProject 'backups/amber-vfx-v4-2026-10-10'
if(Get-Process L2 -ErrorAction SilentlyContinue){throw 'Cerrar L2 antes de instalar VFX V4; no reemplazar paquetes cargados.'}
if(Get-CimInstance Win32_Process | Where-Object {$_.Name -eq 'java.exe' -and $_.CommandLine -match 'GameServer\.jar'}){throw 'Detener GameServer antes de instalar los scripts V4.'}
function Get-AmberHash([string]$Path){(Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash}
$AmberCodec=Join-Path $AmberProject 'tools/open-l2encdec-1.3.9/l2encdec_win.exe'
$AmberRead=Join-Path $AmberStage 'skillgrp.preflight.raw'
& $AmberCodec -o $AmberRead (Join-Path $AmberClient 'system-hud/skillgrp.dat') | Out-Null
if($LASTEXITCODE -ne 0){throw 'No se pudo descifrar el catalogo instalado'}
if((Get-AmberHash $AmberRead) -notin @((Get-AmberHash (Join-Path $AmberStage 'skillgrp.before.raw')),(Get-AmberHash (Join-Path $AmberStage 'skillgrp.raw')))){throw 'Cambios desconocidos en skillgrp.dat'}
$AmberCopies=@(
 @((Join-Path $AmberStage 'skillgrp.dat'),(Join-Path $AmberClient 'system-hud/skillgrp.dat'),'client/system-hud/skillgrp.dat'),
 @((Join-Path $AmberStage 'AmberEffectsV4.usk'),(Join-Path $AmberClient 'animations/AmberEffectsV4.usk'),'client/animations/AmberEffectsV4.usk'),
 @((Join-Path $AmberStage 'AmberVfxMaterialsV4.client.utx'),(Join-Path $AmberClient 'systextures/AmberVfxMaterialsV4.utx'),'client/systextures/AmberVfxMaterialsV4.utx'),
 @((Join-Path $AmberStage 'AmberParticlesV4.u'),(Join-Path $AmberClient 'system-hud/AmberParticlesV4.u'),'client/system-hud/AmberParticlesV4.u'),
 @((Join-Path $AmberStage 'AmberParticlesV4.u'),(Join-Path $AmberClient 'system/AmberParticlesV4.u'),'client/system/AmberParticlesV4.u')
)
foreach($AmberName in @('AmberContract.java','AmberServitor.java')){
 foreach($AmberTree in @('server/game/data/scripts','source/L2J_Mobius_CT_0_Interlude/dist/game/data/scripts','cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/dist/game/data/scripts')){
  $AmberRelative=$AmberTree+'/custom/AmberContract/'+$AmberName
  $AmberCopies+=,@((Join-Path $AmberStage ('server/custom/AmberContract/'+$AmberName)),(Join-Path $AmberProject $AmberRelative),$AmberRelative)
 }
}
foreach($AmberCopy in $AmberCopies){if(-not(Test-Path -LiteralPath $AmberCopy[0])){throw ('Falta archivo preparado: '+$AmberCopy[0])}}
$AmberPalette=[IO.File]::ReadAllBytes((Join-Path $AmberStage 'AmberVfxMaterialsV4.client.utx'))
if($AmberPalette.Length -lt 48 -or [Text.Encoding]::Unicode.GetString($AmberPalette,0,28) -ne 'Lineage2Ver121'){throw 'Rechazar UTX sin formato cliente 121.'}
foreach($AmberCopy in $AmberCopies){
 $AmberSaved=Join-Path $AmberBackup $AmberCopy[2]
 if((Test-Path -LiteralPath $AmberCopy[1]) -and -not(Test-Path -LiteralPath $AmberSaved)){
  New-Item -ItemType Directory -Path (Split-Path $AmberSaved -Parent) -Force | Out-Null
  Copy-Item -LiteralPath $AmberCopy[1] -Destination $AmberSaved
 }
 Copy-Item -LiteralPath $AmberCopy[0] -Destination $AmberCopy[1] -Force
 if((Get-AmberHash $AmberCopy[0]) -ne (Get-AmberHash $AmberCopy[1])){throw 'Copia instalada no coincide'}
}
Write-Host 'V4 instalado. Soulshot V3 preservado. Falta comprobar flechas/area/fuego en el cliente.'
