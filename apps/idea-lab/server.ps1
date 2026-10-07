param([int]$Port = 3212)

$ErrorActionPreference = 'Stop'
$labRoot = $PSScriptRoot
$distRoot = [IO.Path]::GetFullPath((Join-Path $labRoot 'dist'))
$dataDir = Join-Path $labRoot 'data'
$dataFile = Join-Path $dataDir 'workspace.json'
$backupDir = Join-Path $dataDir 'backups'
$sourceDir = Join-Path (Split-Path $labRoot -Parent) 'docs chatsgpt'
$utf8 = New-Object Text.UTF8Encoding($false)

New-Item -ItemType Directory -Path $dataDir -Force | Out-Null
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

function ConvertTo-JsonText($value, [int]$depth = 20) {
    return $value | ConvertTo-Json -Depth $depth -Compress
}

function Send-Response($stream, [int]$status, [string]$contentType, [byte[]]$body) {
    $reasons = @{ 200 = 'OK'; 201 = 'Created'; 204 = 'No Content'; 400 = 'Bad Request'; 404 = 'Not Found'; 405 = 'Method Not Allowed'; 413 = 'Payload Too Large'; 500 = 'Internal Server Error' }
    if ($null -eq $body) { $body = New-Object byte[] 0 }
    $reason = $reasons[$status]
    if (-not $reason) { $reason = 'Response' }
    $header = "HTTP/1.1 $status $reason`r`nContent-Type: $contentType`r`nContent-Length: $($body.Length)`r`nCache-Control: no-store, max-age=0`r`nX-Content-Type-Options: nosniff`r`nConnection: close`r`n`r`n"
    $headerBytes = [Text.Encoding]::ASCII.GetBytes($header)
    $stream.Write($headerBytes, 0, $headerBytes.Length)
    if ($body.Length) { $stream.Write($body, 0, $body.Length) }
    $stream.Flush()
}

function Send-Json($stream, [int]$status, $value) {
    $json = ConvertTo-JsonText $value
    Send-Response $stream $status 'application/json; charset=utf-8' $utf8.GetBytes($json)
}

function Read-Request($stream) {
    $headerBytes = New-Object 'System.Collections.Generic.List[byte]'
    $sequence = New-Object 'System.Collections.Generic.Queue[byte]'
    while ($headerBytes.Count -lt 65536) {
        $next = $stream.ReadByte()
        if ($next -lt 0) { break }
        $headerBytes.Add([byte]$next)
        $sequence.Enqueue([byte]$next)
        while ($sequence.Count -gt 4) { [void]$sequence.Dequeue() }
        if ($sequence.Count -eq 4) {
            $tail = $sequence.ToArray()
            if ($tail[0] -eq 13 -and $tail[1] -eq 10 -and $tail[2] -eq 13 -and $tail[3] -eq 10) { break }
        }
    }
    $headerText = [Text.Encoding]::ASCII.GetString($headerBytes.ToArray())
    $lines = $headerText -split "`r`n"
    if (-not $lines[0]) { return $null }
    $requestParts = $lines[0].Split(' ')
    if ($requestParts.Count -lt 2) { return $null }
    $headers = @{}
    for ($index = 1; $index -lt $lines.Count; $index++) {
        $separator = $lines[$index].IndexOf(':')
        if ($separator -gt 0) {
            $headers[$lines[$index].Substring(0, $separator).Trim().ToLowerInvariant()] = $lines[$index].Substring($separator + 1).Trim()
        }
    }
    $contentLength = 0
    if ($headers.ContainsKey('content-length')) { $contentLength = [int]$headers['content-length'] }
    if ($contentLength -gt 5242880) { return @{ TooLarge = $true } }
    $bodyBytes = New-Object byte[] $contentLength
    $offset = 0
    while ($offset -lt $contentLength) {
        $read = $stream.Read($bodyBytes, $offset, $contentLength - $offset)
        if ($read -le 0) { break }
        $offset += $read
    }
    return @{
        Method = $requestParts[0].ToUpperInvariant()
        Target = $requestParts[1]
        Headers = $headers
        Body = $utf8.GetString($bodyBytes, 0, $offset)
    }
}

function Save-Workspace([string]$body) {
    $parsed = $body | ConvertFrom-Json
    if ($null -eq $parsed.version -or $null -eq $parsed.ideas) { throw 'El espacio de trabajo no tiene una estructura válida.' }
    if (Test-Path -LiteralPath $dataFile) {
        $stamp = Get-Date -Format 'yyyyMMdd-HHmmss-fff'
        Copy-Item -LiteralPath $dataFile -Destination (Join-Path $backupDir "workspace-$stamp.json")
        $oldBackups = Get-ChildItem -LiteralPath $backupDir -Filter 'workspace-*.json' | Sort-Object LastWriteTime -Descending | Select-Object -Skip 60
        $oldBackups | Remove-Item -Force
    }
    $pretty = $parsed | ConvertTo-Json -Depth 30
    $tempFile = $dataFile + '.tmp'
    [IO.File]::WriteAllText($tempFile, $pretty, $utf8)
    Move-Item -LiteralPath $tempFile -Destination $dataFile -Force
}

