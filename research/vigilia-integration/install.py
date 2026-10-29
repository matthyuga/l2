from pathlib import Path
import sys,json,hashlib,shutil,datetime,subprocess
D=Path(__file__).resolve().parent;ROOT=D.parents[1];CLIENT=ROOT.parent/'l2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
state=subprocess.check_output(['powershell.exe','-NoProfile','-Command',"if(Get-Process l2 -ErrorAction SilentlyContinue){'CLIENT'};if(Get-NetTCPConnection -LocalPort 7777 -State Listen -ErrorAction SilentlyContinue){'SERVER'};Get-CimInstance Win32_Process -Filter \"Name = 'java.exe'\" | Where-Object {$_.CommandLine -match 'GameServer.jar'} | ForEach-Object {'GAME_PROCESS'};exit 0"],text=True)
assert not state.strip(),'Client/GameServer must be closed: '+state
if '--restore' in sys.argv:
 m=json.loads((D/'installation.json').read_text());assert m['installed']
 for row in m['files']:assert sha(row['target'])==row['after_sha256'],'Changed since Vigilia installation: '+row['target']
 for row in reversed(m['files']):
  p=Path(row['target'])
  if row['backup']:shutil.copy2(row['backup'],p)
  else:p.unlink()
 m['installed']=False;m['restored']=True;(D/'installation.json').write_text(json.dumps(m,indent=2));print('Vigilia restored; prior map/geodata/server files reinstated.');sys.exit(0)
assert not (D/'installation.json').exists(),'Inspect existing installation manifest'
v=json.loads((D/'verification.json').read_text());assert v['native_load'] and v['wall_conflicts']==0 and v['encrypted_roundtrip_crc']
build=json.loads((D/'build-audit.json').read_text());geo=json.loads((D/'geodata-audit.json').read_text())
assert sha(CLIENT/'Maps/24_19.unr')==build['source_map_sha256'],'Concurrent map change'
assert sha(ROOT/'server/game/data/geodata/24_19.l2j')==geo['source_sha256'],'Concurrent geodata change'
files=[(CLIENT/rel,D/'client'/rel) for rel in ['StaticMeshes/HGVigilia.usx','Maps/24_19.unr']]
assert not files[0][0].exists(),'Package name already exists'
files.append((ROOT/'server/game/data/geodata/24_19.l2j',D/'stage/Geodata/24_19.l2j'))
for row in json.loads((D/'server-source-hashes.json').read_text()):
 p=ROOT/row['relative'];assert (sha(p) if p.exists() else None)==row['before'],'Concurrent source change: '+str(p)
 files.append((p,D/'stage/project'/row['relative']))
backup=ROOT/'backups'/('vigilia-integration-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True)
m=dict(backup=str(backup),installed=False,stationary=True,client_visual_verified=False,files=[])
for target,source in files:
 saved=backup/('client' if target.is_relative_to(CLIENT) else 'project')/(target.relative_to(CLIENT) if target.is_relative_to(CLIENT) else target.relative_to(ROOT))
 existed=target.exists()
 if existed:saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,saved)
 m['files'].append(dict(target=str(target),source=str(source),backup=str(saved) if existed else None,before_sha256=sha(target) if existed else None,after_sha256=sha(source)))
def record():
 s=json.dumps(m,indent=2);(D/'installation.json').write_text(s);(backup/'manifest.json').write_text(s)
record()
try:
 for row in m['files']:
  p=Path(row['target']);p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(row['source'],p);assert sha(p)==row['after_sha256']
 m['installed']=True;record()
except Exception:
 for row in reversed(m['files']):
  p=Path(row['target'])
  if row['backup']:shutil.copy2(row['backup'],p)
  elif p.exists():p.unlink()
 m['rolled_back']=True;record();raise
print('INSTALLED',len(files),'files; backup',backup)
