param([Parameter(Mandatory=$true)][int]$ProcessId)
$source = @'
using System;
using System.Runtime.InteropServices;
public static class GameWindow {
    [DllImport("user32.dll")] public static extern bool ShowWindowAsync(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
}
'@
Add-Type -TypeDefinition $source
$game = Get-Process -Id $ProcessId -ErrorAction Stop
[GameWindow]::ShowWindowAsync($game.MainWindowHandle, 9) | Out-Null
Start-Sleep -Milliseconds 300
[GameWindow]::SetForegroundWindow($game.MainWindowHandle) | Out-Null
