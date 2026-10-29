$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$Settings = New-Object System.Xml.XmlReaderSettings
$Settings.ValidationType = [System.Xml.ValidationType]::Schema
[void]$Settings.Schemas.Add('', (Join-Path $ProjectRoot 'server\game\data\xsd\npcs.xsd'))
$Reader = [System.Xml.XmlReader]::Create((Join-Path $PSScriptRoot 'exports\amber_lab.xml'), $Settings)
try { while ($Reader.Read()) { }; Write-Host 'XML de Amber valido contra npcs.xsd.' }
finally { $Reader.Dispose() }
