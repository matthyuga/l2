$ErrorActionPreference = 'Stop'

$source = @'
using System;
using System.Runtime.InteropServices;
public static class LineageInput {
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
    [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);
    [DllImport("user32.dll")] public static extern bool ShowWindowAsync(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern void mouse_event(uint flags, uint dx, uint dy, uint data, UIntPtr extraInfo);
}
'@
Add-Type -TypeDefinition $source
Add-Type -AssemblyName System.Windows.Forms

$game = Get-Process -Name 'L2' -ErrorAction Stop | Select-Object -First 1
$handle = $game.MainWindowHandle
if ($handle -eq [IntPtr]::Zero) {
    throw 'Lineage II no tiene una ventana activa.'
}

$foreground = [LineageInput]::GetForegroundWindow()
if (($foreground -ne [IntPtr]::Zero) -and ($foreground -ne $handle)) {
    [LineageInput]::ShowWindowAsync($foreground, 6) | Out-Null
}
[LineageInput]::ShowWindowAsync($handle, 9) | Out-Null
[LineageInput]::BringWindowToTop($handle) | Out-Null
[LineageInput]::SetForegroundWindow($handle) | Out-Null
Start-Sleep -Milliseconds 900

$rect = New-Object LineageInput+RECT
if (-not [LineageInput]::GetWindowRect($handle, [ref]$rect)) {
    throw 'No se pudo obtener el tamano de la ventana de Lineage II.'
}

# The account field is at this stable relative position in the Interlude UI.
$x = [int]($rect.Left + (($rect.Right - $rect.Left) * 0.522))
$y = [int]($rect.Top + (($rect.Bottom - $rect.Top) * 0.529))
[LineageInput]::SetCursorPos($x, $y) | Out-Null
[LineageInput]::mouse_event(0x0002, 0, 0, 0, [UIntPtr]::Zero)
[LineageInput]::mouse_event(0x0004, 0, 0, 0, [UIntPtr]::Zero)
Start-Sleep -Milliseconds 250

[System.Windows.Forms.SendKeys]::SendWait('^a')
[System.Windows.Forms.SendKeys]::SendWait('solo')
[System.Windows.Forms.SendKeys]::SendWait('{TAB}')
[System.Windows.Forms.SendKeys]::SendWait('^a')
[System.Windows.Forms.SendKeys]::SendWait('solo123')
[System.Windows.Forms.SendKeys]::SendWait('{ENTER}')
