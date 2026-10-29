$ErrorActionPreference='Stop'
$AmberProject=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$AmberClient=Join-Path (Split-Path $AmberProject -Parent) 'l2'
$AmberStage=Join-Path $PSScriptRoot 'exports/contract/combat-vfx-v7'
$AmberBackup=Join-Path $AmberProject ('backups/amber-vfx-v7-'+(Get-Date -Format 'yyyy-MM-dd-HHmmss'))
if(Get-CimInstance Win32_Process | Where-Object {$_.Name -match '^L2.*\.exe$'}){throw 'Cerrar L2 para recargar skillgrp y no reemplazar archivos cargados.'}
function Get-AmberHash([string]$Path){(Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash}
$AmberCodec=Join-Path $AmberProject 'tools/open-l2encdec-1.3.9/l2encdec_win.exe'
foreach($AmberCatalog in @(@('skillgrp','skillgrp.dat'),@('skillname','skillname-e.dat'))){
 $AmberPreflight=Join-Path $AmberStage ($AmberCatalog[0]+'.preflight.raw')
 & $AmberCodec -o $AmberPreflight (Join-Path $AmberClient ('system-hud/'+$AmberCatalog[1])) | Out-Null
 if($LASTEXITCODE -ne 0 -or (Get-AmberHash $AmberPreflight) -ne (Get-AmberHash (Join-Path $AmberStage ($AmberCatalog[0]+'.before.raw')))){throw 'Catalogo cambiado desde staging.'}
}
$AmberCopies=@(
 @('skillgrp.dat','system-hud/skillgrp.dat'),
 @('skillname-e.dat','system-hud/skillname-e.dat'),
 @('AmberEffectsV7.usk','animations/AmberEffectsV7.usk'),
 @('AmberParticlesV7.u','system-hud/AmberParticlesV7.u'),
 @('AmberParticlesV7.u','system/AmberParticlesV7.u'),
 @('DamageGlyphsV2.u','system-hud/DamageGlyphsV2.u'),
 @('DamageGlyphsV2.u','system/DamageGlyphsV2.u')
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
Set-Content -LiteralPath (Join-Path $AmberStage 'installed-backup.path.txt') -Value $AmberBackup
Write-Host 'V7 cliente instalado. No requiere reiniciar GameServer. Falta prueba .vfx prueba.'
