$ErrorActionPreference = 'Stop'

$root = $PSScriptRoot
$clientRoot = Join-Path (Split-Path $root -Parent) 'l2\system-hud'
$statusFile = Join-Path $root 'hud-restart-status.txt'

function Set-Status([string]$message) {
    $line = ('{0:yyyy-MM-dd HH:mm:ss}  {1}' -f (Get-Date), $message)
    Set-Content -LiteralPath $statusFile -Value $line -Encoding UTF8
}

Set-Status 'Iniciando reinicio asistido.'

Add-Type -AssemblyName System.Windows.Forms
Add-Type @'
using System;
using System.Runtime.InteropServices;
public static class L2HudNativeUi {
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
    [StructLayout(LayoutKind.Sequential)] public struct POINT { public int X, Y; }
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool GetClientRect(IntPtr hWnd, out RECT rect);
    [DllImport("user32.dll")] public static extern bool ClientToScreen(IntPtr hWnd, ref POINT point);
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern void mouse_event(uint flags, uint dx, uint dy, uint data, UIntPtr extra);
}
'@

$oldServer = Get-NetTCPConnection -LocalPort 7777 -State Listen -ErrorAction Stop | Select-Object -First 1
$oldServerPid = $oldServer.OwningProcess
$client = Get-Process -Name L2 -ErrorAction Stop | Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1

[L2HudNativeUi]::SetForegroundWindow($client.MainWindowHandle) | Out-Null
Start-Sleep -Milliseconds 500
[System.Windows.Forms.SendKeys]::SendWait('{ENTER}')
[System.Windows.Forms.SendKeys]::SendWait('//server_restart 5')
[System.Windows.Forms.SendKeys]::SendWait('{ENTER}')
Start-Sleep -Milliseconds 900

$rect = New-Object L2HudNativeUi+RECT
[L2HudNativeUi]::GetClientRect($client.MainWindowHandle, [ref]$rect) | Out-Null
$point = New-Object L2HudNativeUi+POINT
$point.X = [int](($rect.Right - $rect.Left) / 2 - 40)
$point.Y = [int](($rect.Bottom - $rect.Top) / 2 + 48)
[L2HudNativeUi]::ClientToScreen($client.MainWindowHandle, [ref]$point) | Out-Null
[L2HudNativeUi]::SetCursorPos($point.X, $point.Y) | Out-Null
[L2HudNativeUi]::mouse_event(2, 0, 0, 0, [UIntPtr]::Zero)
[L2HudNativeUi]::mouse_event(4, 0, 0, 0, [UIntPtr]::Zero)
Set-Status 'Comando de reinicio confirmado dentro del juego.'

$exitLimit = (Get-Date).AddSeconds(25)
while ((Get-Date) -lt $exitLimit) {
    if (-not (Get-Process -Id $oldServerPid -ErrorAction SilentlyContinue)) { break }
    Start-Sleep -Milliseconds 500
}
if (Get-Process -Id $oldServerPid -ErrorAction SilentlyContinue) {
    throw 'El GameServer no acepto el comando; no se forzo el cierre.'
}

Set-Status 'Servidor anterior detenido limpiamente; iniciando la version HUD.'
& (Join-Path $root 'Start-L2Local.ps1') | Out-Null

$client.Refresh()
if (-not $client.HasExited) {
    [L2HudNativeUi]::SetForegroundWindow($client.MainWindowHandle) | Out-Null
    [System.Windows.Forms.SendKeys]::SendWait('%{F4}')
    if (-not $client.WaitForExit(8000)) {
        $client.CloseMainWindow() | Out-Null
    }
}

Start-Process -FilePath (Join-Path $clientRoot 'L2.exe') -ArgumentList 'L2Protocol' -WorkingDirectory $clientRoot
Set-Status 'LISTO: servidor HUD iniciado y cliente system-hud abierto.'
