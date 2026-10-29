$ErrorActionPreference='Stop'
$perfOut='E:\l2-local\diagnostics\combat-stutter-20261023'
New-Item -ItemType Directory -Path $perfOut -Force | Out-Null
$perfRows=@()
for($sampleIndex=0;$sampleIndex -lt 18;$sampleIndex++){
 $perfStamp=(Get-Date).ToString('o')
 $perfProcesses=Get-CimInstance Win32_PerfFormattedData_PerfProc_Process | Where-Object {$_.Name -match '^(L2|java|mariadbd)' -or $_.PercentProcessorTime -gt 50} | Select-Object Name,IDProcess,PercentProcessorTime,WorkingSetPrivate,PrivateBytes,VirtualBytes,PageFaultsPersec,IOReadBytesPersec,IOWriteBytesPersec
 $perfThreads=Get-CimInstance Win32_PerfFormattedData_PerfProc_Thread -Filter 'IDProcess = 16448' | Sort-Object PercentProcessorTime -Descending | Select-Object -First 5 IDThread,PercentProcessorTime,ThreadState,ThreadWaitReason
 $perfDisks=Get-CimInstance Win32_PerfFormattedData_PerfDisk_PhysicalDisk | Select-Object Name,PercentIdleTime,CurrentDiskQueueLength,AvgDisksecPerRead,DiskReadBytesPersec,DiskReadsPersec
 $perfMemory=Get-CimInstance Win32_PerfFormattedData_PerfOS_Memory | Select-Object AvailableMBytes,PagesInputPersec,PageReadsPersec
 $perfGpu=(& nvidia-smi.exe --query-gpu=utilization.gpu,memory.used,clocks.sm,pstate,temperature.gpu --format=csv,noheader,nounits) -join ''
 $perfRows+=[ordered]@{time=$perfStamp;processes=@($perfProcesses);l2_threads=@($perfThreads);disks=@($perfDisks);memory=$perfMemory;gpu=$perfGpu}
 Start-Sleep -Milliseconds 900
}
$perfRows | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $perfOut 'samples.json') -Encoding UTF8
Write-Output ('Captured '+$perfRows.Count+' samples: '+$perfOut)
