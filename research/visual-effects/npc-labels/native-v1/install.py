"""Install the staged proof, preserving the current client and server files."""
from pathlib import Path
from datetime import datetime
import hashlib, json, shutil, subprocess

ROOT = Path(__file__).resolve().parents[4]
STAGE = Path(__file__).resolve().parent
CLIENT = ROOT.parent / 'l2/system-hud'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
proof = json.loads((STAGE / 'verification.json').read_text())
assert sha(CLIENT / 'npcgrp.dat') == proof['client_before_sha256'], 'Client changed after staging'
p = subprocess.run(['powershell.exe', '-NoProfile', '-Command',
                    "if (Get-Process L2 -ErrorAction SilentlyContinue) { exit 1 }"], capture_output=True)
assert p.returncode == 0, 'Close L2 before installing its files'
for file, schema in [('hellgames_label_test.xml', 'npcs.xsd'), ('HellgamesLabelTest.xml', 'spawns.xsd')]:
    validation = subprocess.run(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(STAGE / 'validate-xml.ps1'),
                                 str(STAGE / file), str(ROOT / 'server/game/data/xsd' / schema)], capture_output=True)
    assert validation.returncode == 0, (validation.stdout + validation.stderr).decode(errors='replace')

targets = [
    (STAGE / 'npcgrp.dat', CLIENT / 'npcgrp.dat'),
    (STAGE / 'HellgamesLabelsV1.u', CLIENT / 'HellgamesLabelsV1.u'),
    (STAGE / 'hellgames_label_test.xml', ROOT / 'server/game/data/stats/npcs/custom/hellgames_label_test.xml'),
    (STAGE / 'HellgamesLabelTest.xml', ROOT / 'server/game/data/lab/world-spawns/HellgamesLabelTest.xml'),
    (STAGE / '902530.htm', ROOT / 'server/game/data/html/default/902530.htm'),
]
assert all(not dest.exists() for _, dest in targets[1:]), 'A new target already exists'
backup = ROOT / 'backups' / ('hellgames-labels-v1-' + datetime.now().strftime('%Y%m%d-%H%M%S'))
backup.mkdir()
records = []
for i, (src, dest) in enumerate(targets):
    old = dest.exists()
    saved = backup / (str(i) + '-' + dest.name)
    if old:
        shutil.copy2(dest, saved)
    records.append(dict(target=str(dest), previous=str(saved) if old else None,
                        before=sha(dest) if old else None, installed=sha(src)))
(backup / 'manifest.json').write_text(json.dumps(records, indent=2), encoding='utf-8')
restore = '''$ErrorActionPreference='Stop'
if (Get-Process L2 -ErrorAction SilentlyContinue) { throw 'Cierra L2 antes de restaurar.' }
$records=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'manifest.json') -Raw | ConvertFrom-Json
foreach($r in $records) {
    if (!(Test-Path -LiteralPath $r.target)) { throw ('Falta '+$r.target) }
    if ((Get-FileHash -LiteralPath $r.target -Algorithm SHA256).Hash.ToLowerInvariant() -ne $r.installed) { throw ('Cambio posterior: '+$r.target) }
}
foreach($r in $records) {
    if($r.previous) { Copy-Item -LiteralPath $r.previous -Destination $r.target -Force }
    else { Remove-Item -LiteralPath $r.target }
}
Write-Host 'Archivos restaurados. Reinicia el GameServer sin jugadores conectados para retirar el NPC.'
'''
(backup / 'Restore.ps1').write_text(restore, encoding='utf-8-sig')
for src, dest in targets:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    assert sha(dest) == sha(src)
proof['installed'] = True
proof['backup'] = str(backup)
proof['location'] = [149140, 46700, -3400]
proof['server_xml_xsd_validation'] = True
proof['live_game_visual_validation'] = False
(STAGE / 'installed.json').write_text(json.dumps(proof, indent=2), encoding='utf-8')
print(json.dumps(proof))
