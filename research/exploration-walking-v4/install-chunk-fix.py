from pathlib import Path
import datetime,hashlib,json,subprocess
base=Path(__file__).resolve().parent;root=base.parent.parent
sha=lambda b:hashlib.sha256(b).hexdigest()
if subprocess.run(['powershell.exe','-NoProfile','-Command','if(Get-Process L2 -ErrorAction SilentlyContinue){exit 9}; if(Get-NetTCPConnection -LocalPort 7777 -State Established -ErrorAction SilentlyContinue){exit 10}']).returncode:
    raise SystemExit('L2 sigue abierto o hay jugadores conectados; no se instala.')
manifest=json.loads((base/'installation.json').read_text(encoding='utf8'))
files={root.parent/'l2/system-hud/d3d9.dll':(base.parent/'map-fog-walking-v4/build/d3d9.dll').read_bytes()}
for prefix in [root/'server/game',root/'source/L2J_Mobius_CT_0_Interlude/dist/game']:
    for source in (base/'server/custom/ExplorationWalking').glob('*.java'):
        files[prefix/'data/scripts/custom/ExplorationWalking'/source.name]=source.read_bytes()
records={item['path']:item for item in manifest['files']}
for target in files:
    if sha(target.read_bytes())!=records[str(target)]['after_sha256']:raise SystemExit('Archivo cambio fuera de V4: '+str(target))
backup=root/'backups'/('exploration-walking-v4-chunks-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir()
(backup/'installation-before.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
patch=[]
for i,(target,data) in enumerate(files.items()):
    old=target.read_bytes();saved=backup/(str(i)+'-'+target.name);saved.write_bytes(old)
    patch.append({'path':str(target),'backup':str(saved),'before_sha256':sha(old),'after_sha256':sha(data)})
(backup/'manifest.json').write_text(json.dumps(patch,indent=2),encoding='utf8')
try:
    for target,data in files.items():
        target.write_bytes(data);assert sha(target.read_bytes())==sha(data)
        records[str(target)]['after_sha256']=sha(data)
except Exception:
    for item in patch:Path(item['path']).write_bytes(Path(item['backup']).read_bytes())
    raise
manifest.update(state='chunk-fix-installed-pending-server-restart',chunk_fix_backup=str(backup),runtime_visual_validation='pending V4.1 user test')
(base/'installation.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
print('V4.1 installed; backup:',backup)
