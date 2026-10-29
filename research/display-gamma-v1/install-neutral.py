from pathlib import Path
import subprocess,json,hashlib,shutil,datetime
S=Path(__file__).resolve().parent;R=S.parents[1];O=S/'neutral';C=R.parent/'l2/system-hud';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (S/'installation-neutral.json').exists(),'Already installed'
check=subprocess.run(['powershell.exe','-NoProfile','-Command','if(Get-Process l2 -ErrorAction SilentlyContinue){exit 1}'],capture_output=True);assert check.returncode==0,'Close L2 before installation'
v=json.loads((O/'verification.json').read_text());assert v['l2_roundtrip']
for name,h in v['inputs'].items():assert sha(Path(name))==h,'Client settings changed since preparation; rerun prepare-neutral.py'
for name,h in v['outputs'].items():assert sha(O/name)==h
B=R/'backups'/('display-gamma-neutral-v1-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));B.mkdir();rows=[]
for n in ['l2.ini','Option.ini']:
 shutil.copy2(C/n,B/n);rows.append({'target':str(C/n),'backup':str(B/n),'before_sha256':sha(C/n),'after_sha256':sha(O/n)})
m={'backup':str(B),'files':rows,'changes':v['changes'],'installed':False,'visual_confirmation':'pending user test','DLLs_modified':False}
def save():
 data=json.dumps(m,indent=2);(S/'installation-neutral.json').write_text(data);(B/'manifest.json').write_text(data)
save();written=[]
try:
 for row in rows:
  p=Path(row['target']);p.write_bytes((O/p.name).read_bytes());written.append(row);assert sha(p)==row['after_sha256']
 m['installed']=True;save()
except BaseException:
 for row in reversed(written):shutil.copy2(row['backup'],row['target'])
 m['restored_after_failure']=True;save();raise
print('Installed neutral client brightness/contrast/gamma. Backup:',B)
