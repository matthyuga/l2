from pathlib import Path
import json,hashlib,shutil,datetime,subprocess
D=Path(__file__).resolve().parent;R=D.parents[1];C=R.parent/'l2';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
state=subprocess.check_output(['powershell.exe','-NoProfile','-Command',"if(Get-Process L2 -ErrorAction SilentlyContinue){'CLIENT'};Get-CimInstance Win32_Process -Filter \"Name = 'java.exe'\" | Where-Object {$_.CommandLine -match 'GameServer.jar'} | ForEach-Object {'SERVER'};exit 0"],text=True);assert not state.strip(),state
assert not (D/'installation.json').exists(),'Already installed'
for p,h in json.loads((D/'source-hashes.json').read_text()).items():assert sha(p)==h,'Concurrent edit '+p
assert json.loads((D/'verification.json').read_text())['clearance']['connected_spawns']==40
files=[(C/'Maps/24_19.unr',D/'client/Maps/24_19.unr'),(R/'server/game/data/geodata/24_19.l2j',D/'stage/Geodata/24_19.l2j')]
for p in (D/'stage/server').rglob('*'):
 if p.is_file():
  for base in [R/'server/game',R/'source/L2J_Mobius_CT_0_Interlude/dist/game',R/'cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/dist/game']:files.append((base/p.relative_to(D/'stage/server'),p))
backup=R/'backups'/('dust2-fit-v3-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True);report=dict(backup=str(backup),version='fit-v3',files=[],client_test_pending=True,exit_critical_unresolved=True)
def record():
 for p in [D/'installation.json',backup/'manifest.json']:p.write_text(json.dumps(report,indent=2),encoding='utf-8')
record()
try:
 for target,source in files:
  saved=backup/('client' if target.is_relative_to(C) else 'project')/(target.relative_to(C) if target.is_relative_to(C) else target.relative_to(R));saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,saved)
  report['files'].append(dict(target=str(target),backup=str(saved),before_sha256=sha(target),after_sha256=sha(source)));record();shutil.copy2(source,target);assert sha(target)==sha(source)
except Exception:
 for row in reversed(report['files']):shutil.copy2(row['backup'],row['target'])
 report['rolled_back']=True;record();raise
report['complete']=True;record()
for manifest in [D.parent/'dust2-integration/installation.json',D.parent/'dust2-scale-v2/installation.json']:
 m=json.loads(manifest.read_text(encoding='utf-8'))
 for row in report['files']:
  for old in m['files']:
   if Path(old['target'])==Path(row['target']):old['after_sha256']=row['after_sha256']
 m['current_version']='fit-v3';m['fit_v3']=report;m['client_physics_verified']=False;m['client_confirmation_applies_to']='Earlier large version; V2 failed door/feet test. V3 pending.'
 manifest.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
 (Path(m['backup'])/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
print('INSTALLED FIT V3',len(files),'files; backup',backup)
