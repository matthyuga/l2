from pathlib import Path
import hashlib,json,zipfile,datetime,shutil,subprocess
D=Path(__file__).resolve().parent;P=D.parents[1];sha=lambda b:hashlib.sha256(b).hexdigest()
assert not (D/'installation.json').exists(),'Review existing installation before reapplying'
assert json.loads((D/'hair-confirmation.json').read_text())['user_confirmed'],'Hair correction must be checked first'
assert '845 unrelated method bodies preserved' in (D/'graft-proof.txt').read_text()
items=[]
def add(target,data):items.append(dict(target=str(target),data=data,before_sha256=sha(target.read_bytes()) if target.exists() else None,after_sha256=sha(data)))
for file in (D/'stage/java').rglob('*.java'):
 rel=file.relative_to(D/'stage/java')
 for base in [P/'source/L2J_Mobius_CT_0_Interlude/java',P/'cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/java']:add(base/rel,file.read_bytes())
for kind,base in [('scripts','data/scripts'),('config','config')]:
 for file in (D/'stage'/kind).rglob('*'):
  if file.is_file():
   for mirror in [P/'server/game',P/'source/L2J_Mobius_CT_0_Interlude/dist/game',P/'cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/dist/game']:add(mirror/base/file.relative_to(D/'stage'/kind),file.read_bytes())
classes={f.relative_to(D/'patched-core').as_posix():f.read_bytes() for f in (D/'patched-core').rglob('*.class')}
classes.update({f.relative_to(D/'compiled').as_posix():f.read_bytes() for f in (D/'compiled/org/l2jmobius/gameserver/custom').glob('*.class')})
assert len(classes)==8
for index,target in enumerate([P/'server/libs/GameServer.jar',P/'source/L2J_Mobius_CT_0_Interlude/dist/libs/GameServer.jar']):
 out=D/('GameServer-'+str(index)+'.jar')
 with zipfile.ZipFile(target) as src,zipfile.ZipFile(out,'w') as dst:
  for info in src.infolist():dst.writestr(info,classes.get(info.filename,src.read(info.filename)))
  for name,data in classes.items():
   if name not in src.namelist():dst.writestr(name,data,compress_type=zipfile.ZIP_DEFLATED)
 with zipfile.ZipFile(target) as src,zipfile.ZipFile(out) as dst:
  assert not dst.testzip()
  assert all(dst.read(name)==src.read(name) for name in src.namelist() if name not in classes)
 add(target,out.read_bytes())
backup=P/'backups'/('modular-appearance-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True)
m=dict(date=datetime.datetime.now().isoformat(),backup=str(backup),files=[],live_installed=False)
def save():
 text=json.dumps(m,indent=2);(D/'installation.json').write_text(text);(backup/'manifest.json').write_text(text)
save()
for index,item in enumerate(items):
 target=Path(item['target']);assert (sha(target.read_bytes()) if target.exists() else None)==item['before_sha256']
 saved=backup/(str(index)+'-'+target.name)
 if target.exists():shutil.copy2(target,saved)
 data=item.pop('data');item['backup']=str(saved) if target.exists() else None;m['files'].append(item);save();target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);assert sha(target.read_bytes())==item['after_sha256']
run=subprocess.run([str(P/'tools/jdk-25.0.4.1+1/bin/java.exe'),'-cp',str(P/'research/gludio-sky'),'AttachGludio','1264',str(D/'install-agent-v2.jar'),str(D)],capture_output=True,text=True,errors='replace')
(D/'agent-install.log').write_text(run.stdout+run.stderr)
if run.returncode or not (D/'live-install-proof.txt').exists():
 for item in reversed(m['files']):
  target=Path(item['target']);assert sha(target.read_bytes())==item['after_sha256']
  if item['backup']:target.write_bytes(Path(item['backup']).read_bytes())
  else:target.unlink()
 m['files_restored_after_failure']=True;save();raise RuntimeError('Live install failed. Original disk files restored; inspect agent-install.log and live-install-error.txt.')
m['live_installed']=True;save();print('INSTALLED',len(items),'files; actual formula/persistence/rollback checks passed; backup:',backup)
