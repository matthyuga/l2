param(
    [Parameter(Mandatory = $true)]
    [string] $InputPath,

    [Parameter(Mandatory = $true)]
    [string] $OutputPath
)

$ErrorActionPreference = 'Stop'

function Read-CompactInt {
    param([IO.BinaryReader] $Reader)

    [int] $first = $Reader.ReadByte()
    [long] $value = $first -band 0x3f
    [int] $shift = 6
    [bool] $more = ($first -band 0x40) -ne 0

    while ($more) {
        [int] $next = $Reader.ReadByte()
        $value = $value -bor (([long] ($next -band 0x7f)) -shl $shift)
        $more = ($next -band 0x80) -ne 0
        $shift += 7
        if ($shift -gt 34) {
            throw 'Invalid compact integer in systemmsg file.'
        }
    }

    if (($first -band 0x80) -ne 0) {
        return [int] (-$value)
    }
    return [int] $value
}

function Read-ASCF {
    param([IO.BinaryReader] $Reader)

    [int] $length = Read-CompactInt $Reader
    if ($length -eq 0) {
        return ''
    }

    if ($length -gt 0) {
        [byte[]] $bytes = $Reader.ReadBytes($length)
        if ($bytes.Length -ne $length) {
            throw 'Unexpected end of ANSI string in systemmsg file.'
        }
        return [Text.Encoding]::GetEncoding(1252).GetString($bytes, 0, $length - 1)
    }

    [int] $characterCount = -$length
    [byte[]] $unicodeBytes = $Reader.ReadBytes($characterCount * 2)
    if ($unicodeBytes.Length -ne ($characterCount * 2)) {
        throw 'Unexpected end of Unicode string in systemmsg file.'
    }
    return [Text.Encoding]::Unicode.GetString($unicodeBytes, 0, ($characterCount - 1) * 2)
}

function Write-CompactInt {
    param(
        [IO.BinaryWriter] $Writer,
        [int] $Value
    )

    [bool] $negative = $Value -lt 0
    [uint64] $remaining = [Math]::Abs([long] $Value)
    [byte] $first = [byte] ($remaining -band 0x3f)
    $remaining = $remaining -shr 6
    if ($negative) {
        $first = $first -bor 0x80
    }
    if ($remaining -ne 0) {
        $first = $first -bor 0x40
    }
    $Writer.Write($first)

    while ($remaining -ne 0) {
        [byte] $next = [byte] ($remaining -band 0x7f)
        $remaining = $remaining -shr 7
        if ($remaining -ne 0) {
            $next = $next -bor 0x80
        }
        $Writer.Write($next)
    }
}

function Write-ASCF {
    param(
        [IO.BinaryWriter] $Writer,
        [string] $Value
    )

    if ([string]::IsNullOrEmpty($Value)) {
        Write-CompactInt $Writer 0
        return
    }

    [byte[]] $bytes = [Text.Encoding]::GetEncoding(1252).GetBytes($Value)
    Write-CompactInt $Writer ($bytes.Length + 1)
    $Writer.Write($bytes)
    $Writer.Write([byte] 0)
}

function Read-Record {
    param([IO.BinaryReader] $Reader)

    [uint32] $id = $Reader.ReadUInt32()
    [void] $Reader.ReadUInt32()
    [void] (Read-ASCF $Reader)
    [void] $Reader.ReadUInt32()
    [void] $Reader.ReadBytes(4)
    [void] (Read-ASCF $Reader)
    [void] (Read-ASCF $Reader)
    for ($index = 0; $index -lt 5; $index++) {
        [void] $Reader.ReadUInt32()
    }
    [void] (Read-ASCF $Reader)
    [void] (Read-ASCF $Reader)
    return $id
}

function Write-Record {
    param(
        [IO.BinaryWriter] $Writer,
        [uint32] $Id,
        [string] $Message,
        [byte[]] $Color
    )

    $Writer.Write($Id)
    $Writer.Write([uint32] 1)
    Write-ASCF $Writer $Message
    $Writer.Write([uint32] 3) # damage group
    $Writer.Write($Color)
    Write-ASCF $Writer '' # item sound
    Write-ASCF $Writer '' # system message reference
    $Writer.Write([uint32] 5) # same native on-screen location as outgoing damage
    $Writer.Write([uint32] 0)
    $Writer.Write([uint32] 1) # one second
    $Writer.Write([uint32] 1) # enable on-screen display
    $Writer.Write([uint32] 0)
    Write-ASCF $Writer '-$s2'
    Write-ASCF $Writer 'damage'
}

[byte[]] $original = [IO.File]::ReadAllBytes($InputPath)
$inputStream = [IO.MemoryStream]::new($original, $false)
$reader = [IO.BinaryReader]::new($inputStream)

try {
    [uint32] $recordCount = $reader.ReadUInt32()
    $ids = [Collections.Generic.HashSet[uint32]]::new()
    for ($index = 0; $index -lt $recordCount; $index++) {
        [void] $ids.Add((Read-Record $reader))
    }

    [long] $recordsEnd = $inputStream.Position
    [string] $footer = Read-ASCF $reader
    if (($footer -ne 'SafePackage') -or ($inputStream.Position -ne $inputStream.Length)) {
        throw "Unexpected systemmsg footer or trailing data (footer='$footer')."
    }

    [uint32[]] $customIds = 2204, 2205, 2206, 2207
    foreach ($id in $customIds) {
        if ($ids.Contains($id)) {
            throw "System message id $id already exists. Refusing to create a duplicate."
        }
    }

    $outputStream = [IO.MemoryStream]::new()
    $writer = [IO.BinaryWriter]::new($outputStream)
    try {
        $writer.Write([uint32] ($recordCount + $customIds.Length))
        $writer.Write($original, 4, [int] ($recordsEnd - 4))

        Write-Record $writer 2204 '[ENEMIGO] $s1: recibes $s2 de dano fisico.' ([byte[]] (255, 180, 100, 255))
        Write-Record $writer 2205 '[ENEMIGO] $s1: recibes $s2 de CRITICO fisico.' ([byte[]] (255, 80, 80, 255))
        Write-Record $writer 2206 '[ENEMIGO] $s1: recibes $s2 de dano magico.' ([byte[]] (255, 130, 180, 255))
        Write-Record $writer 2207 '[ENEMIGO] $s1: recibes $s2 de CRITICO magico.' ([byte[]] (255, 70, 140, 255))

        $writer.Write($original, [int] $recordsEnd, [int] ($original.Length - $recordsEnd))
        $writer.Flush()
        [IO.File]::WriteAllBytes($OutputPath, $outputStream.ToArray())
    }
    finally {
        $writer.Dispose()
        $outputStream.Dispose()
    }

    Write-Output "Patched $recordCount -> $($recordCount + $customIds.Length) records."
    Write-Output 'Added incoming ids 2204-2207; existing records and SafePackage footer preserved. No per-message shadow field is modified.'
}
finally {
    $reader.Dispose()
    $inputStream.Dispose()
}
