from pathlib import Path
import json,hashlib,datetime,shutil,subprocess
D=Path(__file__).resolve().parent;P=Path('E:/l2-local');OLD=D.parent/'2026-10-26-tanda2-v9';sha=lambda b:hashlib.sha256(b).hexdigest()
assert not (D/'installation.json').exists(),'Already installed'
assert json.loads((D/'asset-test-results.json').read_text())['passed']
assert json.loads((D/'native-test-results.json').read_text())['passed']==2303
assert json.loads((D/'tanda2-test-results.json').read_text())['passed']==15486
assert json.loads((D/'render-pipeline-test-results.json').read_text())['shipped_native_loop_replays']==112
assert json.loads((D/'rollback-native-test-results.json').read_text())['independent_repairs_retained']
assert (D/'stage/NWindow.dll').read_bytes()==(OLD/'stage/NWindow.dll').read_bytes()
assert not subprocess.check_output(['powershell','-NoProfile','-Command',"if(Get-Process L2 -ErrorAction SilentlyContinue){'OPEN'}"],text=True).strip(),'Close Lineage II before installation'
previous=json.loads((OLD/'installation.json').read_text());assert previous['live_installed'] and not previous.get('rolled_back')
for item in previous['files']:assert sha(Path(item['target']).read_bytes())==item['after_sha256'],('Changed active file',item['target'])
for item in json.loads((D/'baseline.json').read_text()):assert sha(Path(item['source']).read_bytes())==item['sha256']
backup=P/'backups'/('appearance-v12-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True)
pending=[]
def add(target,data):pending.append(dict(target=str(target),before_sha256=sha(target.read_bytes()) if target.exists() else None,after_sha256=sha(data),data=data))
for profile in ['system-hud','system-camera-online']:add(Path('E:/l2')/profile/'engine.dll',(D/'stage/engine.dll').read_bytes())
head=Path('E:/l2/Animations/NexusOrcFaceV12.ukx');dark=Path('E:/l2/SysTextures/NexusHairGRepairV12.utx');orca=Path('E:/l2/SysTextures/NexusOrcaJRepairV12.utx')
for target in [head,dark,orca]:assert not target.exists();add(target,(D/'stage'/target.name).read_bytes())
state_path=D.parent/'2026-10-24/current-appearance.json';state=json.loads(state_path.read_text());state.update(engine_manifest=str(D/'native-manifest.json'),tanda2_manifest=str(D/'assets-manifest.json'),orc_face_manifest=str(D/'repair-manifest.json'),appearance_repairs_v12=['MDarkElf G alpha 160','FOrc J opaque alpha cutout','MOrc D/E/F matching donor head'])
state['visual_checks_pending']+=['v12: Dark Elf G, female Orc J and male Orc faces D/E/F'];add(state_path,json.dumps(state,indent=2).encode('utf8'))
full=json.loads(json.dumps(previous));independent={str(head),str(dark)}
for i,item in enumerate(pending):
 entry=next((x for x in full['files'] if x['target']==item['target']),None)
 if entry:
  entry['after_sha256']=item['after_sha256']
  if Path(item['target']).name=='engine.dll':
   base=backup/('rollback-engine-'+str(i)+'.dll');base.write_bytes((D/'rollback-stage/engine.dll').read_bytes());entry.update(backup=str(base),before_sha256=sha(base.read_bytes()))
  elif item['target']==str(state_path):
   original=json.loads(Path(entry['backup']).read_text());original.update(engine_manifest=str(D/'rollback-native-manifest.json'),orc_face_manifest=str(D/'repair-manifest.json'),independent_hair_repair=str(dark));base=backup/'rollback-current-appearance.json';base.write_text(json.dumps(original,indent=2),encoding='utf8');entry.update(backup=str(base),before_sha256=sha(base.read_bytes()))
 elif item['target'] not in independent:
  assert item['before_sha256'] is None;full['files'].append({k:v for k,v in item.items() if k!='data'}|dict(backup=None))
full.update(repair_v12_applied=True,repair_v12_manifest=str(D/'repair-manifest.json'),independent_resources_retained_on_tanda2_rollback=sorted(independent),visual_checks_pending=True)
for target in [OLD/'installation.json',Path(previous['backup'])/'manifest.json']:add(target,json.dumps(full,indent=2).encode('utf8'))
manifest=dict(date=datetime.datetime.now().isoformat(),backup=str(backup),files=[],live_installed=False,server_ui_and_existing_textures_unchanged=True,visual_confirmation_pending=True)
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
 for item in manifest['files']:assert sha(Path(item['target']).read_bytes())==item['after_sha256']
 manifest['live_installed']=True;save()
except Exception:
 for item in reversed(manifest['files']):
  target=Path(item['target'])
  if item['backup']:target.write_bytes(Path(item['backup']).read_bytes())
  elif target.exists():target.unlink()
 manifest['failed_and_restored']=True;save();raise
print('INSTALLED v12: Dark Elf G material, Orca J cutout and Orc D/E/F head. Both profiles, backups and independent rollback bases prepared:',backup)
