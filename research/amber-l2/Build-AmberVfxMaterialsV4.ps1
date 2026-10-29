$ErrorActionPreference='Stop'
$AmberProject=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$AmberStage=Join-Path $PSScriptRoot 'exports/contract/combat-vfx-v4'
$AmberRaw=Join-Path $AmberStage 'AmberVfxMaterialsV4.utx'
$AmberEncoded=Join-Path $AmberStage 'AmberVfxMaterialsV4.client.utx'
$AmberCodec=Join-Path $AmberProject 'tools/open-l2encdec-1.3.9/l2encdec_win.exe'
& $AmberCodec -c encode -p 121 -f AmberVfxMaterialsV4.utx -o $AmberEncoded $AmberRaw
if($LASTEXITCODE -ne 0){throw 'No se pudo codificar la paleta V4.'}
$AmberOriginalBytes=[IO.File]::ReadAllBytes($AmberRaw)
$AmberClientBytes=[IO.File]::ReadAllBytes($AmberEncoded)
if([BitConverter]::ToUInt32($AmberOriginalBytes,0) -ne [uint32]2653586369){throw 'La fuente no es un paquete Unreal crudo.'}
if([Text.Encoding]::Unicode.GetString($AmberClientBytes,0,28) -ne 'Lineage2Ver121' -or $AmberClientBytes.Length -ne $AmberOriginalBytes.Length+48){throw 'Falta envoltura cliente 121.'}
$AmberKey=0
foreach($AmberLetter in 'ambervfxmaterialsv4.utx'.ToCharArray()){$AmberKey=($AmberKey+[int]$AmberLetter) -band 255}
for($AmberIndex=0;$AmberIndex -lt $AmberOriginalBytes.Length;$AmberIndex++){
 if(($AmberClientBytes[$AmberIndex+28] -bxor $AmberKey) -ne $AmberOriginalBytes[$AmberIndex]){throw ('Roundtrip fallo en byte '+$AmberIndex)}
}
Write-Host 'PASS: paleta V4 cliente Lineage2Ver121, clave del nombre instalado y roundtrip completo.'
