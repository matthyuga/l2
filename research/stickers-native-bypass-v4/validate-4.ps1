param([switch]$VerifyRacialCustomization, [switch]$VerifyAmberContract, [switch]$VerifyArenaSpawns, [switch]$VerifySkillCatalog, [switch]$VerifyGiranAgenda, [switch]$VerifyGiranDefense, [switch]$VerifyGiranChaos, [int]$GameHeapMb=0)

$ErrorActionPreference = 'Stop'

$Root = $PSScriptRoot
$startupHash = [System.Security.Cryptography.SHA256]::Create()
try {
    $startupKey = [BitConverter]::ToString($startupHash.ComputeHash([Text.Encoding]::UTF8.GetBytes($Root.ToLowerInvariant()))).Replace('-','')
} finally {
    $startupHash.Dispose()
}
$startupMutex = New-Object System.Threading.Mutex($false, ('Local\L2LocalStart_' + $startupKey))
$startupLockHeld = $false
try {
try {
    $startupLockHeld = $startupMutex.WaitOne(0)
    if (-not $startupLockHeld) {
        Write-Host 'Otro lanzador ya esta preparando L2. Esperando ese mismo arranque...' -ForegroundColor Yellow
        $startupDeadline = (Get-Date).AddMinutes(12)
        while (-not $startupLockHeld -and (Get-Date) -lt $startupDeadline) {
            $startupLockHeld = $startupMutex.WaitOne(500)
        }
        if (-not $startupLockHeld) { throw 'El otro arranque no termino. Revisa los registros en logs.' }
    }
} catch [System.Threading.AbandonedMutexException] {
    # A previous launcher exited unexpectedly; this thread now owns its mutex.
    $startupLockHeld = $true
}
Write-Host 'Comprobando el servidor local...' -ForegroundColor Cyan
$ClientRoot = Join-Path (Split-Path $Root -Parent) 'l2\system-hud'
$Java = Join-Path $Root 'tools\jdk-25.0.4.1+1\bin\java.exe'
$MariaDb = Join-Path $Root 'tools\mariadb-11.8.9-winx64\bin\mariadbd.exe'
$MariaDbRoot = Join-Path $Root 'tools\mariadb-11.8.9-winx64'
$MariaDbData = Join-Path $Root 'database\data'
$RunDir = Join-Path $Root 'run'
$LogDir = Join-Path $Root 'logs'
$AmberVerificationOption = '-Dlab.amber.verify=' + $VerifyAmberContract.IsPresent.ToString().ToLowerInvariant()
$RaceVerificationOption = '-Dlab.race.verify=' + $VerifyRacialCustomization.IsPresent.ToString().ToLowerInvariant()
$ArenaVerificationOption = '-Dlab.arena.spawn.verify=' + $VerifyArenaSpawns.IsPresent.ToString().ToLowerInvariant()
$CatalogVerificationOption = '-Dlab.catalog.verify=' + $VerifySkillCatalog.IsPresent.ToString().ToLowerInvariant()
$GiranVerificationOption = '-Dlab.giran.v2.verify=' + $VerifyGiranAgenda.IsPresent.ToString().ToLowerInvariant()
$GiranDefenseVerificationOption = '-Dlab.giran.v3.verify=' + $VerifyGiranDefense.IsPresent.ToString().ToLowerInvariant()
$GiranChaosVerificationOption = '-Dlab.giran.chaos.verify=' + $VerifyGiranChaos.IsPresent.ToString().ToLowerInvariant()
if($GameHeapMb -eq 0){
    $ramMb=[math]::Floor((Get-CimInstance Win32_OperatingSystem).TotalVisibleMemorySize/1024)
    # Use an 8 GiB ceiling on machines with at least 24 GiB total usable physical RAM.
    # Smaller portable hosts retain the existing adaptive 2/3/4 GiB default.
    $GameHeapMb=if($ramMb -ge 24576){8192}else{[int][math]::Min(4096,[math]::Max(2048,[math]::Floor($ramMb/4096)*1024))}
}
if($GameHeapMb -lt 2048 -or $GameHeapMb -gt 8192){throw 'GameHeapMb debe estar entre2048 y8192.'}
$GameHeapOption='-Xmx'+$GameHeapMb+'m'

New-Item -ItemType Directory -Path $RunDir, $LogDir -Force | Out-Null

foreach ($required in @($Java, $MariaDb, (Join-Path $Root 'server\libs\LoginServer.jar'), (Join-Path $Root 'server\libs\GameServer.jar'))) {
    if (-not (Test-Path -LiteralPath $required)) {
        throw "Falta un componente necesario: $required"
    }
}

function Test-LocalPort([int]$Port) {
    return [bool](Get-NetTCPConnection -LocalAddress '127.0.0.1' -LocalPort $Port -State Listen -ErrorAction SilentlyContinue)
}

function Wait-LocalPort([int]$Port, [int]$Seconds, [string]$Name, [int]$ServiceProcessId=0) {
    $limit = (Get-Date).AddSeconds($Seconds)
    while ((Get-Date) -lt $limit) {
        if (Test-LocalPort $Port) { return }
        if ($ServiceProcessId -and -not (Get-Process -Id $ServiceProcessId -ErrorAction SilentlyContinue)) {
            throw "$Name se cerro antes de abrir el puerto $Port. Revisa $LogDir."
        }
        Start-Sleep -Milliseconds 500
    }
    throw "$Name no abrio el puerto $Port. Revisa $LogDir."
}

if (-not (Test-LocalPort 3307)) {
    Write-Host 'Iniciando la base de datos...'
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
    Wait-LocalPort 3307 45 'MariaDB' $process.Id
}

if (-not (Test-LocalPort 2106)) {
    Write-Host 'Iniciando Login Server...'
    $loginDir = Join-Path $Root 'server\login'
    $process = Start-Process -FilePath $Java `
        -ArgumentList '-server','-Djava.net.preferIPv4Stack=true','-Dfile.encoding=UTF-8','-Dorg.slf4j.simpleLogger.log.com.zaxxer.hikari=warn','-XX:+UseZGC','-Xms128m','-Xmx256m','-jar','../libs/LoginServer.jar' `
        -WorkingDirectory $loginDir -WindowStyle Hidden -PassThru `
        -RedirectStandardOutput (Join-Path $LogDir 'login-stdout.log') `
        -RedirectStandardError (Join-Path $LogDir 'login-stderr.log')
    Set-Content -LiteralPath (Join-Path $RunDir 'login.pid') -Value $process.Id
    Wait-LocalPort 2106 90 'Login Server' $process.Id
    Wait-LocalPort 19014 30 'Enlace Login/Game Server' $process.Id
}

if (-not (Test-LocalPort 7777)) {
    # Adopt an existing startup even if its launcher exited before it opened the port.
    $pendingGame = @(Get-CimInstance Win32_Process -Filter "Name = 'java.exe'" | Where-Object {
        $_.ExecutablePath -eq $Java -and $_.CommandLine -match '-jar\s+"?[^"\s]*GameServer\.jar"?(\s|$)'
    })
    if ($pendingGame.Count -gt 1) { throw 'Hay varios GameServer del proyecto en ejecucion. Revisa sus procesos antes de continuar.' }
    if ($pendingGame.Count -eq 1) {
        Write-Host 'GameServer ya se esta preparando. Esperando que abra el puerto del juego...'
        Set-Content -LiteralPath (Join-Path $RunDir 'game.pid') -Value $pendingGame[0].ProcessId
        Wait-LocalPort 7777 600 'Game Server' $pendingGame[0].ProcessId
    } else {
    # Apply staged core fixes only when no GameServer process is using the JAR.
    $corePatchRoot = Join-Path $Root 'server\pending-core-patches'
    if (Test-Path -LiteralPath $corePatchRoot) {
        foreach ($corePatch in Get-ChildItem -LiteralPath $corePatchRoot -Directory | Sort-Object Name) {
            $corePatchApplied = Join-Path $corePatch.FullName '.applied'
            if ((Test-Path -LiteralPath (Join-Path $corePatch.FullName 'org')) -and -not (Test-Path -LiteralPath $corePatchApplied)) {
                Write-Host ('Aplicando correccion pendiente: ' + $corePatch.Name)
                & (Join-Path $Root 'tools\jdk-25.0.4.1+1\bin\jar.exe') --update --file (Join-Path $Root 'server\libs\GameServer.jar') -C $corePatch.FullName org
                if ($LASTEXITCODE -ne 0) { throw ('No se pudo aplicar la correccion: ' + $corePatch.Name) }
                Set-Content -LiteralPath $corePatchApplied -Value 'Applied before GameServer startup.' -Encoding Ascii
            }
        }
    }
    Write-Host 'Iniciando GameServer. Cargando mundo y scripts...'
    $gameDir = Join-Path $Root 'server\game'
    $process = Start-Process -FilePath $Java `
        -ArgumentList '-server',('-javaagent:"'+(Join-Path $Root 'server/agents/sticker-native-actions-v4.jar')+'"'),'-Djava.net.preferIPv4Stack=true','-Dfile.encoding=UTF-8','-Dorg.slf4j.simpleLogger.log.com.zaxxer.hikari=warn',$RaceVerificationOption,$AmberVerificationOption,$ArenaVerificationOption,$CatalogVerificationOption,$GiranVerificationOption,$GiranDefenseVerificationOption,$GiranChaosVerificationOption,'-XX:+UseZGC','-Xms512m',$GameHeapOption,'-jar','../libs/GameServer.jar' `
        -WorkingDirectory $gameDir -WindowStyle Hidden -PassThru `
        -RedirectStandardOutput (Join-Path $LogDir 'game-stdout.log') `
        -RedirectStandardError (Join-Path $LogDir 'game-stderr.log')
    Set-Content -LiteralPath (Join-Path $RunDir 'game.pid') -Value $process.Id
    Wait-LocalPort 7777 600 'Game Server' $process.Id
    }
}

Write-Host 'Lineage II local esta listo.' -ForegroundColor Green
Write-Host "Cliente HUD: $(Join-Path $ClientRoot 'L2.exe')"
Write-Host 'Puedes crear una cuenta escribiendo cualquier usuario y contrasena en el juego.'
} finally {
    if ($startupLockHeld) { $startupMutex.ReleaseMutex() }
    $startupMutex.Dispose()
}
