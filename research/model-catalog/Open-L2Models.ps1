param([ValidatePattern('^[A-Za-z0-9_-]+$')][string]$Package='LineageMonsters', [ValidatePattern('^[A-Za-z0-9_.-]*$')][string]$Mesh='', [ValidatePattern('^research/npc-batch2/packages/[A-Za-z0-9_-]+/assets$')][string]$AssetRoot='', [ValidateSet('ukx','usx','u')][string]$Extension='ukx')
$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$client=Join-Path (Split-Path $root -Parent) 'l2'
$requestedExtension=$Extension
$extension='ukx'
$packageFolder='animations'
foreach($knownAssetRoot in @('research/veilmar/assets','research/airships/superion-assets','research/airships/gracia-assets')){
    $external=Join-Path $root $knownAssetRoot
    if(Test-Path -LiteralPath (Join-Path $external "StaticMeshes/$Package.usx")){
        $client=$external
        $extension='usx'
        $packageFolder='StaticMeshes'
        break
    }
}
if($AssetRoot){
    $client=(Resolve-Path -LiteralPath (Join-Path $root $AssetRoot)).Path
    $extension=$requestedExtension
    $externalPackage=Get-ChildItem -LiteralPath $client -Recurse -File | Where-Object { $_.Name -eq ($Package+'.'+$extension) } | Select-Object -First 1
    if(-not $externalPackage){throw 'Paquete de Tanda 2 no encontrado.'}
    $packageFolder=Split-Path (Split-Path $externalPackage.FullName -Parent) -Leaf
}
$viewer=Join-Path $root 'research/amber-l2/tools/umodel.exe'
if(-not(Test-Path -LiteralPath $viewer)){throw "No se encuentra el visor: $viewer"}
if(-not(Test-Path -LiteralPath (Join-Path (Split-Path $viewer -Parent) 'SDL2.dll'))){throw 'Falta SDL2.dll junto al visor. Revisa research/amber-l2/tools.'}
if(-not $AssetRoot -and -not(Test-Path -LiteralPath (Join-Path $client "$packageFolder/$Package.$extension"))){throw "No se encuentra el paquete: $Package"}
$viewerPackage=$Package+".$extension"
if($AssetRoot){$viewerPackage=$externalPackage.FullName}
$viewerArguments=@('-game=l2','-meshes',('-path="'+$client+'"'),('"'+$viewerPackage+'"'))
if($Mesh){$viewerArguments+=('"'+$Mesh+'"')}
$logDir=Join-Path $PSScriptRoot 'logs'
New-Item -ItemType Directory -Path $logDir -Force | Out-Null
$stamp=Get-Date -Format 'yyyyMMdd-HHmmss-fff'
$stdout=Join-Path $logDir ('viewer-'+$stamp+'.out.log')
$stderr=Join-Path $logDir ('viewer-'+$stamp+'.err.log')
Write-Host "Abriendo $Package $Mesh. La carga de un paquete completo puede tardar unos segundos."
$process=Start-Process -FilePath $viewer -ArgumentList $viewerArguments -WorkingDirectory $PSScriptRoot -WindowStyle Normal -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru
Start-Sleep -Seconds 2
$process.Refresh()
if($process.HasExited){
    $errorText=(Get-Content -LiteralPath $stderr -Raw -ErrorAction SilentlyContinue)
    $outputText=(Get-Content -LiteralPath $stdout -Raw -ErrorAction SilentlyContinue)
    if($process.ExitCode -ne 0 -or $errorText -match 'ERROR|SDL2.dll'){
        throw "El visor no pudo iniciar. $errorText $outputText Registros: $logDir"
    }
}
Write-Host "Registros del visor: $logDir"
