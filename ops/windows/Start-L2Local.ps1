$ErrorActionPreference = 'Stop'

$Root = $PSScriptRoot
$ClientRoot = Join-Path (Split-Path $Root -Parent) 'l2\system-hud'
$Java = Join-Path $Root 'tools\jdk-25.0.4.1+1\bin\java.exe'
$MariaDb = Join-Path $Root 'tools\mariadb-11.8.9-winx64\bin\mariadbd.exe'
$MariaDbRoot = Join-Path $Root 'tools\mariadb-11.8.9-winx64'
$MariaDbData = Join-Path $Root 'database\data'
$RunDir = Join-Path $Root 'run'
$LogDir = Join-Path $Root 'logs'

New-Item -ItemType Directory -Path $RunDir, $LogDir -Force | Out-Null

foreach ($required in @($Java, $MariaDb, (Join-Path $Root 'server\libs\LoginServer.jar'), (Join-Path $Root 'server\libs\GameServer.jar'))) {
    if (-not (Test-Path -LiteralPath $required)) {
        throw "Falta un componente necesario: $required"
    }
}

function Test-LocalPort([int]$Port) {
    return [bool](Get-NetTCPConnection -LocalAddress '127.0.0.1' -LocalPort $Port -State Listen -ErrorAction SilentlyContinue)
}

function Wait-LocalPort([int]$Port, [int]$Seconds, [string]$Name) {
    $limit = (Get-Date).AddSeconds($Seconds)
    while ((Get-Date) -lt $limit) {
        if (Test-LocalPort $Port) { return }
        Start-Sleep -Milliseconds 500
    }
    throw "$Name no abrio el puerto $Port. Revisa $LogDir."
}

if (-not (Test-LocalPort 3307)) {
    $mariaArguments = @(
        '--no-defaults',
        ('--basedir=' + $MariaDbRoot.Replace('\','/')),
        ('--datadir=' + $MariaDbData.Replace('\','/')),
        '--port=3307',
        '--bind-address=127.0.0.1',
        '--skip-name-resolve',
        '--character-set-server=utf8mb4',
        '--collation-server=utf8mb4_unicode_ci',
        '--max-connections=20',
        ('--log-error=' + (Join-Path $LogDir 'mariadb-error.log').Replace('\','/')),
        '--console'
    )
    $process = Start-Process -FilePath $MariaDb `
        -ArgumentList $mariaArguments `
        -WindowStyle Hidden -PassThru
    Set-Content -LiteralPath (Join-Path $RunDir 'mariadb.pid') -Value $process.Id
    Wait-LocalPort 3307 45 'MariaDB'
}

if (-not (Test-LocalPort 2106)) {
    $loginDir = Join-Path $Root 'server\login'
    $process = Start-Process -FilePath $Java `
        -ArgumentList '-server','-Djava.net.preferIPv4Stack=true','-Dfile.encoding=UTF-8','-Dorg.slf4j.simpleLogger.log.com.zaxxer.hikari=warn','-XX:+UseZGC','-Xms128m','-Xmx256m','-jar','../libs/LoginServer.jar' `
        -WorkingDirectory $loginDir -WindowStyle Hidden -PassThru `
        -RedirectStandardOutput (Join-Path $LogDir 'login-stdout.log') `
        -RedirectStandardError (Join-Path $LogDir 'login-stderr.log')
    Set-Content -LiteralPath (Join-Path $RunDir 'login.pid') -Value $process.Id
    Wait-LocalPort 2106 90 'Login Server'
    Wait-LocalPort 19014 30 'Enlace Login/Game Server'
}

if (-not (Test-LocalPort 7777)) {
    $gameDir = Join-Path $Root 'server\game'
    $process = Start-Process -FilePath $Java `
        -ArgumentList '-server','-Djava.net.preferIPv4Stack=true','-Dfile.encoding=UTF-8','-Dorg.slf4j.simpleLogger.log.com.zaxxer.hikari=warn','-XX:+UseZGC','-Xms512m','-Xmx2048m','-jar','../libs/GameServer.jar' `
        -WorkingDirectory $gameDir -WindowStyle Hidden -PassThru `
        -RedirectStandardOutput (Join-Path $LogDir 'game-stdout.log') `
        -RedirectStandardError (Join-Path $LogDir 'game-stderr.log')
    Set-Content -LiteralPath (Join-Path $RunDir 'game.pid') -Value $process.Id
    Wait-LocalPort 7777 180 'Game Server'
}

Write-Host 'Lineage II local esta listo.' -ForegroundColor Green
Write-Host "Cliente HUD: $(Join-Path $ClientRoot 'L2.exe')"
Write-Host 'Puedes crear una cuenta escribiendo cualquier usuario y contrasena en el juego.'
