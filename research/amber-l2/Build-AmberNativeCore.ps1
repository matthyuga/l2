$ErrorActionPreference = 'Stop'
$AmberProject = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$AmberJava = Join-Path $AmberProject 'tools/jdk-25.0.4.1+1/bin'
$AmberStage = Join-Path $PSScriptRoot 'exports/contract/native-controls'
$AmberBuild = Join-Path $AmberProject 'build/amber-native-controls'
$AmberOriginal = Join-Path $AmberProject 'backups/amber-native-controls-2026-10-10/GameServer.jar'
$AmberOutput = Join-Path $AmberStage 'GameServer.jar'
$AmberSource = Join-Path $AmberProject 'source/L2J_Mobius_CT_0_Interlude/java/org/l2jmobius/gameserver/network/clientpackets/RequestActionUse.java'
$AmberEntry = 'org/l2jmobius/gameserver/network/clientpackets/RequestActionUse.class'
if ((Get-FileHash -LiteralPath $AmberOriginal).Hash -ne 'AB6DC1C692B98FB489F3D5BC8B5C3323C0DADCCF7BFCF89B63BA7E5DA5A5AA38') { throw 'Base de GameServer desconocida.' }
New-Item -ItemType Directory -Path $AmberBuild -Force | Out-Null
& (Join-Path $AmberJava 'javac.exe') -encoding UTF-8 -cp (Join-Path $AmberProject 'server/libs/*') -d $AmberBuild $AmberSource
if ($LASTEXITCODE -ne 0) { throw 'No se pudo compilar RequestActionUse.' }
Copy-Item -LiteralPath $AmberOriginal -Destination $AmberOutput -Force
& (Join-Path $AmberJava 'jar.exe') --update --file $AmberOutput -C $AmberBuild $AmberEntry
if ($LASTEXITCODE -ne 0) { throw 'No se pudo actualizar el JAR.' }
Add-Type -AssemblyName System.IO.Compression.FileSystem
function Get-AmberEntryHash($Entry) {
    $AmberStream = $Entry.Open(); $AmberDigest = [Security.Cryptography.SHA256]::Create()
    try { [BitConverter]::ToString($AmberDigest.ComputeHash($AmberStream)) } finally { $AmberStream.Dispose(); $AmberDigest.Dispose() }
}
$AmberBefore = [IO.Compression.ZipFile]::OpenRead($AmberOriginal)
$AmberAfter = [IO.Compression.ZipFile]::OpenRead($AmberOutput)
try {
    if ($AmberBefore.Entries.Count -ne $AmberAfter.Entries.Count) { throw 'Cambio inesperado en el numero de entradas del JAR.' }
    $AmberChanged = @()
    foreach ($AmberOld in $AmberBefore.Entries) {
        $AmberNew = $AmberAfter.GetEntry($AmberOld.FullName)
        if (-not $AmberNew) { throw ('Falta entrada: ' + $AmberOld.FullName) }
        if ((Get-AmberEntryHash $AmberOld) -ne (Get-AmberEntryHash $AmberNew)) { $AmberChanged += $AmberOld.FullName }
    }
    if ($AmberChanged.Count -ne 1 -or $AmberChanged[0] -ne $AmberEntry) { throw ('Entradas inesperadas modificadas: ' + ($AmberChanged -join ', ')) }
    Write-Host ('PASS: solo RequestActionUse.class cambio; se conservaron {0} entradas del core.' -f ($AmberBefore.Entries.Count - 1))
} finally { $AmberBefore.Dispose(); $AmberAfter.Dispose() }
