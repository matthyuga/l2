from pathlib import Path
import json,hashlib,shutil,subprocess,datetime
D=Path(__file__).resolve().parent;R=D.parents[1];C=R.parent/'l2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not (D/'installation.json').exists(),'Already installed'
state=subprocess.check_output(['powershell.exe','-NoProfile','-Command',"if(Get-Process L2 -ErrorAction SilentlyContinue){'CLIENT'};exit 0"],text=True)
assert not state.strip(),'L2 remains open'
v=json.loads((D/'verification.json').read_text());target=C/'Maps/24_19.unr';staged=D/'client/Maps/24_19.unr'
assert json.loads((D/'reloaded-verification.json').read_text())['new_actors']==v['new_actors']
assert sha(target)==v['source_sha256'],'Map changed concurrently'
assert sha(staged)==v['staged_sha256'],'Staged map changed'
names=['dust2-integration','dust2-scale-v2','dust2-fit-v3','dust2-stairs-v4','dust2-ramp-v5','dust2-ramps-v6','dust2-camera-v7','dust2-camera-v8']
parents=[(name,D.parent/name/'installation.json') for name in names]
for name,p in parents:
 m=json.loads(p.read_text(encoding='utf-8'))
 assert all(sha(row['target'])==row['after_sha256'] for row in m['files']),name+' manifest differs'
backup=R/'backups'/('dust2-camera-v9-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True)
saved=backup/'Maps/24_19.unr';saved.parent.mkdir();shutil.copy2(target,saved)
report=dict(version='camera-v9',backup=str(backup),files=[dict(target=str(target),backup=str(saved),before_sha256=sha(target),after_sha256=sha(staged))],client_camera_test_pending=True,client_staircase2_confirmed=True)
for name,p in parents:shutil.copy2(p,backup/(name+'-installation.json'))
try:
 shutil.copy2(staged,target);assert sha(target)==v['staged_sha256']
except Exception:
 shutil.copy2(saved,target);raise
report['complete']=True
for dest in [D/'installation.json',backup/'manifest.json']:dest.write_text(json.dumps(report,indent=2))
for name,p in parents:
 m=json.loads(p.read_text(encoding='utf-8'))
 for row in m['files']:
  if Path(row['target'])==target:row['after_sha256']=sha(target)
 m['current_version']='camera-v9';m['camera_v9']=report
 m['client_confirmation_applies_to']='V7 escalera2: complete ascent confirmed by Kevin. V8 camera incomplete in Shot00082..85. V9 camera pending.'
 for dest in [p,Path(m['backup'])/'manifest.json']:dest.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
print('Installed camera V9. Backup:',backup)
