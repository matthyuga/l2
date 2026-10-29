param([switch]$Verify)
$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
if(Get-Process -Name L2 -ErrorAction SilentlyContinue){throw 'El cliente L2 sigue abierto.'}
if(Get-NetTCPConnection -LocalPort 7777 -State Established -ErrorAction SilentlyContinue){throw 'Hay un jugador conectado.'}
$listener=Get-NetTCPConnection -LocalPort 7777 -State Listen -ErrorAction Stop | Select-Object -First 1
$game=Get-CimInstance Win32_Process | Where-Object ProcessId -eq $listener.OwningProcess
$java=Join-Path $root 'tools/jdk-25.0.4.1+1/bin/java.exe'
if($game.ExecutablePath -ne $java -or $game.CommandLine -notmatch 'GameServer\.jar'){throw 'No es el GameServer esperado.'}
$argsText=$game.CommandLine -replace '^"[^"]+"\s+',''
if($argsText -eq $game.CommandLine){throw 'No se pudo separar el ejecutable de sus argumentos.'}
$argsText=$argsText -replace '\s*-Dlab\.veilmar\.verify=\w+',''
$flag=if($Verify){'true'}else{'false'}
$argsText=$argsText -replace '-jar\s+',"-Dlab.veilmar.verify=$flag -jar "
$installation=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'installation.json') -Raw | ConvertFrom-Json
foreach($file in @('game-stderr.log','game-stdout.log')){
    $path=Join-Path $root "logs/$file"
    if(Test-Path -LiteralPath $path){Copy-Item -LiteralPath $path -Destination (Join-Path $installation.backup ('before-'+(Get-Date -Format 'HHmmss')+'-'+$file))}
}
Stop-Process -Id $game.ProcessId
Wait-Process -Id $game.ProcessId -Timeout 30 -ErrorAction SilentlyContinue
$process=Start-Process -FilePath $java -ArgumentList $argsText -WorkingDirectory (Join-Path $root 'server/game') -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $root 'logs/game-stdout.log') -RedirectStandardError (Join-Path $root 'logs/game-stderr.log')
Set-Content -LiteralPath (Join-Path $root 'run/game.pid') -Value $process.Id
Write-Output "GameServer iniciado: $($process.Id), Veilmar verify=$flag. Memoria y demas parametros conservados."
