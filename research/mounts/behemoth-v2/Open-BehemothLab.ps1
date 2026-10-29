$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '../../..')).Path
$nodePath = Join-Path $projectRoot 'tools/node-v24.22.0-win-x64/node.exe'
$editorPath = Join-Path $projectRoot 'research/scene-editor'
$ready = $false
try { $status = Invoke-RestMethod 'http://127.0.0.1:32302/api/status'; $ready = $status.app -eq 'l2-scene-editor' } catch {}
if (!$ready) {
 $env:L2_SCENE_EDITOR_PORT = '32302'
 Start-Process -FilePath $nodePath -ArgumentList 'server.js' -WorkingDirectory $editorPath -WindowStyle Hidden
 for ($attempt=0; $attempt -lt 30; $attempt++) {
  Start-Sleep -Milliseconds 300
  try { $status = Invoke-RestMethod 'http://127.0.0.1:32302/api/status'; if ($status.app -eq 'l2-scene-editor') { $ready=$true; break } } catch {}
 }
}
if (!$ready) { throw 'No se pudo iniciar la sala de ensayo en el puerto 32302.' }
Start-Process 'http://127.0.0.1:32302/assets/exports/l2lab-behemoth-two-riders-animated/lab.html'
