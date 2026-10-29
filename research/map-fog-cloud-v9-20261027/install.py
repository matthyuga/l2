from pathlib import Path
import hashlib, json, shutil, subprocess, datetime

root = Path(__file__).resolve().parent
target = Path(r'E:\l2\system-hud\d3d9.dll')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
expected = 'e7a845ebf8e7b7f223fee839398a14c7142b1be238470144171f85c020dd4750'

def require_closed():
    processes = subprocess.run(['tasklist.exe', '/FI', 'IMAGENAME eq L2.exe', '/FO', 'CSV', '/NH'], capture_output=True, text=True, check=True).stdout
    if '"l2.exe"' in processes.lower():
        raise SystemExit('Cerrar L2 antes de instalar. No se cambio ningun archivo.')

require_closed()
if sha(target) != expected:
    raise SystemExit('El proxy actual difiere de V8. No se sobrescribe.')
guards = {
    'NWindow.dll': 'a4de43d5d31241daae7dac072134c011abdd036b0d1ee291eead0bb5e9c6ca7d',
    'D3DDrv.dll': '2b496d235cca529b6180588a987ca0059600a2323193d96e87b90014105be0c2',
}
for name, digest in guards.items():
    if sha(target.parent / name) != digest:
        raise SystemExit(f'{name} cambio; revisar compatibilidad antes de instalar.')
source = root / 'build/d3d9.dll'
verification = json.loads((root / 'verification.json').read_text(encoding='utf-8'))
if verification['candidate_sha256'] != sha(source) or not verification['checks_passed']:
    raise SystemExit('La DLL no coincide con el candidato verificado.')
stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
backup = Path(r'E:\l2-local\backups') / ('map-fog-cloud-v9-' + stamp)
backup.mkdir()
shutil.copy2(target, backup / 'd3d9.dll')
log = target.parent / 'NexusMapFog.log'
if log.exists():
    shutil.copy2(log, backup / 'NexusMapFog-before.log')
require_closed()
manifest = {'state': 'installed-awaiting-in-game-validation', 'target': str(target), 'backup': str(backup / 'd3d9.dll'), 'before_sha256': expected, 'after_sha256': sha(source), 'guards': guards, 'server_changed': False, 'exploration_data_changed': False, 'client_closed_at_install': True}
shutil.copy2(source, target)
assert sha(target) == manifest['after_sha256']
(root / 'installation.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
(backup / 'installation.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
print('INSTALLED V9. Solo d3d9.dll; servidor, HSL y progreso conservados.')
print('Backup:', backup)
