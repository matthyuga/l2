param([switch]$ServicesOnly, [switch]$VerifyAcademy)
$ErrorActionPreference = 'Stop'
$Root = $PSScriptRoot
$Profile = Get-Content -LiteralPath (Join-Path $Root 'environment.json') -Raw | ConvertFrom-Json
if ($Profile.state -notin @('prepared','verified')) { throw 'La preparacion de este entorno todavia no termino.' }
$Address = $Profile.address
$Java = Join-Path $Root 'tools\jdk\bin\java.exe'
$Maria = Join-Path $Root 'tools\mariadb\bin\mariadbd.exe'
function OwnedListener([int]$Port, [string]$Kind) {
    $c = Get-NetTCPConnection -LocalAddress $Address -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
    if (!$c) { return $false }
    $p = Get-CimInstance Win32_Process -Filter ("ProcessId=" + $c.OwningProcess)
    $pidFile = Join-Path $Root ('run\' + $Kind + '.pid')
    if (!(Test-Path -LiteralPath $pidFile) -or [int](Get-Content -LiteralPath $pidFile) -ne $p.ProcessId) { throw "Puerto $Address`:$Port ocupado por un proceso no registrado en este entorno." }
    if ($p.ExecutablePath -ne $(if ($Kind -eq 'database') {$Maria} else {$Java})) { throw 'No coincide el ejecutable propietario del puerto.' }
    return $true
}
function Wait-Port([int]$Port, [int]$Seconds, [int]$ServiceId) {
    $until = (Get-Date).AddSeconds($Seconds)
    while ((Get-Date) -lt $until) {
        if (Get-NetTCPConnection -LocalAddress $Address -LocalPort $Port -State Listen -ErrorAction SilentlyContinue) { return }
        if (!(Get-Process -Id $ServiceId -ErrorAction SilentlyContinue)) { throw "Servicio $ServiceId finalizo. Revisa logs de $($Profile.name)." }
        Start-Sleep -Milliseconds 500
    }
    throw "Tiempo agotado esperando $Address`:$Port. Revisa logs de $($Profile.name)."
}
function Pending-Service([string]$Kind) {
    $pidFile = Join-Path $Root ('run\' + $Kind + '.pid')
    if (!(Test-Path -LiteralPath $pidFile)) { return 0 }
    $pendingId = [int](Get-Content -LiteralPath $pidFile)
    $process = Get-CimInstance Win32_Process -Filter ("ProcessId=" + $pendingId)
    if (!$process) { return 0 }
    $expected = if ($Kind -eq 'database') {$Maria} else {$Java}
    if ($process.ExecutablePath -ne $expected) { return 0 }
    $signature = if ($Kind -eq 'database') {'--defaults-file='} elseif ($Kind -eq 'game') {'GameServer\.jar'} else {'LoginServer\.jar'}
    if ($process.CommandLine -notmatch $signature) { return 0 }
    return $pendingId
}
$mutex = New-Object System.Threading.Mutex($false, ('Local\L2Environment_' + $Profile.id))
$held = $false
try {
    try { $held = $mutex.WaitOne(0) } catch [System.Threading.AbandonedMutexException] { $held = $true }
    if (!$held) { throw 'Ya hay un arranque en curso para este entorno.' }
    New-Item -ItemType Directory -Path (Join-Path $Root 'logs'), (Join-Path $Root 'run') -Force | Out-Null
    foreach ($service in @(@('database',3307,240),@('login',2106,120),@('game',7777,600))) {
        $pending = Pending-Service $service[0]
        if ($pending -gt 0) { Wait-Port $service[1] $service[2] $pending }
    }
    if (!(OwnedListener 3307 'database')) {
        $p = Start-Process -FilePath $Maria -ArgumentList ('--defaults-file="' + (Join-Path $Root 'database\my.ini') + '"'), '--console' -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $Root 'logs\database-stdout.log') -RedirectStandardError (Join-Path $Root 'logs\database-stderr.log')
        Set-Content -LiteralPath (Join-Path $Root 'run\database.pid') -Value $p.Id
        Wait-Port 3307 240 $p.Id
    }
    if (!(OwnedListener 2106 'login')) {
        $p = Start-Process -FilePath $Java -ArgumentList '-Xms64m','-Xmx256m','-Dfile.encoding=UTF-8','-Djava.net.preferIPv4Stack=true','-jar','../libs/LoginServer.jar' -WorkingDirectory (Join-Path $Root 'server\login') -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $Root 'logs\login-stdout.log') -RedirectStandardError (Join-Path $Root 'logs\login-stderr.log')
        Set-Content -LiteralPath (Join-Path $Root 'run\login.pid') -Value $p.Id
        Wait-Port 2106 120 $p.Id
        Wait-Port 19014 30 $p.Id
    }
    if (!(OwnedListener 7777 'game')) {
        $verifyOption = '-Dacademy.verify=' + ($VerifyAcademy.IsPresent -and $Profile.id -eq 'academy').ToString().ToLowerInvariant()
        $p = Start-Process -FilePath $Java -ArgumentList '-Xms512m',('-Xmx' + $Profile.heapMb + 'm'),'-XX:+UseZGC','-Dfile.encoding=UTF-8','-Djava.net.preferIPv4Stack=true',$verifyOption,'-jar','../libs/GameServer.jar' -WorkingDirectory (Join-Path $Root 'server\game') -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $Root 'logs\game-stdout.log') -RedirectStandardError (Join-Path $Root 'logs\game-stderr.log')
        Set-Content -LiteralPath (Join-Path $Root 'run\game.pid') -Value $p.Id
        Wait-Port 7777 600 $p.Id
    }
    Write-Host ($Profile.name + ': servicios listos en ' + $Address)
    if (!$ServicesOnly) {
        $client = Join-Path $Root 'client\Lineage II\system\L2.exe'
        Start-Process -FilePath $client -ArgumentList 'L2Protocol' -WorkingDirectory (Split-Path $client)
    }
} finally {
    if ($held) { $mutex.ReleaseMutex() }
    $mutex.Dispose()
}
