param([switch]$InstallOnly)
$ErrorActionPreference = 'Stop'
try {
 $staged = Join-Path $PSScriptRoot 'LineageMonster-native-ride.u'
 $target = Join-Path $PSScriptRoot 'client-lab/system/LineageMonster.u'
 if (!(Test-Path -LiteralPath $staged)) { throw 'Falta el paquete de montaje preparado.' }
 $reportPath = Join-Path $PSScriptRoot 'native-ride-class-patch.json'
 $report = Get-Content -LiteralPath $reportPath -Raw | ConvertFrom-Json
 $expected = $report.stagedSHA256
 $mountStaged = Join-Path $PSScriptRoot 'BHMTransport.u'
 $mountTarget = Join-Path $PSScriptRoot 'client-lab/system/BHMTransport.u'
 if ((Get-FileHash -LiteralPath $mountStaged -Algorithm SHA256).Hash -ne $report.mountPackageSHA256) { throw 'La malla preparada no coincide con su verificacion.' }
 if ((Get-FileHash -LiteralPath $staged -Algorithm SHA256).Hash -ne $expected) { throw 'El paquete preparado no coincide con su verificacion.' }
 if (Get-Process -Name L2 -ErrorAction SilentlyContinue) { throw 'Cerra Lineage II antes de actualizar y abrir el cliente de pruebas.' }
 if ((Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash -ne $expected) {
  try { Copy-Item -LiteralPath $staged -Destination $target -Force }
  catch { throw 'Cerra Lineage II antes de abrir este acceso: el juego mantiene bloqueado LineageMonster.u.' }
 }
 if ((Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash -ne $expected) { throw 'No se pudo verificar el paquete instalado.' }
 if ((Get-FileHash -LiteralPath $mountTarget -Algorithm SHA256).Hash -ne $report.mountPackageSHA256) {
  $backup = Join-Path $PSScriptRoot 'BHMTransport-before-real-bone.u'
  if (!(Test-Path -LiteralPath $backup)) { Copy-Item -LiteralPath $mountTarget -Destination $backup }
  Copy-Item -LiteralPath $mountStaged -Destination $mountTarget -Force
 }
 if ((Get-FileHash -LiteralPath $mountTarget -Algorithm SHA256).Hash -ne $report.mountPackageSHA256) { throw 'No se pudo verificar la malla instalada.' }
 $localizedReportPath = Join-Path $PSScriptRoot 'native-ride-int-fix.json'
 if (Test-Path -LiteralPath $localizedReportPath) {
  $localizedReport = Get-Content -LiteralPath $localizedReportPath -Raw | ConvertFrom-Json
  $localizedStaged = Join-Path $PSScriptRoot 'LineageMonster-native-ride.int'
  $localizedTarget = Join-Path $PSScriptRoot 'client-lab/system/LineageMonster.int'
  if ((Get-FileHash -LiteralPath $localizedStaged -Algorithm SHA256).Hash -ne $localizedReport.stagedSHA256) { throw 'No coincide el archivo de animaciones localizado preparado.' }
  if ((Get-FileHash -LiteralPath $localizedTarget -Algorithm SHA256).Hash -ne $localizedReport.stagedSHA256) {
   $backup = Join-Path $PSScriptRoot 'LineageMonster-before-native-idle.int'
   if (!(Test-Path -LiteralPath $backup)) { Copy-Item -LiteralPath $localizedTarget -Destination $backup }
   Copy-Item -LiteralPath $localizedStaged -Destination $localizedTarget -Force
  }
  if ((Get-FileHash -LiteralPath $localizedTarget -Algorithm SHA256).Hash -ne $localizedReport.stagedSHA256) { throw 'No se pudo verificar el archivo de animaciones localizado instalado.' }
  $localizedReport.installed = $true
  $localizedReport | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $localizedReportPath -Encoding UTF8
 }
 $report.installed = $true
 if ($report.PSObject.Properties['installationPending']) { $report.PSObject.Properties.Remove('installationPending') }
 $report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $reportPath -Encoding UTF8
 $installationPath = Join-Path $PSScriptRoot 'client-installation.json'
 if (Test-Path -LiteralPath $installationPath) {
  $installation = Get-Content -LiteralPath $installationPath -Raw | ConvertFrom-Json
  $installation.packageSHA256 = $report.mountPackageSHA256
  $installation.nativeClientVerified = $false
  $installation.operationalStatus = 'Real Bone15 and complete animation tables installed; in-game visual test pending.'
  $installation | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $installationPath -Encoding UTF8
 }
 if (!$InstallOnly) { Start-Process -FilePath (Join-Path $PSScriptRoot 'client-lab/system/L2.exe') -WorkingDirectory (Join-Path $PSScriptRoot 'client-lab/system') }
} catch {
 Write-Host $_.Exception.Message -ForegroundColor Red
 exit 1
}
