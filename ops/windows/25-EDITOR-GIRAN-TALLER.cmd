@echo off
setlocal
set "ROOT=%~dp0"
set "NODE=%ROOT%tools\node-v24.22.0-win-x64\node.exe"
set "SERVER=%ROOT%research\scene-editor\server-giran-isolated.js"
set "PROFILE=%ROOT%run\chrome-giran-editor"
powershell.exe -NoProfile -Command "if(-not (Get-NetTCPConnection -LocalPort 32291 -State Listen -ErrorAction SilentlyContinue)){Start-Process -FilePath '%NODE%' -ArgumentList 'server-giran-isolated.js' -WorkingDirectory '%ROOT%research\scene-editor' -WindowStyle Hidden}"
powershell.exe -NoProfile -Command "$ready=$false;for($i=0;$i-lt 30;$i++){try{$ready=(Invoke-RestMethod 'http://127.0.0.1:32291/api/status' -TimeoutSec 1).app -eq 'l2-scene-editor'}catch{};if($ready){break};Start-Sleep -Milliseconds 200};if(-not $ready){exit 1}"
start "Taller Giran aislado" "C:\Program Files\Google\Chrome\Application\chrome.exe" --user-data-dir="%PROFILE%" --new-window http://127.0.0.1:32291
