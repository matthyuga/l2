from pathlib import Path
import json,subprocess,hashlib,shutil,datetime
D=Path(__file__).resolve().parent;R=D.parents[1];V3=D.parent/'dust2-fit-v3';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
state=subprocess.check_output(['powershell.exe','-NoProfile','-Command',"if(Get-Process L2 -ErrorAction SilentlyContinue){'CLIENT'};exit 0"],text=True);assert not state.strip(),'Close L2 before replacing the client map'
for p,h in json.loads((D/'source-hashes.json').read_text()).items():assert sha(p)==h,'Concurrent change '+p
assert json.loads((D/'clearance-audit.json').read_text())['connected_spawns']==40
assert 'pass=426 fail=0' in (V3/'stairs-repair-server.txt').read_text()
files=[(R.parent/'l2/Maps/24_19.unr',D/'native-walls/client/Maps/24_19.unr'),(R/'server/game/data/geodata/24_19.l2j',D/'stage/Geodata/24_19.l2j')]
backup=R/'backups'/('dust2-stairs-v4-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True);report=dict(version='stairs-v4',backup=str(backup),files=[],client_test_pending=True)
original_geo=Path(json.loads((V3/'stairs-repair-installation.json').read_text())['backup'])/'24_19.l2j'
for target,source in files:
 saved=backup/target.name;shutil.copy2(original_geo if target.suffix=='.l2j' else target,saved)
 report['files'].append(dict(target=str(target),backup=str(saved),before_sha256=sha(saved),pre_install_sha256=sha(target),after_sha256=sha(source)))
 shutil.copy2(source,target);assert sha(target)==sha(source)
report['complete']=True
for p in [D/'installation.json',backup/'manifest.json']:p.write_text(json.dumps(report,indent=2))
for name in ['dust2-integration','dust2-scale-v2','dust2-fit-v3']:
 p=D.parent/name/'installation.json';m=json.loads(p.read_text(encoding='utf-8'))
 for row in m['files']:
  for new in report['files']:
   if Path(row['target'])==Path(new['target']):row['after_sha256']=new['after_sha256']
 m['current_version']='stairs-v4';m['stairs_v4']=report;m['client_physics_verified']=False;m['client_confirmation_applies_to']='V3 doors and floor support confirmed; remaining stairs prompted V4.'
 for dest in [p,Path(m['backup'])/'manifest.json']:dest.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
a=json.loads((V3/'stairs-repair-installation.json').read_text());a.update(after_sha256=sha(files[1][0]),server_probe_pending=False,server_edges_passed=426,integrated_native_support='stairs-v4');(V3/'stairs-repair-installation.json').write_text(json.dumps(a,indent=2))
print('Installed stairs V4: map and geodata; rollback pair restores pre-stair V3;',backup)
