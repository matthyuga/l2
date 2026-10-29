$ErrorActionPreference='Stop'
$surveyRoot=$PSScriptRoot
$jdkBin='E:\l2-local\tools\jdk-25.0.4.1+1\bin'
$roomClasses='E:\l2-local\research\pvp-round-sets\compiled'
& "$jdkBin\javac.exe" -encoding UTF-8 -cp "E:\l2-local\server\libs\*;$roomClasses" -d "$surveyRoot\adapter-classes" "$surveyRoot\adapter-src\custom\ElvenPvpRoom\RoomTacticalPolicy.java" "$surveyRoot\adapter-src\custom\ElvenPvpRoom\MobiusTacticalPreview.java"
if($LASTEXITCODE -ne 0){throw 'Adapter compilation failed'}
& "$jdkBin\javac.exe" -encoding UTF-8 -cp "$surveyRoot\adapter-classes" -d "$surveyRoot\test-classes" "$surveyRoot\test-src\RoomTacticalPolicyCheck.java"
if($LASTEXITCODE -ne 0){throw 'Policy test compilation failed'}
& "$jdkBin\java.exe" -cp "$surveyRoot\adapter-classes;$surveyRoot\test-classes" RoomTacticalPolicyCheck "$surveyRoot\policy-verification.txt"
if($LASTEXITCODE -ne 0){throw 'Decision tests failed'}
