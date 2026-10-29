param([Parameter(Mandatory=$true)][string]$LocalRoot)
$ErrorActionPreference = 'Stop'
$expectedHash = 'E64898F18E4D8691C83D3901BB4DDB8F9C9FACA95E7DFBCF7BC7741B6D1F4454'
$url = 'https://raw.githubusercontent.com/naustagic/L2JOrion_Interlude/98e351766c569504210a24d96a9f39262f19b397/L2jOrion_Geodata/geodata/24_19.l2j'
$geoDirectory = Join-Path (Resolve-Path -LiteralPath $LocalRoot).Path 'server\game\data\geodata'
if (-not (Test-Path -LiteralPath $geoDirectory -PathType Container)) { throw 'No existe la carpeta geodata del servidor.' }
$destination = Join-Path $geoDirectory '24_19.l2j'
if (Test-Path -LiteralPath $destination) {
    if ((Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash -ne $expectedHash) { throw 'Hay otra geodata del Coliseo: no se sobrescribe.' }
    Write-Host 'Geodata del Coliseo ya instalada y hash correcto.'
    return
}
if (Get-NetTCPConnection -LocalPort 7777 -State Listen -ErrorAction SilentlyContinue) { throw 'Deten el GameServer de forma segura antes de instalar.' }
$download = Join-Path $geoDirectory ('24_19.' + [Guid]::NewGuid().ToString('N') + '.download')
try {
    Invoke-WebRequest -Uri $url -OutFile $download
    if ((Get-FileHash -LiteralPath $download -Algorithm SHA256).Hash -ne $expectedHash) { throw 'Hash incorrecto: no se instala.' }
    Move-Item -LiteralPath $download -Destination $destination
    Write-Host 'Geodata Coliseo instalada. Reinicia y verifica el log GeoEngine.'
} finally {
    if (Test-Path -LiteralPath $download) { Remove-Item -LiteralPath $download }
}
