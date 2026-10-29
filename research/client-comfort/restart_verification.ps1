$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
if (Get-Process -Name L2 -ErrorAction SilentlyContinue) { throw 'L2 sigue abierto.' }
if (Get-NetTCPConnection -LocalPort 7777 -State Established -ErrorAction SilentlyContinue) { throw 'Hay un jugador conectado.' }
$listener = Get-NetTCPConnection -LocalPort 7777 -State Listen -ErrorAction Stop
$gameProcess = Get-CimInstance Win32_Process | Where-Object ProcessId -eq $listener.OwningProcess
if ($gameProcess.CommandLine -notmatch 'GameServer\.jar') { throw 'No es el GameServer esperado.' }
Copy-Item -LiteralPath (Join-Path $root 'logs/game-stderr.log') -Destination (Join-Path $PSScriptRoot 'verification-first-run.log')
Stop-Process -Id $gameProcess.ProcessId
Wait-Process -Id $gameProcess.ProcessId -Timeout 30 -ErrorAction SilentlyContinue
& (Join-Path $root 'Start-L2Local.ps1') -VerifySkillCatalog
