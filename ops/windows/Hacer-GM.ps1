param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$Personaje
)

$ErrorActionPreference = 'Stop'
$client = Join-Path $PSScriptRoot 'tools\mariadb-11.8.9-winx64\bin\mariadb.exe'
$databasePassword = $env:L2_DB_PASSWORD
if (-not $databasePassword) {
    throw 'Define L2_DB_PASSWORD en tu entorno local antes de ejecutar este script.'
}
if (-not (Get-NetTCPConnection -LocalAddress '127.0.0.1' -LocalPort 3307 -State Listen -ErrorAction SilentlyContinue)) {
    throw 'MariaDB no está iniciado. Ejecuta primero Start-L2Local.ps1.'
}

$escaped = $Personaje.Replace("'", "''")
$result = & $client --host=127.0.0.1 --port=3307 --user=l2j "--password=$databasePassword" --database=l2jmobiusinterlude --batch --skip-column-names --execute="UPDATE characters SET accesslevel=100 WHERE char_name='$escaped'; SELECT ROW_COUNT();"
if ($LASTEXITCODE -ne 0) { throw 'No se pudo actualizar el personaje.' }
if (($result | Select-Object -Last 1) -eq '1') {
    Write-Host "$Personaje ahora tiene nivel Master/GM (100). Vuelve a entrar al juego." -ForegroundColor Green
} else {
    throw "No encontré el personaje '$Personaje'. Créalo y sal del juego antes de ejecutar este comando."
}
