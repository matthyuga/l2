$ErrorActionPreference = 'Stop'
$AmberProject = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$AmberClient = Join-Path (Split-Path $AmberProject -Parent) 'l2'
$AmberStage = Join-Path $PSScriptRoot 'exports/contract/native-controls'
$AmberBackup = Join-Path $AmberProject 'backups/amber-native-controls-2026-10-10'
$AmberCodec = Join-Path $AmberProject 'tools/open-l2encdec-1.3.9/l2encdec_win.exe'
if (Get-Process L2 -ErrorAction SilentlyContinue) { throw 'Cerrar L2 antes de instalar.' }
if (Get-NetTCPConnection -LocalPort 7777 -State Listen -ErrorAction SilentlyContinue) { throw 'Detener GameServer antes de reemplazar su JAR.' }
function Get-AmberHash([string]$Path) { (Get-FileHash -LiteralPath $Path).Hash }
$AmberAction = Join-Path $AmberClient 'system-hud/actionname-e.dat'
$AmberPreflight = Join-Path $AmberStage 'actionname.preflight.raw'
& $AmberCodec -o $AmberPreflight $AmberAction | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'No se pudo descifrar el catalogo de acciones.' }
if ((Get-AmberHash $AmberPreflight) -notin @((Get-AmberHash (Join-Path $AmberStage 'actionname.before.raw')), (Get-AmberHash (Join-Path $AmberStage 'actionname.raw')))) { throw 'El catalogo de acciones contiene otros cambios: integrar antes de instalar.' }
$AmberFiles = @{
    (Join-Path $AmberStage 'actionname-e.dat') = @($AmberAction)
    (Join-Path $AmberStage 'AmberActorsV1.int') = @((Join-Path $AmberClient 'system-hud/AmberActorsV1.int'), (Join-Path $AmberClient 'system/AmberActorsV1.int'))
    (Join-Path $AmberStage 'GameServer.jar') = @((Join-Path $AmberProject 'server/libs/GameServer.jar'))
}
foreach ($AmberSource in $AmberFiles.Keys) {
    if (-not (Test-Path -LiteralPath $AmberSource)) { throw "Falta $AmberSource" }
    foreach ($AmberDestination in $AmberFiles[$AmberSource]) {
        if ((Test-Path -LiteralPath $AmberDestination) -and $AmberDestination -ne $AmberAction) {
            $AmberAllowed = @(Get-AmberHash $AmberSource)
            if ($AmberDestination.EndsWith('GameServer.jar')) { $AmberAllowed += Get-AmberHash (Join-Path $AmberBackup 'GameServer.jar') }
            if ((Get-AmberHash $AmberDestination) -notin $AmberAllowed) { throw "Version desconocida: $AmberDestination" }
        }
    }
}
New-Item -ItemType Directory -Path $AmberBackup -Force | Out-Null
foreach ($AmberSource in $AmberFiles.Keys) {
    foreach ($AmberDestination in $AmberFiles[$AmberSource]) {
        $AmberSaved = Join-Path $AmberBackup ([IO.Path]::GetFileName($AmberDestination))
        if ((Test-Path -LiteralPath $AmberDestination) -and -not (Test-Path -LiteralPath $AmberSaved)) { Copy-Item -LiteralPath $AmberDestination -Destination $AmberSaved }
        Copy-Item -LiteralPath $AmberSource -Destination $AmberDestination -Force
        if ((Get-AmberHash $AmberDestination) -ne (Get-AmberHash $AmberSource)) { throw "Copia incorrecta: $AmberDestination" }
    }
}
Write-Host 'Amber: Attack, Flechas de fuego y Lluvia de flechas instalados; configuracion de animaciones en el paquete propio.'
