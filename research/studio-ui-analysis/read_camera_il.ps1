# Static disassembly with existing Cecil tooling; never loads target game code for execution.
$ErrorActionPreference='Stop'
Add-Type -Path 'K:\JUEGOS\KOIKATSU 22\BepInEx\core\Mono.Cecil.dll'
$assemblyPath='K:\JUEGOS\KOIKATSU 22\CharaStudio_Data\Managed\Assembly-CSharp.dll'
$assembly=[Mono.Cecil.AssemblyDefinition]::ReadAssembly($assemblyPath)
$names=@('InputMouseProc','InputMouseWheelZoomProc','InputKeyProc','CameraUpdate','LateUpdate','.ctor')
$lines=foreach($method in $assembly.MainModule.GetType('Studio.CameraControl').Methods){
 if($method.Name -in $names){
  "METHOD $($method.FullName) TOKEN $($method.MetadataToken.ToString())"
  foreach($instruction in $method.Body.Instructions){$instruction.ToString()}
 }
}
$lines | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'camera-cil.txt') -Encoding UTF8
$assembly.Dispose()
Write-Output ('Saved static disassembly: '+$lines.Count+' lines')
$kkus=[Mono.Cecil.AssemblyDefinition]::ReadAssembly('K:\JUEGOS\KOIKATSU 22\BepInEx\plugins\KKUS.dll')
$cameraFeature=$kkus.MainModule.GetType('HSUS.Features.CameraShortcuts')
$types=@($cameraFeature)+@($cameraFeature.NestedTypes)
$kkusLines=foreach($type in $types){foreach($method in $type.Methods){if($method.HasBody){"METHOD $($method.FullName) TOKEN $($method.MetadataToken.ToString())";foreach($instruction in $method.Body.Instructions){$instruction.ToString()}}}}
$kkusLines | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'kkus-camera-cil.txt') -Encoding UTF8
$kkus.Dispose()
