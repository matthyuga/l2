from pathlib import Path
import datetime,hashlib,json,subprocess
base=Path(__file__).resolve().parent;root=base.parent.parent
previous=base.parent/'exploration-walking-v4/installation.json'
sha=lambda b:hashlib.sha256(b).hexdigest()
if subprocess.run(['powershell.exe','-NoProfile','-Command','if(Get-NetTCPConnection -LocalPort 7777 -State Established -ErrorAction SilentlyContinue){exit 10}']).returncode:
    raise SystemExit('Hay jugadores conectados; desconectar antes de instalar/reiniciar.')
manifest=json.loads(previous.read_text(encoding='utf8'))
files={}
for prefix in [root/'server/game',root/'source/L2J_Mobius_CT_0_Interlude/dist/game']:
    for name in ['ExplorationWalking.java','NativeExplorationZones.java','native-zones.xml','zone-masks.bin']:
        files[prefix/'data/scripts/custom/ExplorationWalking'/name]=(base/'server/custom/ExplorationWalking'/name).read_bytes()
records={item['path']:item for item in manifest['files']}
for target in files:
    if str(target) in records:
        if sha(target.read_bytes())!=records[str(target)]['after_sha256']:raise SystemExit('Archivo modificado: '+str(target))
    elif target.exists():raise SystemExit('Archivo nuevo ya existe: '+str(target))
backup=root/'backups'/('exploration-native-v5-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir()
(backup/'installation-before.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
patch=[]
for i,(target,data) in enumerate(files.items()):
    old=target.read_bytes() if target.exists() else None
    item=dict(path=str(target),before_sha256=sha(old) if old is not None else None,after_sha256=sha(data))
    if old is not None:
        saved=backup/(str(i)+'-'+target.name);saved.write_bytes(old);item['backup']=str(saved)
    patch.append(item)
(backup/'manifest.json').write_text(json.dumps(patch,indent=2),encoding='utf8')
try:
    for target,data in files.items():target.write_bytes(data);assert sha(target.read_bytes())==sha(data)
except Exception:
    for item in patch:
        p=Path(item['path'])
        if 'backup' in item:p.write_bytes(Path(item['backup']).read_bytes())
        else:p.unlink(missing_ok=True)
    raise
for item in patch:
    if item['path'] in records:records[item['path']]['after_sha256']=item['after_sha256']
    else:manifest['files'].append(item)
manifest.update(state='native-v5-installed-pending-restart',native_v5_backup=str(backup),runtime_visual_validation='V4.1 fog confirmed; V5 native discovery pending user test')
previous.write_text(json.dumps(manifest,indent=2),encoding='utf8')
(base/'installation.json').write_text(json.dumps(dict(state=manifest['state'],backup=str(backup),files=patch,runtime_visual_validation=manifest['runtime_visual_validation']),indent=2),encoding='utf8')
print('V5 native locations installed; backup:',backup)
