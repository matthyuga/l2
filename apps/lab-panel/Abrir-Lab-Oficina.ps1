$ErrorActionPreference = 'Stop'

$panelRoot = $PSScriptRoot
$root = Split-Path $panelRoot -Parent
$runtimeDir = Join-Path $panelRoot 'office-runtime'
$profileDir = Join-Path $runtimeDir 'browser-profile'
$panelPidFile = Join-Path $runtimeDir 'panel.pid'
$databasePidFile = Join-Path $runtimeDir 'mariadb.pid'
$node = Join-Path $root 'tools\node-portable\node.exe'
$mariaDb = Join-Path $root 'tools\mariadb-11.8.9-winx64\bin\mariadbd.exe'
$databaseAdmin = Join-Path $root 'tools\mariadb-11.8.9-winx64\bin\mariadb-admin.exe'
$databaseData = Join-Path $root 'database\data'
$logDir = Join-Path $root 'logs'
$url = 'http://127.0.0.1:3210/'

New-Item -ItemType Directory -Path $runtimeDir, $profileDir, $logDir -Force | Out-Null

function Test-Port([int]$port) {
    try {
        $client = New-Object Net.Sockets.TcpClient
        $result = $client.BeginConnect('127.0.0.1', $port, $null, $null)
        $opened = $result.AsyncWaitHandle.WaitOne(350)
        if ($opened) { $client.EndConnect($result) }
        $client.Close()
        return $opened
    }
    catch { return $false }
}

function Wait-Port([int]$port, [int]$seconds, [string]$name) {
    $limit = (Get-Date).AddSeconds($seconds)
    while ((Get-Date) -lt $limit) {
        if (Test-Port $port) { return }
        Start-Sleep -Milliseconds 250
    }
    throw "$name no pudo abrir el puerto $port."
}

function Test-Panel {
    try {
        $response = Invoke-RestMethod -Uri ($url + 'api/status') -TimeoutSec 1
        return $response.database -eq $true
    }
    catch { return $false }
}

if (-not (Test-Path -LiteralPath $node)) { throw "Falta el Node portátil: $node" }
if (-not (Test-Path -LiteralPath $mariaDb)) { throw "Falta MariaDB portátil: $mariaDb" }

if (-not (Test-Port 3307)) {
    $arguments = @(
        '--no-defaults',
        ('--basedir=' + (Join-Path $root 'tools\mariadb-11.8.9-winx64').Replace('\','/')),
        ('--datadir=' + $databaseData.Replace('\','/')),
        '--port=3307', '--bind-address=127.0.0.1', '--skip-name-resolve',
        '--character-set-server=utf8mb4', '--collation-server=utf8mb4_unicode_ci',
        '--max-connections=20', ('--log-error=' + (Join-Path $logDir 'mariadb-office-error.log').Replace('\','/'))
    )
    $databaseProcess = Start-Process -FilePath $mariaDb -ArgumentList $arguments -WorkingDirectory (Split-Path $mariaDb -Parent) -WindowStyle Hidden -PassThru
    Set-Content -LiteralPath $databasePidFile -Value $databaseProcess.Id -Encoding ASCII
    Wait-Port 3307 45 'MariaDB portátil'
}

if (-not (Test-Panel)) {
    $previousRoot = $env:L2_LOCAL_ROOT
    $previousMode = $env:L2_LAB_OFFICE
    try {
        $env:L2_LOCAL_ROOT = $root
        $env:L2_LAB_OFFICE = '1'
        $panelProcess = Start-Process -FilePath $node -ArgumentList 'server.js' -WorkingDirectory $panelRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $runtimeDir 'panel.log') -RedirectStandardError (Join-Path $runtimeDir 'panel-error.log') -PassThru
        Set-Content -LiteralPath $panelPidFile -Value $panelProcess.Id -Encoding ASCII
    }
    finally {
        $env:L2_LOCAL_ROOT = $previousRoot
        $env:L2_LAB_OFFICE = $previousMode
    }
    Wait-Port 3210 15 'Laboratorio L2'
    if (-not (Test-Panel)) { throw 'El panel abrió pero no pudo conectarse con la base portátil.' }
}

$browserCandidates = @(
    @{ Path = 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'; Private = '--inprivate' },
    @{ Path = 'C:\Program Files\Microsoft\Edge\Application\msedge.exe'; Private = '--inprivate' },
    @{ Path = 'C:\Program Files\Google\Chrome\Application\chrome.exe'; Private = '--incognito' },
    @{ Path = 'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'; Private = '--incognito' },
    @{ Path = 'C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe'; Private = '--incognito' },
    @{ Path = 'C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe'; Private = '--incognito' }
)
$browser = $browserCandidates | Where-Object { Test-Path -LiteralPath $_.Path } | Select-Object -First 1
if ($browser) {
    Start-Process -FilePath $browser.Path -ArgumentList @($browser.Private, '--no-first-run', '--disable-sync', ('--user-data-dir="' + $profileDir + '"'), $url)
}
else {
    Start-Process $url
}

