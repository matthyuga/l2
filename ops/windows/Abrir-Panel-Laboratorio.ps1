$ErrorActionPreference = 'Stop'

$root = $PSScriptRoot
$panelRoot = Join-Path $root 'lab-panel'
$pidFile = Join-Path $panelRoot 'panel.pid'
$logFile = Join-Path $panelRoot 'panel.log'
$url = 'http://127.0.0.1:3210'

function Test-Panel {
    try {
        $response = Invoke-WebRequest -UseBasicParsing -Uri ($url + '/api/status') -TimeoutSec 1
        return $response.StatusCode -eq 200
    }
    catch {
        return $false
    }
}

if (-not (Test-Panel)) {
    $node = Join-Path $root 'tools\node-portable\node.exe'
    if (-not (Test-Path -LiteralPath $node)) {
        $node = (Get-Command 'node.exe' -ErrorAction Stop).Source
    }
    $previousRoot = $env:L2_LOCAL_ROOT
    try {
        $env:L2_LOCAL_ROOT = $root
        $process = Start-Process -FilePath $node -ArgumentList 'server.js' -WorkingDirectory $panelRoot -WindowStyle Hidden -RedirectStandardOutput $logFile -RedirectStandardError (Join-Path $panelRoot 'panel-error.log') -PassThru
    }
    finally {
        $env:L2_LOCAL_ROOT = $previousRoot
    }
    Set-Content -LiteralPath $pidFile -Value $process.Id -Encoding ASCII

    $ready = $false
    for ($attempt = 0; $attempt -lt 20; $attempt++) {
        Start-Sleep -Milliseconds 300
        if (Test-Panel) {
            $ready = $true
            break
        }
    }
    if (-not $ready) {
        throw "El panel no pudo iniciar. Revisa $logFile"
    }
}

Start-Process $url
