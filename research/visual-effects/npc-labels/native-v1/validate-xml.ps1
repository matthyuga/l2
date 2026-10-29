param([string]$DocumentPath,[string]$SchemaPath)
$ErrorActionPreference='Stop'
$settings=[System.Xml.XmlReaderSettings]::new()
$settings.ValidationType=[System.Xml.ValidationType]::Schema
$null=$settings.Schemas.Add($null,$SchemaPath)
$settings.add_ValidationEventHandler({ param($sender,$eventArgs) throw $eventArgs.Message })
$reader=[System.Xml.XmlReader]::Create($DocumentPath,$settings)
try { while($reader.Read()) {} } finally { $reader.Dispose() }
Write-Host 'PASS: XML schema validation.'
