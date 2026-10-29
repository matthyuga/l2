import pathlib,subprocess,json,hashlib,shutil,datetime
D=pathlib.Path(__file__).resolve().parent;ROOT=D.parents[1];CLIENT=ROOT.parent/'l2';OLD=ROOT/'research/dust2-integration';sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
state=subprocess.check_output(['powershell.exe','-NoProfile','-Command',"if(Get-Process l2 -ErrorAction SilentlyContinue){'CLIENT'};Get-CimInstance Win32_Process -Filter \"Name = 'java.exe'\" | Where-Object {$_.CommandLine -match 'GameServer.jar'} | ForEach-Object {'SERVER'};exit 0"],text=True)
assert not state.strip(),'Close client/GameServer: '+state
assert not (D/'installation.json').exists(),'Already installed'
for p,h in json.loads((D/'source-hashes.json').read_text()).items():assert sha(p)==h,'Concurrent edit: '+p
v=json.loads((D/'verification.json').read_text());assert v['visual_actor_scales_verified']==37 and v['old_collision_references_removed']==3176
files=[(CLIENT/'Maps/24_19.unr',D/'client/Maps/24_19.unr'),(CLIENT/'StaticMeshes/HGDust2Arena.usx',D/'client/StaticMeshes/HGDust2Arena.usx'),(ROOT/'server/game/data/geodata/24_19.l2j',D/'stage/Geodata/24_19.l2j')]
for p in (D/'stage/server').rglob('*'):
 if p.is_file():
  rel=p.relative_to(D/'stage/server')
  for root in [ROOT/'server/game',ROOT/'source/L2J_Mobius_CT_0_Interlude/dist/game',ROOT/'cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/dist/game']:files.append((root/rel,p))
backup=ROOT/'backups'/('dust2-scale-v2-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True);report=dict(backup=str(backup),files=[],version='scale-v2',client_test_pending=True)
def record():(D/'installation.json').write_text(json.dumps(report,indent=2));(backup/'manifest.json').write_text(json.dumps(report,indent=2))
record()
try:
 for target,source in files:
  saved=backup/('client' if target.is_relative_to(CLIENT) else 'project')/(target.relative_to(CLIENT) if target.is_relative_to(CLIENT) else target.relative_to(ROOT));saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,saved)
  report['files'].append(dict(target=str(target),backup=str(saved),before_sha256=sha(target),after_sha256=sha(source)));record();shutil.copy2(source,target);assert sha(target)==sha(source)
except Exception:
 for row in reversed(report['files']):shutil.copy2(row['backup'],row['target'])
 report['rolled_back']=True;record();raise
report['complete']=True;record();m=json.loads((OLD/'installation.json').read_text(encoding='utf-8'))
for row in report['files']:
 item=next(i for i in m['files'] if pathlib.Path(i['target'])==pathlib.Path(row['target']));item['after_sha256']=row['after_sha256']
m['scale_v2']=report;m['current_version']='scale-v2';m['client_physics_verified']=False;m['client_confirmation_applies_to']='Prior large-scale version only'
(OLD/'installation.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8');(pathlib.Path(m['backup'])/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8');print('SCALE_V2_INSTALLED',len(files),'files; backup',backup)
