from pathlib import Path
import subprocess,hashlib,json,datetime
base=Path(__file__).resolve().parent;root=base.parent.parent;client=root.parent/'l2/system-hud';target=client/'d3d9.dll'
sha=lambda b:hashlib.sha256(b).hexdigest()
if subprocess.run(['powershell.exe','-NoProfile','-Command','if(Get-Process L2 -ErrorAction SilentlyContinue){exit 9}']).returncode:
    raise SystemExit('L2 esta abierto. Cerrar antes de reemplazar DLL.')
mp=base.parent/'exploration-walking-v4/installation.json';manifest=json.loads(mp.read_text(encoding='utf8'))
record=next(r for r in manifest['files'] if Path(r['path'])==target)
old=target.read_bytes();new=(base/'build/d3d9.dll').read_bytes()
if sha(old)!=record['after_sha256']:raise SystemExit('DLL instalada modificada fuera del manifiesto; se cancela.')
backup=root/'backups'/('map-fog-render-v6-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir()
(backup/'d3d9.dll').write_bytes(old);(backup/'installation-before.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
patch=dict(state='installed-pending-client-test',backup=str(backup),path=str(target),before_sha256=sha(old),after_sha256=sha(new),server_restarted=False)
(backup/'manifest.json').write_text(json.dumps(patch,indent=2),encoding='utf8')
try:target.write_bytes(new);assert sha(target.read_bytes())==sha(new)
except Exception:target.write_bytes(old);raise
record['after_sha256']=sha(new);manifest.update(state='native-v5-plus-render-v6-pending-client-test',render_v6_backup=str(backup),runtime_visual_validation='V6 native texture identity and Present refresh awaiting game test')
mp.write_text(json.dumps(manifest,indent=2),encoding='utf8');(base/'installation.json').write_text(json.dumps(patch,indent=2),encoding='utf8')
print('V6 renderer installed; server and saved exploration unchanged; backup:',backup)
