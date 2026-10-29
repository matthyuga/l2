from pathlib import Path
import datetime
import hashlib
import json
import subprocess

base=Path(__file__).resolve().parent
root=base.parent.parent
client=root.parent/'l2/system-hud'
sha=lambda b:hashlib.sha256(b).hexdigest()
check=subprocess.run(['powershell.exe','-NoProfile','-Command',"if(Get-Process -Name L2 -ErrorAction SilentlyContinue){exit 9}"],capture_output=True)
if check.returncode:raise SystemExit('L2 sigue abierto; no se instala.')
expected='a8bda77a97cd3e8583ce61e227380303212dbfc25ae10f8907106379fec3f292'
if sha((client/'NWindow.dll').read_bytes())!=expected:raise SystemExit('NWindow cambio; se cancela.')
v1=json.loads((base.parent/'map-fog-native-v1/installation.json').read_text(encoding='utf8'))
oldDll=next(x for x in v1['files'] if Path(x['path']).name=='d3d9.dll')
if sha((client/'d3d9.dll').read_bytes())!=oldDll['sha256']:raise SystemExit('El proxy instalado no es V1; se cancela.')
newPackage=client/'NexusMapFogV2.u'
if newPackage.exists():raise SystemExit('El paquete V2 ya existe; no se sobrescribe.')
control=base.parent/'map-fog-native-v1/control.py'
controlText=control.read_text(encoding='utf8')
controlText=controlText.replace("key = 'Revision' if action == 'anchor' else 'Mode'", "if action == 'anchor' and 'Layout=GiranV2' in text:\n    print('Giran tiene una ubicacion fija: esta version ya no necesita centrar el rectangulo.')\n    raise SystemExit(0)\nkey = 'Revision' if action == 'anchor' else 'Mode'")
files={client/'d3d9.dll':(base/'build/d3d9.dll').read_bytes(),
       client/'NexusMapFog.ini':(base/'NexusMapFog.ini').read_bytes(),
       newPackage:(base/'build/NexusMapFogV2.u').read_bytes(),
       control:controlText.encode('utf8')}
backup=root/'backups'/('map-fog-giran-v2-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True)
manifest=[]
for path,data in files.items():
    old=path.read_bytes() if path.exists() else None
    item={'path':str(path),'before_sha256':sha(old) if old is not None else None,'after_sha256':sha(data)}
    if old is not None:
        name=('client-' if path.parent==client else 'project-')+path.name
        saved=backup/name;saved.write_bytes(old);item['backup']=str(saved)
    manifest.append(item)
(backup/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
written=[]
try:
    for (path,data),item in zip(files.items(),manifest):
        path.write_bytes(data);written.append(item)
        assert sha(path.read_bytes())==item['after_sha256']
except Exception:
    for item in reversed(written):
        path=Path(item['path'])
        if 'backup' in item:path.write_bytes(Path(item['backup']).read_bytes())
        else:path.unlink(missing_ok=True)
    raise
result={'state':'installed-pending-client-launch','backup':str(backup),'files':manifest,
        'client_original_nwindow_sha256':expected,'server_changed':False,'visual_validation':'pending'}
(base/'installation.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print('INSTALADO V2: niebla opaca en todo el mapa, Giran despejada con borde suave. Backup:',backup)
