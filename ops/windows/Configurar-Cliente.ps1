$ErrorActionPreference = 'Stop'

$AdminScript = Join-Path $PSScriptRoot 'Configurar-Cliente-Administrador.ps1'
$process = Start-Process -FilePath 'powershell.exe' `
    -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File',"`"$AdminScript`"" `
    -Verb RunAs -Wait -PassThru

if ($process.ExitCode -ne 0) {
    throw "La configuracion del cliente termino con codigo $($process.ExitCode)."
}
