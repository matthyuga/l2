param([ValidateSet('','armor-editor.html')][string]$Page='')
$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$node=Join-Path $root 'tools/node-portable/node.exe'
$url='http://127.0.0.1:32280'
if(-not(Test-Path -LiteralPath $node)){throw "No se encuentra Node portable: $node"}
$running=$false
try{$status=Invoke-RestMethod -Uri ($url+'/api/status') -TimeoutSec 2;$running=$status.app -eq 'l2-model-gallery'}catch{}
if(-not $running){
    if(Get-NetTCPConnection -LocalPort 32280 -State Listen -ErrorAction SilentlyContinue){throw 'El puerto de la galería está ocupado por otro programa.'}
    $logs=Join-Path $PSScriptRoot 'logs';New-Item -ItemType Directory -Path $logs -Force | Out-Null
    $process=Start-Process -FilePath $node -ArgumentList ('"'+(Join-Path $PSScriptRoot 'server.js')+'"') -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $logs 'gallery.out.log') -RedirectStandardError (Join-Path $logs 'gallery.err.log') -PassThru
    $process.Id | Set-Content -LiteralPath (Join-Path $logs 'gallery.pid')
    for($i=0;$i -lt 20;$i++){Start-Sleep -Milliseconds 300;try{$status=Invoke-RestMethod -Uri ($url+'/api/status') -TimeoutSec 1;if($status.app -eq 'l2-model-gallery'){$running=$true;break}}catch{}}
    if(-not $running){throw "No pudo iniciar la galería. Revisa $logs/gallery.err.log"}
}
Start-Process -FilePath ($url+'/'+$Page)
