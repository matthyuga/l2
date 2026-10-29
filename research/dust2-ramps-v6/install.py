from pathlib import Path
import json,hashlib,shutil,subprocess,datetime
D=Path(__file__).resolve().parent;R=D.parents[1];C=R.parent/'l2';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not (D/'installation.json').exists(),'Already installed'
state=subprocess.check_output(['powershell.exe','-NoProfile','-Command',"if(Get-Process L2 -ErrorAction SilentlyContinue){'CLIENT'};exit 0"],text=True);assert not state.strip(),'L2 is open; close it before replacing the map'
for p,h in json.loads((D/'source-hashes.json').read_text()).items():assert sha(p)==h,'Concurrent edit '+p
assert not json.loads((D/'profile-audit.json').read_text())['discontinuities'],'Discontinuous ramp entry or exit'
v=json.loads((D/'verification.json').read_text());assert v['ramps']==32
files=[(C/'Maps/24_19.unr',D/'client/Maps/24_19.unr'),(R/'server/game/data/geodata/24_19.l2j',D/'stage/Geodata/24_19.l2j')]
backup=R/'backups'/('dust2-ramps-v6-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True);report=dict(version='ramps-v6',backup=str(backup),files=[],client_test_pending=True,ramps=32)
for target,source in files:
 saved=backup/target.name;shutil.copy2(target,saved);report['files'].append(dict(target=str(target),backup=str(saved),before_sha256=sha(target),after_sha256=sha(source)))
try:
 for target,source in files:shutil.copy2(source,target);assert sha(target)==sha(source)
except Exception:
 for row in report['files']:shutil.copy2(row['backup'],row['target'])
 raise
report['complete']=True
for dest in [D/'installation.json',backup/'manifest.json']:dest.write_text(json.dumps(report,indent=2))
for name in ['dust2-integration','dust2-scale-v2','dust2-fit-v3','dust2-stairs-v4','dust2-ramp-v5']:
 p=D.parent/name/'installation.json';m=json.loads(p.read_text(encoding='utf-8'));shutil.copy2(p,backup/(name+'-installation.json'))
 for row in m['files']:
  for new in report['files']:
   if Path(row['target'])==Path(new['target']):row['after_sha256']=new['after_sha256']
 m['current_version']='ramps-v6';m['ramps_v6']=report;m['client_physics_verified']=False;m['client_confirmation_applies_to']='V5 single captured staircase passed repeated ascent/descent; V6 map-wide rollout pending.'
 for dest in [p,Path(m['backup'])/'manifest.json']:dest.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
print('Installed32 stair supports, matching geodata and combined backup:',backup)
