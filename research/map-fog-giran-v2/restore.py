from pathlib import Path
import hashlib
import json
import subprocess
base=Path(__file__).resolve().parent
root=base.parent.parent;client=root.parent/'l2/system-hud'
record=json.loads((base/'installation.json').read_text(encoding='utf8'))
check=subprocess.run(['powershell.exe','-NoProfile','-Command',"if(Get-Process -Name L2 -ErrorAction SilentlyContinue){exit 9}"],capture_output=True)
if check.returncode:raise SystemExit('Cierra L2 antes de restaurar.')
for item in record['files']:
    path=Path(item['path'])
    if path.parent not in (client,base.parent/'map-fog-native-v1'):raise SystemExit('Destino fuera del alcance: '+str(path))
    if not path.exists():raise SystemExit('Archivo ausente; revisar antes de restaurar: '+str(path))
    if path.name=='NexusMapFog.ini':
        if 'Layout=GiranV2' not in path.read_text(encoding='ascii'):raise SystemExit('INI no reconocido.')
    elif hashlib.sha256(path.read_bytes()).hexdigest()!=item['after_sha256']:raise SystemExit('Archivo cambiado: '+str(path))
for item in record['files']:
    path=Path(item['path'])
    if 'backup' in item:
        data=Path(item['backup']).read_bytes()
        assert hashlib.sha256(data).hexdigest()==item['before_sha256']
        path.write_bytes(data)
    else:path.unlink()
record['state']='restored-to-v1'
(base/'installation.json').write_text(json.dumps(record,indent=2),encoding='utf8')
print('Restaurada la version V1 del rectangulo. Para quitarla, usar despues map-fog-native-v1/restore.py.')
