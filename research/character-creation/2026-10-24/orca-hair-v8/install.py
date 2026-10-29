from pathlib import Path
import hashlib,json,datetime,shutil,zipfile,subprocess
D=Path(__file__).resolve().parent;P=D.parents[3];sha=lambda b:hashlib.sha256(b).hexdigest();items=[]
assert not (D/'installation.json').exists()
assert json.loads((D/'native-test-results.json').read_text())['passed']==2303
assert json.loads((D/'server-test-results.json').read_text())['passed']==13608
assert not subprocess.check_output(['powershell','-NoProfile','-Command',"if(Get-Process L2 -ErrorAction SilentlyContinue){'OPEN'}"],text=True).strip(),'Close client first'
old=json.loads((D.parent/'dark-face-v7/installation.json').read_text());guards={i['target']:i['after_sha256'] for i in old['files']}
def add(target,data):items.append(dict(target=str(target),data=data,before_sha256=sha(target.read_bytes()),after_sha256=sha(data)))
for profile in ['system-hud','system-camera-online']:
 target=Path('E:/l2')/profile/'engine.dll';assert sha(target.read_bytes())==guards[str(target)];add(target,(D/'stage/engine.dll').read_bytes())
rel=Path('org/l2jmobius/gameserver/network/clientpackets/CharacterCreate.java');source=(D/'source'/rel).read_bytes()
for base in [P/'source/L2J_Mobius_CT_0_Interlude/java',P/'cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/java']:
 target=base/rel;assert b'(_hairStyle > (((_classId >= 44)' in target.read_bytes();add(target,source)
classes={p.relative_to(D/'compiled').as_posix():p.read_bytes() for p in (D/'compiled').rglob('*.class')};assert len(classes)==2
def patchjar(target,out):
 with zipfile.ZipFile(target) as src,zipfile.ZipFile(out,'w') as dst:
  assert set(classes)<=set(src.namelist())
  for info in src.infolist():dst.writestr(info,classes.get(info.filename,src.read(info.filename)))
 with zipfile.ZipFile(target) as src,zipfile.ZipFile(out) as dst:
  assert not dst.testzip();assert all(src.read(n)==dst.read(n) for n in src.namelist() if n not in classes)
module=P/'research/modular-appearance-20261024';body=json.loads((module/'installation.json').read_text());rebase=[]
for index,target in enumerate([P/'server/libs/GameServer.jar',P/'source/L2J_Mobius_CT_0_Interlude/dist/libs/GameServer.jar']):
 entry=next(i for i in body['files'] if i['target']==str(target));assert sha(target.read_bytes())==entry['after_sha256']
 out=D/('GameServer-'+str(index)+'.jar');patchjar(target,out);add(target,out.read_bytes())
 # Preserve historical backups; create new rollback bases that retain this hair fix.
 before=Path(entry['backup']);assert sha(before.read_bytes())==entry['before_sha256'];new=Path(body['backup'])/'hair-v8-rollback-base'/('GameServer-'+str(index)+'.jar');new.parent.mkdir(exist_ok=True);assert not new.exists();patchjar(before,new)
 rebase.append(dict(entry=entry,backup=str(new),before_sha256=sha(new.read_bytes()),after_sha256=sha(out.read_bytes())))
backup=P/'backups'/('orca-hair-v8-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True);m=dict(backup=str(backup),files=[])
for index,item in enumerate(items):
 target=Path(item['target']);assert sha(target.read_bytes())==item['before_sha256'];saved=backup/(str(index)+'-'+target.name);shutil.copy2(target,saved);data=item.pop('data');item['backup']=str(saved);m['files'].append(item);(D/'installation.json').write_text(json.dumps(m,indent=2));(backup/'manifest.json').write_text(json.dumps(m,indent=2));target.write_bytes(data)
run=subprocess.run([str(P/'tools/jdk-25.0.4.1+1/bin/java.exe'),'-cp',str(P/'research/gludio-sky'),'AttachGludio','1264',str(D.parent/'integration/reload-appearance.jar'),str(D)],capture_output=True,text=True,errors='replace');(D/'reload.log').write_text(run.stdout+run.stderr)
assert not run.returncode and (D/'server-reload-proof.txt').exists(),'Review reload.log'
for r in rebase:r['entry'].update(backup=r['backup'],before_sha256=r['before_sha256'],after_sha256=r['after_sha256'])
body['hair_v8_rollback_preserved']=True;(module/'installation.json').write_text(json.dumps(body,indent=2));(Path(body['backup'])/'manifest.json').write_text(json.dumps(body,indent=2))
m['server_live_reload']=True;(D/'installation.json').write_text(json.dumps(m,indent=2));(backup/'manifest.json').write_text(json.dumps(m,indent=2));print('INSTALLED: female Orc H/I mapping and female hair limit 8; live server updated; body rollback retains hair fix')
