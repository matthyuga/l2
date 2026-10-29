$ErrorActionPreference='Stop'
$perfOut='E:\l2-local\diagnostics\combat-stutter-20261023'
$perfRows=@()
for($sampleIndex=0;$sampleIndex -lt 50;$sampleIndex++){
 $perfRows+=[ordered]@{time=(Get-Date).ToString('o');processes=@(Get-CimInstance Win32_PerfFormattedData_PerfProc_Process -Filter 'IDProcess = 16448 OR IDProcess = 1264' | Select-Object Name,IDProcess,PercentProcessorTime,PrivateBytes,VirtualBytes,PageFaultsPersec,IOReadBytesPersec);gpu=((& nvidia-smi.exe --query-gpu=utilization.gpu,memory.used,clocks.sm,pstate --format=csv,noheader,nounits)-join '')}
 if($sampleIndex%5 -eq 0){$perfRows|ConvertTo-Json -Depth 5|Set-Content -LiteralPath (Join-Path $perfOut 'active-samples.json') -Encoding UTF8}
 Start-Sleep -Milliseconds 900
}
$perfRows|ConvertTo-Json -Depth 5|Set-Content -LiteralPath (Join-Path $perfOut 'active-samples.json') -Encoding UTF8
Write-Output 'Active sampling complete.'
