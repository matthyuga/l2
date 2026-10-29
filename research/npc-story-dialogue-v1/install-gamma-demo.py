from pathlib import Path
import subprocess,json,hashlib,shutil,datetime
BASE=Path(__file__).resolve().parent;S=BASE/'client-demo-gamma-v2';ROOT=BASE.parents[1];C=ROOT.parent/'l2/system-hud'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (S/'installation.json').exists(),'Demo already installed'
check=subprocess.run(['powershell.exe','-NoProfile','-Command','if(Get-Process l2 -ErrorAction SilentlyContinue){exit 1}'],capture_output=True);assert check.returncode==0,'L2 is open; close it before installation'
for name,h in json.loads((S/'input-hashes.json').read_text()).items():assert sha(Path(name))==h,'Concurrent change: '+name
java=ROOT/'tools/jdk-25.0.4.1+1/bin/java.exe';cp=str(ROOT/'tools/XDAT_NEW/xdat_editor/dist/*')+';'+str(ROOT/'tools/javafx-sdk-21.0.9/lib/*')
run=subprocess.run([str(java),'-cp',cp,'groovy.ui.GroovyMain',str(S/'verify-gamma.groovy'),str(S)],capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=120)
(S/'client-verification.txt').write_text(run.stdout+run.stderr,encoding='utf-8');assert run.returncode==0,run.stdout+run.stderr
assert 'all other 143 windows byte identical' in (S/'build-gamma-xdat.log').read_text()
assert not (C/'NexusAmberGammaV2.u').exists(),'New package collision'
backup=ROOT/'backups'/('npc-story-gamma-v2-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir()
records=[]
for n in ['Interface.u','Interface.xdat','NexusAmberGammaV2.u']:
 target=C/n;saved=backup/n if target.exists() else None
 if saved:shutil.copy2(target,saved)
 records.append({'target':str(target),'backup':str(saved) if saved else None,'before_sha256':sha(target) if target.exists() else None,'after_sha256':sha(S/n),'source':str(S/n)})
manifest={'backup':str(backup),'files':records,'installed':False,'scope':'Local inverse-gamma portrait with Original/Compensar comparison; no global settings changes','in_game_verification':'pending user test','server_changed':False}
def save():
 text=json.dumps(manifest,indent=2);(S/'installation.json').write_text(text);(backup/'manifest.json').write_text(text)
save();written=[]
try:
 for row in records:
  target=Path(row['target']);assert (sha(target) if target.exists() else None)==row['before_sha256'];target.write_bytes(Path(row['source']).read_bytes());written.append(row);assert sha(target)==row['after_sha256']
 manifest['installed']=True;save()
except BaseException:
 for row in reversed(written):
  target=Path(row['target']);assert sha(target)==row['after_sha256']
  if row['backup']:shutil.copy2(row['backup'],target)
  else:target.unlink()
 manifest['restored_after_failure']=True;save();raise
print('INSTALLED: local Amber portrait gamma compensation. Backup:',backup)
