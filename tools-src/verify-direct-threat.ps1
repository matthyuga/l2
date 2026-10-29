$ErrorActionPreference='Stop'
$taskRoot='E:\l2-local'
$taskJdk=Join-Path $taskRoot 'tools\jdk-25.0.4.1+1\bin'
$taskReport=Join-Path $taskRoot 'reports\direct-threat-2026-10-12'
$taskBuild=Join-Path $taskRoot 'build\direct-threat-test'
$taskName='DirectThreatVerification'+(Get-Date -Format 'HHmmssfff')
$taskText=[IO.File]::ReadAllText((Join-Path $taskRoot 'tools-src\DirectThreatVerification.java')).Replace('DirectThreatVerification',$taskName)
$taskSource=Join-Path $taskBuild ($taskName+'.java')
[IO.File]::WriteAllText($taskSource,$taskText)
& (Join-Path $taskJdk 'javac.exe') -encoding UTF-8 -cp (Join-Path $taskRoot 'server\libs\*') -d $taskBuild $taskSource (Join-Path $taskRoot 'tools-src\AttachDirectThreat.java')
if($LASTEXITCODE){throw 'No compilo el arnes.'}
$taskManifest=Join-Path $taskReport 'agent.mf'
Set-Content -LiteralPath $taskManifest -Value ("Manifest-Version: 1.0`nAgent-Class: "+$taskName+"`n") -Encoding Ascii
$taskAgent=Join-Path $taskReport ($taskName+'.jar')
& (Join-Path $taskJdk 'jar.exe') --create --file $taskAgent --manifest $taskManifest -C $taskBuild ($taskName+'.class')
if($LASTEXITCODE){throw 'No se pudo empaquetar.'}
$taskListener=Get-NetTCPConnection -LocalPort 7777 -State Listen | Select-Object -First 1
& (Join-Path $taskJdk 'java.exe') -cp $taskBuild AttachDirectThreat $taskListener.OwningProcess $taskAgent $taskReport
Get-Content -LiteralPath (Join-Path $taskReport 'verification.txt')
if($LASTEXITCODE){throw 'Fallo la verificacion.'}
