$ErrorActionPreference = 'Stop'

$HostsFile = 'C:\Windows\System32\drivers\etc\hosts'
$BackupDir = Join-Path $PSScriptRoot 'backups'
$BackupFile = Join-Path $BackupDir 'hosts-before-lineage2-local.txt'
$HostName = 'L2authd.Lineage2.com'
$Entry = "127.0.0.1 $HostName # Lineage II local"

$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = [Security.Principal.WindowsPrincipal]::new($identity)
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw 'Este script necesita ejecutarse como administrador.'
}

New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
if (-not (Test-Path -LiteralPath $BackupFile)) {
    Copy-Item -LiteralPath $HostsFile -Destination $BackupFile
}

$lines = @(Get-Content -LiteralPath $HostsFile)
$escapedHost = [regex]::Escape($HostName)
$lines = @($lines | Where-Object { $_ -notmatch "(?i)^\s*(?:\d{1,3}\.){3}\d{1,3}\s+$escapedHost(?:\s|$)" })
if ($lines.Count -gt 0 -and $lines[-1] -ne '') {
    $lines += ''
}
$lines += "# Lineage II Interlude local ($PSScriptRoot)"
$lines += $Entry

[IO.File]::WriteAllLines($HostsFile, $lines, [Text.UTF8Encoding]::new($false))
ipconfig.exe /flushdns | Out-Null

Write-Host 'Cliente configurado: L2authd.Lineage2.com -> 127.0.0.1' -ForegroundColor Green
Write-Host "Copia anterior de hosts: $BackupFile"
