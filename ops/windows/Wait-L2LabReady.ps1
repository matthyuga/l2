param([int]$TimeoutSeconds=900)
$ErrorActionPreference='Stop'
$taskRoot=$PSScriptRoot
$gamePidFile=Join-Path $taskRoot 'run\game.pid'
$gameLog=Join-Path $taskRoot 'logs\game-stderr.log'
if(-not (Test-Path -LiteralPath $gamePidFile)){throw 'No se encontro el proceso del GameServer.'}
$gameProcessId=[int](Get-Content -LiteralPath $gamePidFile -Raw).Trim()
$gameProcess=Get-Process -Id $gameProcessId -ErrorAction Stop
$gameStarted=$gameProcess.StartTime
$deadline=(Get-Date).AddSeconds($TimeoutSeconds)
$lastCount=-1
$announced=$false
$checkedHistory=$false
while((Get-Date) -lt $deadline){
    if(-not (Get-Process -Id $gameProcessId -ErrorAction SilentlyContinue)){
        throw 'GameServer se cerro durante la preparacion. Revisa logs.'
    }
    if((Test-Path -LiteralPath $gameLog) -and (Get-Item -LiteralPath $gameLog).LastWriteTime -ge $gameStarted){
        if(-not $checkedHistory){
            # A long-running server may have logged many lines since it became ready.
            $checkedHistory=$true
            if(Select-String -LiteralPath $gameLog -Pattern 'ROSTER_MANUAL_READY|Roster Coliseo: 39 perfiles Player preparados' -Quiet){
                Write-Host 'Mundo personalizado listo. Abriendo el cliente...' -ForegroundColor Green
                exit 0
            }
        }
        $lines=@(Get-Content -LiteralPath $gameLog -Tail 1500)
        if($lines -match 'ROSTER_MANUAL_READY|Roster Coliseo: 39 perfiles Player preparados'){
            Write-Host 'Mundo personalizado listo. Abriendo el cliente...' -ForegroundColor Green
            exit 0
        }
        if($lines -match 'Roster Coliseo normal: preparacion parcial; duelos bloqueados'){
            throw 'No terminaron de prepararse los bots. Revisa logs\game-stderr.log.'
        }
        $prepared=@($lines | Select-String 'RosterHybridReload PASS').Count
        if($prepared -ne $lastCount){
            Write-Host "Preparando bots: $prepared/39. Esperando para evitar cargas simultaneas en el disco..." -ForegroundColor Yellow
            $lastCount=$prepared
            $announced=$true
        }
    }
    if(-not $announced){
        Write-Host 'Esperando la preparacion del mundo personalizado...' -ForegroundColor Yellow
        $announced=$true
    }
    Start-Sleep -Seconds 2
}
throw 'La preparacion de los bots tardo mas de lo esperado. Revisa logs antes de volver a iniciar.'
