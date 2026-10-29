$ErrorActionPreference = 'Stop'
$LabRoot = $PSScriptRoot
$ProjectRoot = Split-Path (Split-Path $LabRoot -Parent) -Parent
$ClientRoot = Join-Path (Split-Path $ProjectRoot -Parent) 'l2'
$Profile = Join-Path $ClientRoot 'system-amber'
$OriginalProfile = Join-Path $ClientRoot 'system-hud'
$Marker = Join-Path $Profile 'amber-lab-profile.txt'
if ((Test-Path -LiteralPath $Profile) -and -not (Test-Path -LiteralPath $Marker)) {
    throw "La carpeta $Profile ya existe y no pertenece a este laboratorio."
}
foreach ($asset in @('L2AmberNPCv4.ukx', 'L2AmberMotionv3.ukx')) {
    $target = Join-Path $ClientRoot ('animations\' + $asset)
    if ((Test-Path -LiteralPath $target) -and -not (Test-Path -LiteralPath $Marker)) {
        throw "Ya existe un recurso con el nombre $target."
    }
}
$NpcTarget = Join-Path $ProjectRoot 'server\game\data\stats\npcs\custom\amber_lab.xml'
if ((Test-Path -LiteralPath $NpcTarget) -and -not (Test-Path -LiteralPath $Marker)) {
    throw "Ya existe la configuracion $NpcTarget."
}
New-Item -ItemType Directory -Path $Profile -Force | Out-Null
Copy-Item -Path (Join-Path $OriginalProfile '*') -Destination $Profile -Recurse -Force
Set-Content -LiteralPath $Marker -Value 'Amber L2 Lab - perfil aislado creado desde system-hud' -Encoding UTF8
Copy-Item -LiteralPath (Join-Path $LabRoot 'exports\npcgrp.dat') -Destination (Join-Path $Profile 'npcgrp.dat') -Force
Copy-Item -LiteralPath (Join-Path $LabRoot 'exports\NpcName-e.dat') -Destination (Join-Path $Profile 'NpcName-e.dat') -Force
foreach ($asset in @('L2AmberNPCv4.ukx', 'L2AmberMotionv3.ukx')) {
    Copy-Item -LiteralPath (Join-Path $LabRoot ('exports\' + $asset)) -Destination (Join-Path $ClientRoot ('animations\' + $asset)) -Force
}
Copy-Item -LiteralPath (Join-Path $LabRoot 'exports\amber_lab.xml') -Destination $NpcTarget -Force
$SourceNpcDir = Join-Path $ProjectRoot 'source\L2J_Mobius_CT_0_Interlude\dist\game\data\stats\npcs\custom'
Copy-Item -LiteralPath (Join-Path $LabRoot 'exports\amber_lab.xml') -Destination (Join-Path $SourceNpcDir 'amber_lab.xml') -Force
Write-Host 'Instalado: perfil system-amber, NPC 902500, display 59001.'
Write-Host 'El cliente habitual sigue usando system-hud. Amber se invoca manualmente: //spawn 902500.'
