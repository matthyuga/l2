from pathlib import Path
import hashlib, json, shutil, subprocess

root = Path(__file__).resolve().parent
manifest = json.loads((root / 'installation.json').read_text(encoding='utf-8'))
processes = subprocess.run(['tasklist.exe', '/FI', 'IMAGENAME eq L2.exe', '/FO', 'CSV', '/NH'], capture_output=True, text=True, check=True).stdout
if '"l2.exe"' in processes.lower():
    raise SystemExit('Cerrar L2 antes de restaurar.')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
target, backup = Path(manifest['target']), Path(manifest['backup'])
if sha(target) != manifest['after_sha256'] or sha(backup) != manifest['before_sha256']:
    raise SystemExit('Identidad inesperada; no se sobrescribe.')
shutil.copy2(backup, target)
assert sha(target) == manifest['before_sha256']
manifest['state'] = 'restored-v7'
(root / 'installation.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
print('Restaurada V7. Datos y servidor conservados.')
