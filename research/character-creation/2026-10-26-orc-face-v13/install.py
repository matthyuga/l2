from pathlib import Path
import json,hashlib,datetime,shutil,subprocess
D=Path(__file__).resolve().parent;P=Path('E:/l2-local');OLD=D.parent/'2026-10-26-appearance-v12';GLOBAL=D.parent/'2026-10-26-tanda2-v9';sha=lambda b:hashlib.sha256(b).hexdigest()
assert not (D/'installation.json').exists()
assert json.loads((D/'asset-test-results.json').read_text())['passed']
assert json.loads((D/'native-test-results.json').read_text())['passed']==2303
assert json.loads((D/'tanda2-test-results.json').read_text())['passed']==15486
assert json.loads((D/'render-pipeline-test-results.json').read_text())['shipped_native_loop_replays']==112
assert not subprocess.check_output(['powershell','-NoProfile','-Command',"if(Get-Process L2 -ErrorAction SilentlyContinue){'OPEN'}"],text=True).strip(),'Close Lineage II'
full=json.loads((GLOBAL/'installation.json').read_text());prev=json.loads((OLD/'installation.json').read_text())
for x in full['files']:assert sha(Path(x['target']).read_bytes())==x['after_sha256'],x['target']
for x in prev['files']:assert sha(Path(x['target']).read_bytes())==x['after_sha256'],x['target']
backup=P/'backups'/('orc-face-v13-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True);pending=[]
def add(target,data):pending.append(dict(target=str(target),data=data,before_sha256=sha(target.read_bytes()) if target.exists() else None,after_sha256=sha(data)))
for profile in ['system-hud','system-camera-online']:
 target=Path('E:/l2')/profile/'engine.dll';assert target.read_bytes()==(OLD/'stage/engine.dll').read_bytes();add(target,(D/'stage/engine.dll').read_bytes())
head=Path('E:/l2/Animations/NexusOrcFaceV13.ukx');assert not head.exists();add(head,(D/'stage/NexusOrcFaceV13.ukx').read_bytes())
state_path=D.parent/'2026-10-24/current-appearance.json';state=json.loads(state_path.read_text());state.update(engine_manifest=str(D/'native-manifest.json'),orc_face_manifest=str(D/'manifest.json'),orc_head_repair='v13 embedded FaceDefault in all LODs');state['visual_checks_pending']+=['v13 Orc faces D/E/F render and critical-error check'];add(state_path,json.dumps(state,indent=2).encode('utf8'))
for i,item in enumerate(pending):
 entry=next((x for x in full['files'] if x['target']==item['target']),None)
 if entry:
  entry['after_sha256']=item['after_sha256']
  if Path(item['target']).name=='engine.dll':
   base=backup/('rollback-engine-'+str(i)+'.dll');base.write_bytes((D/'stage/rollback-engine.dll').read_bytes());entry.update(backup=str(base),before_sha256=sha(base.read_bytes()))
  elif item['target']==str(state_path):
   original=json.loads(Path(entry['backup']).read_text());original.update(orc_face_manifest=str(D/'manifest.json'),orc_head_repair='v13');base=backup/'rollback-current-appearance.json';base.write_text(json.dumps(original,indent=2),encoding='utf8');entry.update(backup=str(base),before_sha256=sha(base.read_bytes()))
full['independent_resources_retained_on_tanda2_rollback']+= [str(head)];full['repair_v13_applied']=True
for target in [GLOBAL/'installation.json',Path(full['backup'])/'manifest.json']:add(target,json.dumps(full,indent=2).encode('utf8'))
# Mark the preceding patch superseded; its hash-guarded rollback must not be
# used as a shortcut after a later installation without first restoring v13.
manifest=dict(date=datetime.datetime.now().isoformat(),backup=str(backup),files=[],live_installed=False,server_and_hair_assets_unchanged=True,visual_confirmation_pending=True)
for i,item in enumerate(pending):
 target=Path(item['target']);saved=backup/(str(i)+'-'+target.name) if item['before_sha256'] else None
 if saved:shutil.copy2(target,saved)
 manifest['files'].append({k:v for k,v in item.items() if k!='data'}|dict(backup=str(saved) if saved else None))
def save():
 (D/'installation.json').write_text(json.dumps(manifest,indent=2),encoding='utf8');(backup/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
save()
try:
 for item in pending:
  target=Path(item['target']);assert (sha(target.read_bytes()) if target.exists() else None)==item['before_sha256'];target.write_bytes(item['data'])
 for x in manifest['files']:assert sha(Path(x['target']).read_bytes())==x['after_sha256']
 manifest['live_installed']=True;save()
except Exception:
 for x in reversed(manifest['files']):
  target=Path(x['target'])
  if x['backup']:target.write_bytes(Path(x['backup']).read_bytes())
  elif target.exists():target.unlink()
 manifest['failed_and_restored']=True;save();raise
print('INSTALLED v13: material-bound Orc head in both profiles; hair changes preserved. Backup:',backup)
