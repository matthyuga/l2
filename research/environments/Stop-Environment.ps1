$ErrorActionPreference = 'Stop'
$Root = $PSScriptRoot
$Profile = Get-Content -LiteralPath (Join-Path $Root 'environment.json') -Raw | ConvertFrom-Json
$clients = @(Get-NetTCPConnection -LocalAddress $Profile.address -LocalPort 7777 -State Established -ErrorAction SilentlyContinue)
if ($clients.Count) { throw 'Hay un cliente conectado a este entorno. Sali del juego antes de detenerlo para conservar el progreso.' }
foreach ($kind in @('game','login','database')) {
    $file = Join-Path $Root ('run\' + $kind + '.pid')
    if (!(Test-Path -LiteralPath $file)) { continue }
    $serviceId = [int](Get-Content -LiteralPath $file)
    $p = Get-CimInstance Win32_Process -Filter ("ProcessId=" + $serviceId)
    if (!$p) { continue }
    $expected = Join-Path $Root $(if ($kind -eq 'database') {'tools\mariadb\bin\mariadbd.exe'} else {'tools\jdk\bin\java.exe'})
    if ($p.ExecutablePath -ne $expected) { throw "PID $serviceId ya no pertenece a este entorno. No se detuvo." }
    if ($kind -ne 'database' -and $p.CommandLine -notmatch $(if ($kind -eq 'game') {'GameServer\.jar'} else {'LoginServer\.jar'})) { throw 'El proceso registrado no corresponde al servicio esperado.' }
    if ($kind -eq 'database') {
        & (Join-Path $Root 'tools\mariadb\bin\mariadb-admin.exe') ('--defaults-extra-file=' + (Join-Path $Root 'database\client.ini')) shutdown
        if ($LASTEXITCODE -ne 0) { throw 'No se pudo cerrar la base de datos.' }
    } else {
        Stop-Process -Id $serviceId
    }
    if (Get-Process -Id $serviceId -ErrorAction SilentlyContinue) { Wait-Process -Id $serviceId -Timeout 60 }
}
Write-Host 'Servicios de este entorno detenidos. Los otros entornos no se tocaron.'
