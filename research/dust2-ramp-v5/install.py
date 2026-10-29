from pathlib import Path
import json,hashlib,shutil,subprocess,datetime
D=Path(__file__).resolve().parent;R=D.parents[1];C=R.parent/'l2';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
state=subprocess.check_output(['powershell.exe','-NoProfile','-Command',"if(Get-Process L2 -ErrorAction SilentlyContinue){'CLIENT'};exit 0"],text=True);assert not state.strip(),'L2 is still running'
assert not (D/'installation.json').exists(),'Already installed'
for p,h in json.loads((D/'source-hashes.json').read_text()).items():assert sha(p)==h,'Concurrent edit '+p
files=[(C/'Maps/24_19.unr',D/'client/Maps/24_19.unr'),(R/'server/game/data/geodata/24_19.l2j',D/'stage/Geodata/24_19.l2j')];rel='data/scripts/custom/Dust2Arena/Dust2Arena.java'
for base in [R/'server/game',R/'source/L2J_Mobius_CT_0_Interlude/dist/game',R/'cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/dist/game']:files.append((base/rel,D/'stage/server'/rel))
backup=R/'backups'/('dust2-ramp-v5-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True);report=dict(backup=str(backup),version='ramp-v5-local-test',files=[],client_test_pending=True)
for target,source in files:
 saved=backup/('client' if target.is_relative_to(C) else 'project')/(target.relative_to(C) if target.is_relative_to(C) else target.relative_to(R));saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,saved)
 report['files'].append(dict(target=str(target),backup=str(saved),before_sha256=sha(target),after_sha256=sha(source)));shutil.copy2(source,target);assert sha(target)==sha(source)
report['complete']=True
for p in [D/'installation.json',backup/'manifest.json']:p.write_text(json.dumps(report,indent=2))
for name in ['dust2-integration','dust2-scale-v2','dust2-fit-v3','dust2-stairs-v4']:
 p=D.parent/name/'installation.json';m=json.loads(p.read_text(encoding='utf-8'))
 for row in m['files']:
  for new in report['files']:
   if Path(row['target'])==Path(new['target']):row['after_sha256']=new['after_sha256']
 m['current_version']='ramp-v5-local-test';m['ramp_v5']=report;m['client_physics_verified']=False
 for dest in [p,Path(m['backup'])/'manifest.json']:dest.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
print('Installed local ramp test with matched geodata and .dust2 escalera; backup',backup)
