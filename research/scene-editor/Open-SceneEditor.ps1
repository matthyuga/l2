param([string]$Project='', [switch]$Ambientes, [switch]$CollapseDemo)
$ErrorActionPreference='Stop'
$labRoot=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$nodePath=Join-Path $labRoot 'tools/node-v24.22.0-win-x64/node.exe'
if(-not(Test-Path -LiteralPath $nodePath)){$nodePath=Join-Path $labRoot 'tools/node-portable/node.exe'}
$editorUrl='http://127.0.0.1:32290'
$ready=$false
try{$ready=(Invoke-RestMethod -Uri ($editorUrl+'/api/status') -TimeoutSec 2).app -eq 'l2-scene-editor'}catch{}
if(-not $ready){
 if(Get-NetTCPConnection -LocalPort 32290 -State Listen -ErrorAction SilentlyContinue){throw 'El puerto 32290 está ocupado por otro programa.'}
 $logsPath=Join-Path $PSScriptRoot 'logs'
 New-Item -ItemType Directory -Path $logsPath -Force | Out-Null
 $editorProcess=Start-Process -FilePath $nodePath -ArgumentList ('"'+(Join-Path $PSScriptRoot 'server.js')+'"') -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $logsPath 'editor.out.log') -RedirectStandardError (Join-Path $logsPath 'editor.err.log') -PassThru
 $editorProcess.Id | Set-Content -LiteralPath (Join-Path $logsPath 'editor.pid')
 for($attempt=0;$attempt -lt 20;$attempt++){Start-Sleep -Milliseconds 250;try{$ready=(Invoke-RestMethod -Uri ($editorUrl+'/api/status') -TimeoutSec 1).app -eq 'l2-scene-editor';if($ready){break}}catch{}}
 if(-not $ready){throw 'No pudo iniciar el editor. Revisar research/scene-editor/logs.'}
}
if($CollapseDemo){$editorUrl+='/assets/exports/dion-collapse-demo-v1/demo.html'}
if($Project){
 if($Project -notmatch '^[a-zA-Z0-9][a-zA-Z0-9_-]{0,99}\.json$' -or -not(Test-Path -LiteralPath (Join-Path $PSScriptRoot ('projects/'+$Project)))){throw 'Proyecto no disponible.'}
 $editorUrl+='?project='+[Uri]::EscapeDataString($Project)
}
if($Ambientes){$editorUrl+=$(if($Project){'&'}else{'?'})+'ambientes=1'}
Start-Process -FilePath $editorUrl
