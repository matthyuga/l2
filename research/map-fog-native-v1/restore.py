from pathlib import Path
import hashlib
import json
import subprocess
lab = Path(__file__).resolve().parent
root = lab.parent.parent
client = root.parent / 'l2/system-hud'
manifest = json.loads((lab / 'installation.json').read_text(encoding='utf8'))
running = subprocess.run(['powershell.exe', '-NoProfile', '-Command',
                          "if(Get-Process -Name L2 -ErrorAction SilentlyContinue){exit 9}"], capture_output=True)
if running.returncode != 0:
    raise SystemExit('Cierra L2 antes de restaurar.')
for item in manifest['files']:
    path = Path(item['path'])
    if path.parent not in (root, client):
        raise SystemExit('Destino fuera del alcance previsto: ' + str(path))
    if not path.exists():
        continue
    data = path.read_bytes()
    if path.name == 'NexusMapFog.ini':
        # The diagnostic controls intentionally change this new file.
        if not data.startswith(b'[MapFog]'):
            raise SystemExit('INI no reconocido; no se elimina.')
    elif hashlib.sha256(data).hexdigest() != item['sha256']:
        raise SystemExit('Archivo cambiado; no se elimina: ' + str(path))
for item in manifest['files']:
    Path(item['path']).unlink(missing_ok=True)
manifest['state'] = 'restored'
(lab / 'installation.json').write_text(json.dumps(manifest, indent=2), encoding='utf8')
print('Restaurado: retirados solamente el cargador y los controles nuevos de niebla.')
