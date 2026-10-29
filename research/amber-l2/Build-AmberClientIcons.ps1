$ErrorActionPreference = 'Stop'
$AmberProject = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$AmberStage = Join-Path $PSScriptRoot 'exports/contract/visual-v3'
$AmberRaw = Join-Path $AmberStage 'AmberIconsV1.utx'
$AmberEncoded = Join-Path $AmberStage 'AmberIconsV1.client.utx'
$AmberCodec = Join-Path $AmberProject 'tools/open-l2encdec-1.3.9/l2encdec_win.exe'
& $AmberCodec -c encode -p 121 -f AmberIconsV1.utx -o $AmberEncoded $AmberRaw
if ($LASTEXITCODE -ne 0) { throw 'No se pudieron codificar los iconos de Amber.' }
$AmberOriginalBytes = [IO.File]::ReadAllBytes($AmberRaw)
$AmberClientBytes = [IO.File]::ReadAllBytes($AmberEncoded)
if ([Text.Encoding]::Unicode.GetString($AmberClientBytes, 0, 28) -ne 'Lineage2Ver121' -or
    $AmberClientBytes.Length -ne $AmberOriginalBytes.Length + 48) { throw 'Paquete cliente sin cabecera/tail 121.' }
$AmberKey = 0
foreach ($AmberLetter in 'ambericonsv1.utx'.ToCharArray()) { $AmberKey = ($AmberKey + [int]$AmberLetter) -band 255 }
for ($AmberIndex = 0; $AmberIndex -lt $AmberOriginalBytes.Length; $AmberIndex++) {
    if (($AmberClientBytes[$AmberIndex + 28] -bxor $AmberKey) -ne $AmberOriginalBytes[$AmberIndex]) {
        throw "Roundtrip de iconos fallo en byte $AmberIndex."
    }
}
Write-Host 'AmberIconsV1: Lineage2Ver121, roundtrip completo PASS; texturas originales intactas.'