function Get-SourceFiles {
    if (-not (Test-Path -LiteralPath $sourceDir)) { return @() }
    return @(Get-ChildItem -LiteralPath $sourceDir -Filter '*.json' -File | Sort-Object Name)
}

$listener = New-Object Net.Sockets.TcpListener([Net.IPAddress]::Loopback, $Port)
$listener.Start()
$running = $true
Write-Output "Laboratorio de Ideas L2 listo en http://127.0.0.1:$Port/"

try {
    while ($running) {
        $client = $listener.AcceptTcpClient()
        try {
            $client.ReceiveTimeout = 5000
            $stream = $client.GetStream()
            $request = Read-Request $stream
            if ($null -eq $request) { continue }
            if ($request.TooLarge) { Send-Json $stream 413 @{ error = 'La solicitud supera 5 MB.' }; continue }

            $targetUri = New-Object Uri(('http://127.0.0.1:' + $Port + $request.Target))
            $route = $targetUri.AbsolutePath

            if ($request.Method -eq 'GET' -and $route -eq '/api/health') {
                Send-Json $stream 200 @{ ok = $true; portable = $true; dataFile = $dataFile }
                continue
            }
            if ($request.Method -eq 'GET' -and $route -eq '/api/workspace') {
                if (-not (Test-Path -LiteralPath $dataFile)) { Send-Json $stream 404 @{ error = 'No se encontró workspace.json.' }; continue }
                Send-Response $stream 200 'application/json; charset=utf-8' ([IO.File]::ReadAllBytes($dataFile))
                continue
            }
            if ($request.Method -eq 'PUT' -and $route -eq '/api/workspace') {
                Save-Workspace $request.Body
                Send-Json $stream 200 @{ saved = $true; savedAt = [DateTimeOffset]::Now.ToUnixTimeMilliseconds() }
                continue
            }
            if ($request.Method -eq 'POST' -and $route -eq '/api/backup') {
                if (-not (Test-Path -LiteralPath $dataFile)) { Send-Json $stream 404 @{ error = 'No hay datos para respaldar.' }; continue }
                $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
                $backup = Join-Path $backupDir "manual-$stamp.json"
                Copy-Item -LiteralPath $dataFile -Destination $backup
                Send-Json $stream 201 @{ saved = $true; file = [IO.Path]::GetFileName($backup) }
                continue
            }
            if ($request.Method -eq 'GET' -and $route -eq '/api/sources') {
                $sources = @(Get-SourceFiles | ForEach-Object { @{ name = $_.Name; size = $_.Length; modified = ([DateTimeOffset]$_.LastWriteTime).ToUnixTimeMilliseconds() } })
                Send-Json $stream 200 $sources
                continue
            }
            if ($request.Method -eq 'GET' -and $route -eq '/api/source') {
                $requestedName = [Web.HttpUtility]::UrlDecode($targetUri.Query.TrimStart('?').Replace('name=', ''))
                $source = Get-SourceFiles | Where-Object { $_.Name -eq $requestedName } | Select-Object -First 1
                if (-not $source) { Send-Json $stream 404 @{ error = 'Fuente no encontrada.' }; continue }
                Send-Json $stream 200 @{ name = $source.Name; content = [IO.File]::ReadAllText($source.FullName, $utf8); modified = ([DateTimeOffset]$source.LastWriteTime).ToUnixTimeMilliseconds() }
                continue
            }
            if ($request.Method -eq 'POST' -and $route -eq '/api/shutdown') {
                Send-Json $stream 200 @{ stopping = $true }
                $running = $false
                continue
            }
            if ($request.Method -ne 'GET') { Send-Json $stream 405 @{ error = 'Método no permitido.' }; continue }

            $relative = [Web.HttpUtility]::UrlDecode($route.TrimStart('/'))
            if (-not $relative) { $relative = 'index.html' }
            $candidate = [IO.Path]::GetFullPath((Join-Path $distRoot $relative.Replace('/', [IO.Path]::DirectorySeparatorChar)))
            if (-not $candidate.StartsWith($distRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase) -and $candidate -ne (Join-Path $distRoot 'index.html')) {
                Send-Json $stream 404 @{ error = 'Ruta inválida.' }
                continue
            }
            if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) { Send-Json $stream 404 @{ error = 'Archivo no encontrado.' }; continue }
            $extensions = @{ '.html' = 'text/html; charset=utf-8'; '.css' = 'text/css; charset=utf-8'; '.js' = 'application/javascript; charset=utf-8'; '.svg' = 'image/svg+xml'; '.png' = 'image/png'; '.ico' = 'image/x-icon' }
            $extension = [IO.Path]::GetExtension($candidate).ToLowerInvariant()
            $mime = $extensions[$extension]
            if (-not $mime) { $mime = 'application/octet-stream' }
            Send-Response $stream 200 $mime ([IO.File]::ReadAllBytes($candidate))
        }
        catch {
            try { Send-Json $stream 500 @{ error = $_.Exception.Message } } catch {}
            Write-Error $_
        }
        finally {
            if ($stream) { $stream.Dispose() }
            $client.Close()
        }
    }
}
finally {
    $listener.Stop()
}

