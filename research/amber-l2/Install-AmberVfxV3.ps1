$ErrorActionPreference='Stop'
$AmberProject=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$AmberClient=Join-Path (Split-Path $AmberProject -Parent) 'l2'
$AmberStage=Join-Path $PSScriptRoot 'exports/contract/combat-vfx-v3'
$AmberBackup=Join-Path $AmberProject 'backups/amber-vfx-v3-2026-10-10'
$AmberCodec=Join-Path $AmberProject 'tools/open-l2encdec-1.3.9/l2encdec_win.exe'
if(Get-Process L2 -ErrorAction SilentlyContinue){throw 'Cerrar L2 antes de instalar VFX V3.'}
if(Get-CimInstance Win32_Process | Where-Object {$_.Name -eq 'java.exe' -and $_.CommandLine -match 'GameServer\.jar'}){throw 'Cerrar GameServer antes de instalar VFX V3.'}
function Get-AmberHash([string]$Path){(Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash}
foreach($AmberSpec in @(@('skillgrp','skillgrp.dat'),@('skillname','skillname-e.dat'))){
 $AmberRead=Join-Path $AmberStage ($AmberSpec[0]+'.preflight.raw')
 & $AmberCodec -o $AmberRead (Join-Path $AmberClient ('system-hud/'+$AmberSpec[1])) | Out-Null
 if($LASTEXITCODE -ne 0){throw 'No se pudo descifrar el catalogo instalado'}
 if((Get-AmberHash $AmberRead) -notin @((Get-AmberHash (Join-Path $AmberStage ($AmberSpec[0]+'.before.raw'))),(Get-AmberHash (Join-Path $AmberStage ($AmberSpec[0]+'.raw'))))){throw ('Cambios desconocidos en '+$AmberSpec[1])}
}
$AmberAssets=@{
 (Join-Path $PSScriptRoot 'tools/l2editor/L2Editor/AmberParticlesV3.u')=@((Join-Path $AmberClient 'system-hud/AmberParticlesV3.u'),(Join-Path $AmberClient 'system/AmberParticlesV3.u'))
 (Join-Path $AmberStage 'AmberEffectsV3.usk')=@((Join-Path $AmberClient 'animations/AmberEffectsV3.usk'))
}
foreach($AmberSource in $AmberAssets.Keys){
 if(-not(Test-Path -LiteralPath $AmberSource)){throw 'Falta paquete V3'}
 foreach($AmberDestination in $AmberAssets[$AmberSource]){
  $AmberAllowed=@((Get-AmberHash $AmberSource))
  $AmberPrior=Join-Path $AmberBackup ('client/'+$AmberDestination.Substring($AmberClient.Length+1))
  if(Test-Path -LiteralPath $AmberPrior){$AmberAllowed+=(Get-AmberHash $AmberPrior)}
  if((Test-Path -LiteralPath $AmberDestination) -and (Get-AmberHash $AmberDestination) -notin $AmberAllowed){throw ('Otra version instalada en '+$AmberDestination)}
 }
}
New-Item -ItemType Directory -Path $AmberBackup -Force | Out-Null
foreach($AmberName in @('skillgrp.dat','skillname-e.dat')){
 $AmberDestination=Join-Path $AmberClient ('system-hud/'+$AmberName)
 $AmberSaved=Join-Path $AmberBackup ('client/system-hud/'+$AmberName)
 New-Item -ItemType Directory -Path (Split-Path $AmberSaved -Parent) -Force | Out-Null
 if(-not(Test-Path -LiteralPath $AmberSaved)){Copy-Item -LiteralPath $AmberDestination -Destination $AmberSaved}
 Copy-Item -LiteralPath (Join-Path $AmberStage $AmberName) -Destination $AmberDestination -Force
}
foreach($AmberSource in $AmberAssets.Keys){foreach($AmberDestination in $AmberAssets[$AmberSource]){
 Copy-Item -LiteralPath $AmberSource -Destination $AmberDestination -Force
 if((Get-AmberHash $AmberSource) -ne (Get-AmberHash $AmberDestination)){throw 'Copia de paquete no coincide'}
}}
Write-Host 'VFX V3 instalado: fuego y soulshot en arco, lluvia circular y destellos de impacto.'
