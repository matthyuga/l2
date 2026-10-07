$ErrorActionPreference = 'Stop'

$labRoot = $PSScriptRoot
$runtimeDir = Join-Path $labRoot 'runtime'
$profileDir = Join-Path $runtimeDir 'browser-profile'
$pidFile = Join-Path $runtimeDir 'server.pid'
$logFile = Join-Path $runtimeDir 'server.log'
$errorFile = Join-Path $runtimeDir 'server-error.log'
$serverScript = Join-Path $labRoot 'server.ps1'
$url = 'http://127.0.0.1:3212/'

New-Item -ItemType Directory -Path $runtimeDir -Force | Out-Null
New-Item -ItemType Directory -Path $profileDir -Force | Out-Null

function Test-IdeaLab {
    try {
        $response = Invoke-WebRequest -UseBasicParsing -Uri ($url + 'api/health') -TimeoutSec 1
        return $response.StatusCode -eq 200
    }
    catch {
        return $false
    }
}

if (-not (Test-IdeaLab)) {
    $quotedScript = '"' + $serverScript + '"'
    $process = Start-Process -FilePath 'powershell.exe' -ArgumentList @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $quotedScript) -WorkingDirectory $labRoot -WindowStyle Hidden -RedirectStandardOutput $logFile -RedirectStandardError $errorFile -PassThru
    Set-Content -LiteralPath $pidFile -Value $process.Id -Encoding ASCII

    $ready = $false
    for ($attempt = 0; $attempt -lt 30; $attempt++) {
        Start-Sleep -Milliseconds 200
        if (Test-IdeaLab) {
            $ready = $true
            break
        }
    }
    if (-not $ready) {
        throw "El Laboratorio de Ideas no pudo iniciar. Revisa $errorFile"
    }
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

