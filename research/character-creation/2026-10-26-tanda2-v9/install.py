from pathlib import Path
import json,hashlib,zipfile,subprocess,shutil,datetime
D=Path(__file__).resolve().parent;P=Path('E:/l2-local');sha=lambda b:hashlib.sha256(b).hexdigest()
assert not (D/'installation.json').exists(),'Already installed; do not overwrite backups'
for name in ['native-test-results.json','tanda2-test-results.json','asset-test-results.json','server-test-results.json']:assert (D/name).exists(),name
assert json.loads((D/'native-test-results.json').read_text())['passed']==2303
assert json.loads((D/'tanda2-test-results.json').read_text())['passed']==15486
assert json.loads((D/'server-test-results.json').read_text())['passed']==15876
assert json.loads((D/'asset-test-results.json').read_text())['passed']
ps=['powershell','-NoProfile','-Command']
assert not subprocess.check_output(ps+["if(Get-Process L2 -ErrorAction SilentlyContinue){'OPEN'}"],text=True).strip(),'Client is open'
for item in json.loads((D/'baseline.json').read_text()):assert sha(Path(item['target']).read_bytes())==item['sha256'],('Changed since preparation',item['target'])
pid=subprocess.check_output(ps+["Get-NetTCPConnection -LocalPort 7777 -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique"],text=True).strip()
assert pid.isdigit(),'Expected running GameServer on 7777'
classes={p.relative_to(D/'compiled').as_posix():p.read_bytes() for p in (D/'compiled').rglob('*.class')};assert len(classes)==2
def patchjar(source,destination):
 with zipfile.ZipFile(source) as src,zipfile.ZipFile(destination,'w') as dst:
  assert set(classes)<=set(src.namelist())
  for info in src.infolist():dst.writestr(info,classes.get(info.filename,src.read(info.filename)))
 with zipfile.ZipFile(source) as src,zipfile.ZipFile(destination) as dst:
  assert dst.testzip() is None;assert src.namelist()==dst.namelist();assert all(src.read(n)==dst.read(n) for n in src.namelist() if n not in classes)
backup=P/'backups'/('tanda2-v9-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True)
pending=[]
def add(target,data):
 assert target.is_file() or not target.exists(),target
 pending.append(dict(target=str(target),data=data,before_sha256=sha(target.read_bytes()) if target.exists() else None,after_sha256=sha(data)))
for profile in ['system-hud','system-camera-online']:
 for name in ['engine.dll','NWindow.dll','NexusHairT2V9.u']:add(Path('E:/l2')/profile/name,(D/'stage'/name).read_bytes())
add(Path('E:/l2/SysTextures/NexusHairT2M9.utx'),(D/'stage/NexusHairT2M9.utx').read_bytes())
rel=Path('org/l2jmobius/gameserver/network/clientpackets/CharacterCreate.java')
for folder in [P/'source/L2J_Mobius_CT_0_Interlude/java',P/'cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/java']:
 target=folder/rel;assert b'(!_isFemale && (_hairStyle > 6))' in target.read_bytes();add(target,(D/'source'/rel).read_bytes())
module=P/'research/modular-appearance-20261024';body=json.loads((module/'installation.json').read_text());rebase=[]
for i,target in enumerate([P/'server/libs/GameServer.jar',P/'source/L2J_Mobius_CT_0_Interlude/dist/libs/GameServer.jar']):
 entry=next(x for x in body['files'] if x['target']==str(target));assert sha(target.read_bytes())==entry['after_sha256'],('Body manifest drift',target)
 out=D/('GameServer-'+str(i)+'.jar');patchjar(target,out);add(target,out.read_bytes())
 if i==0:
  with zipfile.ZipFile(target) as z:
   for name in classes:
    f=D/'rollback-live/compiled'/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(z.read(name))
 previous=Path(entry['backup']);assert sha(previous.read_bytes())==entry['before_sha256']
 rebased=backup/'body-rollback-base'/('GameServer-'+str(i)+'.jar');rebased.parent.mkdir(exist_ok=True);patchjar(previous,rebased)
 entry.update(backup=str(rebased),before_sha256=sha(rebased.read_bytes()),after_sha256=sha(out.read_bytes()))
body['tanda2_v9_rollback_preserved']=True
for target in [module/'installation.json',Path(body['backup'])/'manifest.json']:add(target,json.dumps(body,indent=2).encode('utf8'))
current=D.parent/'2026-10-24/current-appearance.json';state=json.loads(current.read_text());state.update(engine_manifest=str(D/'native-manifest.json'),tanda2_manifest=str(D/'assets-manifest.json'),tanda2_letters={i['model']:[] for i in json.loads((D/'assets-manifest.json').read_text())['items']})
for item in json.loads((D/'assets-manifest.json').read_text())['items']:state['tanda2_letters'][item['model']].append(item['letter'])
state['visual_checks_pending']+=['Tanda 2 v9 seven new hairstyles, all materials and persistence'];add(current,json.dumps(state,indent=2).encode('utf8'))
manifest=dict(date=datetime.datetime.now().isoformat(),backup=str(backup),game_server_pid=pid,files=[],live_installed=False,source_counts=dict(original=84,tanda1=28,tanda2=7),original_and_tanda1_assets_unchanged=True)
for i,item in enumerate(pending):
 target=Path(item['target']);saved=backup/(str(i)+'-'+target.name) if item['before_sha256'] else None
 if saved:shutil.copy2(target,saved)
 manifest['files'].append({k:v for k,v in item.items() if k!='data'}|dict(backup=str(saved) if saved else None))
def save():
 (D/'installation.json').write_text(json.dumps(manifest,indent=2),encoding='utf8');(backup/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
save()
agent=D.parent/'2026-10-24/integration/reload-appearance.jar';java=P/'tools/jdk-25.0.4.1+1/bin/java.exe'
try:
 for item in pending:
  target=Path(item['target']);actual=sha(target.read_bytes()) if target.exists() else None;assert actual==item['before_sha256'],target;target.write_bytes(item['data'])
 run=subprocess.run([str(java),'-cp',str(P/'research/gludio-sky'),'AttachGludio',pid,str(agent),str(D)],capture_output=True,text=True,errors='replace',timeout=60);(D/'server-reload.log').write_text(run.stdout+run.stderr,encoding='utf8')
 assert run.returncode==0 and (D/'server-reload-proof.txt').exists(),run.stdout+run.stderr
 for item in manifest['files']:assert sha(Path(item['target']).read_bytes())==item['after_sha256']
 manifest['live_installed']=True;manifest['visual_checks_pending']=True;save()
except Exception:
 for item in reversed(manifest['files']):
  target=Path(item['target'])
  if item['backup']:target.write_bytes(Path(item['backup']).read_bytes())
  elif target.exists():target.unlink()
 manifest['failed_and_files_restored']=True;save();raise
print('INSTALLED: 7 new choices, both client profiles, source/JAR mirrors and live GameServer. Backup:',backup)
