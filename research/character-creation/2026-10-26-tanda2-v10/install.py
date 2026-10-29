from pathlib import Path
import json,hashlib,datetime,shutil,subprocess
D=Path(__file__).resolve().parent;P=Path('E:/l2-local');OLD=D.parent/'2026-10-26-tanda2-v9';sha=lambda b:hashlib.sha256(b).hexdigest()
assert not (D/'installation.json').exists(),'Already installed'
assert json.loads((D/'asset-test-results.json').read_text())['passed']
assert json.loads((D/'render-pipeline-test-results.json').read_text())['shipped_native_loop_replays']==112
assert json.loads((D/'native-test-results.json').read_text())['passed']==2303
assert json.loads((D/'tanda2-test-results.json').read_text())['passed']==15486
assert (D/'stage/NWindow.dll').read_bytes()==(OLD/'stage/NWindow.dll').read_bytes(),'UI must remain identical'
ps=['powershell','-NoProfile','-Command'];assert not subprocess.check_output(ps+["if(Get-Process L2 -ErrorAction SilentlyContinue){'OPEN'}"],text=True).strip(),'Lineage II is still open; close it before installation'
previous=json.loads((OLD/'installation.json').read_text());assert previous['live_installed'] and not previous.get('rolled_back')
for item in previous['files']:assert sha(Path(item['target']).read_bytes())==item['after_sha256'],('Changed since v9',item['target'])
backup=P/'backups'/('tanda2-v10-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True)
pending=[]
def add(target,data):pending.append(dict(target=str(target),before_sha256=sha(target.read_bytes()) if target.exists() else None,after_sha256=sha(data),data=data))
for profile in ['system-hud','system-camera-online']:
 add(Path('E:/l2')/profile/'engine.dll',(D/'stage/engine.dll').read_bytes())
 new=Path('E:/l2')/profile/'NexusHairT2V10.u';assert not new.exists();add(new,(D/'stage/NexusHairT2V10.u').read_bytes())
new=Path('E:/l2/SysTextures/NexusHairT2M10.utx');assert not new.exists();add(new,(D/'stage/NexusHairT2M10.utx').read_bytes())
state_path=D.parent/'2026-10-24/current-appearance.json';state=json.loads(state_path.read_text());state.update(engine_manifest=str(D/'native-manifest.json'),tanda2_manifest=str(D/'assets-manifest.json'),tanda2_repair='v10 material TextureIndex and GetPcTexNum');add(state_path,json.dumps(state,indent=2).encode('utf8'))
# Keep the full Tanda 2 rollback pointing to pre-v9 backups, while accepting
# these corrected current hashes and removing the new unique packages too.
full=json.loads(json.dumps(previous))
for item in pending:
 entry=next((x for x in full['files'] if x['target']==item['target']),None)
 if entry:entry['after_sha256']=item['after_sha256']
 else:
  assert item['before_sha256'] is None;full['files'].append({k:v for k,v in item.items() if k!='data'}|dict(backup=None))
full.update(repair_v10_manifest=str(D/'assets-manifest.json'),repair_v10_applied=True,visual_checks_pending=True)
for target in [OLD/'installation.json',Path(previous['backup'])/'manifest.json']:add(target,json.dumps(full,indent=2).encode('utf8'))
manifest=dict(date=datetime.datetime.now().isoformat(),backup=str(backup),files=[],live_installed=False,server_unchanged=True,ui_unchanged=True,original_and_tanda1_unchanged=True)
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
 manifest['live_installed']=True;manifest['visual_confirmation_pending']=True;save()
except Exception:
 for item in reversed(manifest['files']):
  target=Path(item['target'])
  if item['backup']:target.write_bytes(Path(item['backup']).read_bytes())
  elif target.exists():target.unlink()
 manifest['failed_and_restored']=True;save();raise
print('INSTALLED v10: corrected material links and native counts in both client profiles. Original/Tanda 1/UI/server unchanged. Backup:',backup)
