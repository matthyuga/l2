from pathlib import Path
import datetime
import hashlib
import json
import subprocess

lab = Path(__file__).resolve().parent
root = lab.parent.parent
client = root.parent / 'l2/system-hud'
expected = 'a8bda77a97cd3e8583ce61e227380303212dbfc25ae10f8907106379fec3f292'
sha = lambda data: hashlib.sha256(data).hexdigest()
if sha((client / 'NWindow.dll').read_bytes()) != expected:
    raise SystemExit('El cliente cambio: no se instala sobre una DLL diferente.')
running = subprocess.run(['powershell.exe', '-NoProfile', '-Command',
                          "if(Get-Process -Name L2 -ErrorAction SilentlyContinue){exit 9}"], capture_output=True)
if running.returncode != 0:
    raise SystemExit('Cierra L2 antes de instalar; no se modifico ningun archivo.')
files = {client / 'd3d9.dll': (lab / 'build/d3d9.dll').read_bytes(),
         client / 'NexusMapFog.ini': (lab / 'NexusMapFog.ini').read_bytes()}
actions = {'1-PARCIAL': 'partial', '2-OPACA': 'total', '3-APAGAR': 'off', '4-CENTRAR': 'anchor'}
for label, action in actions.items():
    files[root / ('NIEBLA-' + label + '.cmd')] = (
        '@echo off\r\npython "%~dp0research\\map-fog-native-v1\\control.py" ' + action + '\r\n'
        'if errorlevel 1 pause\r\n').encode('ascii')
for target in files:
    if target.exists():
        raise SystemExit('Ya existe, no se sobrescribe: ' + str(target))
backup = root / 'backups' / ('map-fog-native-v1-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
backup.mkdir(parents=True)
records = []
try:
    for target, data in files.items():
        target.write_bytes(data)
        assert sha(target.read_bytes()) == sha(data)
        records.append({'path': str(target), 'sha256': sha(data), 'previously_existed': False})
except Exception:
    for record in reversed(records):
        path = Path(record['path'])
        if path.exists() and sha(path.read_bytes()) == record['sha256']:
            path.unlink()
    raise
manifest = {'state': 'installed-pending-client-launch', 'nwindow_sha256': expected,
            'files': records, 'client_binary_files_modified': [],
            'server_changed': False, 'runtime_visual_validation': 'pending',
            'diagnostic_only': True, 'mode': 'partial', 'backup': str(backup)}
(backup / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf8')
(lab / 'installation.json').write_text(json.dumps(manifest, indent=2), encoding='utf8')
print('INSTALADO: cobertura nativa de diagnostico; esperando inicio del cliente.')
print('NWindow.dll e Interface.u/XDAT conservados. Manifiesto:', backup / 'manifest.json')
