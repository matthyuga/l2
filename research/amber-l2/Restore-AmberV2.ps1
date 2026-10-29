$ErrorActionPreference='Stop'
$AmberProfile='E:\l2\system-amber'
if (-not (Test-Path -LiteralPath (Join-Path $AmberProfile 'amber-lab-profile.txt'))) { throw 'Missing profile marker' }
foreach ($AmberFile in @('npcgrp.dat','NpcName-e.dat')) {
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot ('backups\before-visual-v3\'+$AmberFile)) -Destination (Join-Path $AmberProfile $AmberFile) -Force
}
Write-Host 'Restaurado el catalogo de Amber v2. Reinicia el cliente para verlo.'
