param([Parameter(Mandatory=$true)][int]$ProcessId)

$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
trap {
    ($_ | Out-String) | Set-Content -LiteralPath (Join-Path $root 'runtime-gameguard-error.txt') -Encoding UTF8
    exit 1
}
$source = @'
using System;
using System.Runtime.InteropServices;
public static class ProcessMemoryReader
{
    [DllImport("kernel32.dll", SetLastError=true)]
    public static extern IntPtr OpenProcess(uint access, bool inherit, int processId);
    [DllImport("kernel32.dll", SetLastError=true)]
    public static extern bool ReadProcessMemory(IntPtr process, IntPtr address, byte[] buffer, int size, out IntPtr read);
    [DllImport("kernel32.dll")]
    public static extern bool CloseHandle(IntPtr handle);
}
'@
Add-Type -TypeDefinition $source

$process = Get-Process -Id $ProcessId
$module = $process.Modules | Where-Object ModuleName -ieq 'Core.dll' | Select-Object -First 1
if (-not $module) {
    $loaded = ($process.Modules | ForEach-Object ModuleName) -join ', '
    throw "Core.dll is not loaded. Modules: $loaded"
}

$address = [IntPtr]($module.BaseAddress.ToInt64() + 0x1373b0)
$handle = [ProcessMemoryReader]::OpenProcess(0x410, $false, $ProcessId)
if ($handle -eq [IntPtr]::Zero) { throw "OpenProcess failed: $([Runtime.InteropServices.Marshal]::GetLastWin32Error())" }
try {
    $buffer = New-Object byte[] 4
    $read = [IntPtr]::Zero
    if (-not [ProcessMemoryReader]::ReadProcessMemory($handle, $address, $buffer, 4, [ref]$read)) {
        throw "ReadProcessMemory failed: $([Runtime.InteropServices.Marshal]::GetLastWin32Error())"
    }
    $result = [pscustomobject]@{
        ProcessId = $ProcessId
        ModuleBase = ('0x{0:X8}' -f $module.BaseAddress.ToInt64())
        Address = ('0x{0:X8}' -f $address.ToInt64())
        Value = [BitConverter]::ToInt32($buffer, 0)
        Bytes = (($buffer | ForEach-Object { $_.ToString('X2') }) -join ' ')
        Timestamp = (Get-Date).ToString('o')
    }
    $result | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $root 'runtime-gameguard-value.json') -Encoding UTF8
}
finally {
    [ProcessMemoryReader]::CloseHandle($handle) | Out-Null
}
