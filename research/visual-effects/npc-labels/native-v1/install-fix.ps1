$ErrorActionPreference='Stop'
$stage=$PSScriptRoot
$root=Split-Path (Split-Path (Split-Path (Split-Path $stage -Parent) -Parent) -Parent) -Parent
$client=Join-Path (Split-Path $root -Parent) 'l2\system-hud'
if(Get-Process L2 -ErrorAction SilentlyContinue){throw 'Cierra L2 antes de instalar la correccion.'}
$target=Join-Path $client 'HellgamesLabelsV1.u'
$source=Join-Path $stage 'fixed\HellgamesLabelsV1.u'
$before=(Get-FileHash -LiteralPath (Join-Path $stage 'HellgamesLabelsV1.u') -Algorithm SHA256).Hash
if((Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash -ne $before){throw 'El paquete instalado cambio; revisar antes de reemplazar.'}
$check=Get-Content -LiteralPath (Join-Path $stage 'fix-emitter-defaults.log') -Raw
if($check -notmatch 'PASS EventGold.Label' -or $check -notmatch 'PASS EventGold.Motes'){throw 'Verificacion incompleta.'}
$backup=Join-Path $root ('backups\hellgames-labels-emitter-fix-'+(Get-Date -Format yyyyMMdd-HHmmss))
$null=New-Item -ItemType Directory -Path $backup
Copy-Item -LiteralPath $target -Destination (Join-Path $backup 'HellgamesLabelsV1.u')
Copy-Item -LiteralPath $source -Destination $target -Force
$after=(Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLowerInvariant()
if((Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant() -ne $after){throw 'Copia no coincide.'}
# Preserve the original full rollback, accepting only this verified replacement.
$info=Get-Content -LiteralPath (Join-Path $stage 'installed.json') -Raw | ConvertFrom-Json
$manifestPath=Join-Path $info.backup 'manifest.json'
Copy-Item -LiteralPath $manifestPath -Destination (Join-Path $backup 'original-manifest.json')
$manifest=Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
($manifest | Where-Object target -eq $target).installed=$after
$manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $manifestPath -Encoding UTF8
@{installed=$true;backup=$backup;sha256=$after;TriggerDisabled=$false;Disabled=$false;AlphaTest=$false;LevelOfWeather=0;ingameVisualVerified=$false} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $stage 'emitter-fix-installed.json') -Encoding UTF8
Write-Host 'Correccion instalada. Abrir L2 de nuevo; no requiere reiniciar GameServer.'
