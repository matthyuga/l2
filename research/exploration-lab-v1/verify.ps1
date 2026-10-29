$ErrorActionPreference = 'Stop'
$labRoot = $PSScriptRoot
$projectRoot = Split-Path (Split-Path $labRoot -Parent) -Parent
$javaBin = Join-Path $projectRoot 'tools\jdk-25.0.4.1+1\bin'
$outputDir = Join-Path $labRoot 'build'
$sources = @(
    (Join-Path $labRoot 'src\custom\ExplorationLab\ExplorationState.java'),
    (Join-Path $labRoot 'src\custom\ExplorationLab\ExplorationLab.java'),
    (Join-Path $labRoot 'tests\ExplorationStateTest.java')
)
& (Join-Path $javaBin 'javac.exe') -encoding UTF-8 -cp (Join-Path $projectRoot 'server\libs\*') -d $outputDir @sources
if ($LASTEXITCODE -ne 0) { throw 'La compilacion fallo.' }
& (Join-Path $javaBin 'java.exe') -cp $outputDir custom.ExplorationLab.ExplorationStateTest
if ($LASTEXITCODE -ne 0) { throw 'La verificacion fallo.' }
