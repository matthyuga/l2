"""Hash-guarded local installation with recorded rollback and live class reload."""
from pathlib import Path
import subprocess,json,hashlib,datetime,zipfile,shutil
D=Path(__file__).resolve().parent;P=D.parents[3];sha=lambda b:hashlib.sha256(b).hexdigest()
assert not (D/'installation.json').exists(),'Already installed; inspect existing manifest.'
assert json.loads((D/'native-test-results.json').read_text())['passed']==2179
assert json.loads((D/'server-test-results.json').read_text())['passed']==13608
assert json.loads((D/'asset-test-results.json').read_text())['all_native_resources_load']
check=subprocess.check_output(['powershell','-NoProfile','-Command',"if(Get-Process L2 -ErrorAction SilentlyContinue){'OPEN'}"],text=True);assert not check.strip(),'Close L2 client first'
plan=json.loads((D/'install-plan.json').read_text())
# Replace only these two ZIP entries in each JAR; preserve all other entries.
classes={p.relative_to(D/'compiled').as_posix():p.read_bytes() for p in (D/'compiled').rglob('*.class')};assert len(classes)==2
for index,target in enumerate([P/'server/libs/GameServer.jar',P/'source/L2J_Mobius_CT_0_Interlude/dist/libs/GameServer.jar']):
 staged=D/'stage'/('GameServer-'+str(index)+'.jar');original=target.read_bytes()
 with zipfile.ZipFile(target) as src,zipfile.ZipFile(staged,'w') as dst:
  assert set(classes)<=set(src.namelist())
  for info in src.infolist():dst.writestr(info,classes.get(info.filename,src.read(info.filename)))
 with zipfile.ZipFile(target) as src,zipfile.ZipFile(staged) as dst:
  assert not dst.testzip()
  assert all(src.read(n)==dst.read(n) for n in src.namelist() if n not in classes)
 plan.append(dict(target=str(target),stage=str(staged),before_sha256=sha(original),after_sha256=sha(staged.read_bytes())))
for item in plan:
 target=Path(item['target']);assert (sha(target.read_bytes()) if target.exists() else None)==item['before_sha256'],('Changed baseline',target)
 assert sha(Path(item['stage']).read_bytes())==item['after_sha256'],('Changed staging',target)
backup=P/'backups'/('character-appearance-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True)
manifest=dict(date=datetime.datetime.now().isoformat(),backup=str(backup),files=[],client_visual_verified=False,server_live_reload=False)
def save():
 text=json.dumps(manifest,indent=2);(backup/'manifest.json').write_text(text);(D/'installation.json').write_text(text)
save()
for i,item in enumerate(plan):
 target=Path(item['target']);saved=backup/(str(i)+'-'+target.name)
 if target.exists():shutil.copy2(target,saved)
 item['backup']=str(saved) if target.exists() else None;manifest['files'].append(item);save()
 target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(Path(item['stage']).read_bytes());assert sha(target.read_bytes())==item['after_sha256']
java=P/'tools/jdk-25.0.4.1+1/bin/java.exe'
run=subprocess.run([str(java),'-cp',str(P/'research/gludio-sky'),'AttachGludio','1264',str(D/'reload-appearance.jar'),str(D)],capture_output=True,text=True,errors='replace')
(D/'server-reload.log').write_text(run.stdout+run.stderr)
assert run.returncode==0 and (D/'server-reload-proof.txt').exists(),('Files installed; live reload requires attention',run.stdout,run.stderr)
manifest['server_live_reload']=True;save()
print('INSTALLED',len(plan),'files; live server reloaded; backup:',backup)
