from pathlib import Path
import json,hashlib,datetime,subprocess,shutil
D=Path(__file__).resolve().parent;P=Path('E:/l2-local');G=D.parent/'2026-10-26-tanda2-v9';sha=lambda b:hashlib.sha256(b).hexdigest()
assert not (D/'installation.json').exists()
assert json.loads((D/'native-test-results.json').read_text())['passed']==2303
assert json.loads((D/'tanda2-test-results.json').read_text())['passed']==15486
assert json.loads((D/'render-pipeline-test-results.json').read_text())['shipped_native_loop_replays']==112
assert not subprocess.check_output(['powershell','-NoProfile','-Command',"if(Get-Process L2 -ErrorAction SilentlyContinue){'OPEN'}"],text=True).strip(),'Close client'
full=json.loads((G/'installation.json').read_text())
for x in full['files']:assert sha(Path(x['target']).read_bytes())==x['after_sha256'],x['target']
backup=P/'backups'/('orc-faces-removed-v14-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True);items=[]
def add(target,data):items.append(dict(target=str(target),data=data,before_sha256=sha(target.read_bytes()),after_sha256=sha(data)))
for profile in ['system-hud','system-camera-online']:
 for name in ['engine.dll','NWindow.dll']:add(Path('E:/l2')/profile/name,(D/'stage'/name).read_bytes())
statepath=D.parent/'2026-10-24/current-appearance.json';state=json.loads(statepath.read_text());state.update(engine_manifest=str(D/'native-manifest.json'),orc_new_faces_removed=True,orc_face_manifest=None,orc_head_repair='Removed D/E/F; native A fallback for saved indices');add(statepath,json.dumps(state,indent=2).encode())
for i,item in enumerate(items):
 e=next(x for x in full['files'] if x['target']==item['target']);e['after_sha256']=item['after_sha256'];name=Path(item['target']).name
 if name in ['engine.dll','NWindow.dll']:
  base=backup/('global-rollback-'+str(i)+'-'+name);base.write_bytes((D/'rollback-stage'/name).read_bytes());e.update(backup=str(base),before_sha256=sha(base.read_bytes()))
 else:
  before=json.loads(Path(e['backup']).read_text());before.update(engine_manifest=str(D/'rollback-native-manifest.json'),orc_new_faces_removed=True,orc_face_manifest=None,orc_head_repair='Removed D/E/F; native A fallback');base=backup/'global-rollback-appearance.json';base.write_text(json.dumps(before,indent=2));e.update(backup=str(base),before_sha256=sha(base.read_bytes()))
full['orc_new_faces_removed_v14']=True
for target in [G/'installation.json',Path(full['backup'])/'manifest.json']:add(target,json.dumps(full,indent=2).encode())
m=dict(backup=str(backup),live_installed=False,files=[],characters_unchanged=True,hair_resources_unchanged=True)
for i,item in enumerate(items):
 target=Path(item['target']);saved=backup/(str(i)+'-'+target.name);shutil.copy2(target,saved);m['files'].append({k:v for k,v in item.items() if k!='data'}|dict(backup=str(saved)))
def save():
 (D/'installation.json').write_text(json.dumps(m,indent=2));(backup/'manifest.json').write_text(json.dumps(m,indent=2))
save()
try:
 for item in items:
  target=Path(item['target']);assert sha(target.read_bytes())==item['before_sha256'];target.write_bytes(item['data'])
 for x in m['files']:assert sha(Path(x['target']).read_bytes())==x['after_sha256']
 m['live_installed']=True;save()
except Exception:
 for x in reversed(m['files']):Path(x['target']).write_bytes(Path(x['backup']).read_bytes())
 m['failed_and_restored']=True;save();raise
print('REMOVED: male Orc Fighter new faces D/E/F; saved indices fall back to native A; hair and other models preserved.')
