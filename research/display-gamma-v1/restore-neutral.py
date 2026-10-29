from pathlib import Path
import subprocess,json,hashlib,shutil,re
S=Path(__file__).resolve().parent;p=S/'installation-neutral.json';m=json.loads(p.read_text());assert m['installed'] and not m.get('restored')
check=subprocess.run(['powershell.exe','-NoProfile','-Command','if(Get-Process l2 -ErrorAction SilentlyContinue){exit 1}'],capture_output=True);assert check.returncode==0,'Close L2 before restoration'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for row in m['files']:
 assert sha(Path(row['backup']))==row['before_sha256']
 t=Path(row['target'])
 if t.name=='l2.ini':assert sha(t)==row['after_sha256'],'Later l2.ini change; review before restoring'
 else:assert re.search(rb'(?m)^Gamma=1\.000000\r?$',t.read_bytes()),'Later gamma change; review before restoring'
for row in m['files']:
 t=Path(row['target'])
 if t.name=='l2.ini':shutil.copy2(row['backup'],t)
 else:
  old=Path(row['backup']).read_bytes();gamma=re.search(rb'(?m)^Gamma=([^\r\n]*)',old)[1];new,n=re.subn(rb'(?m)^Gamma=[^\r\n]*',b'Gamma='+gamma,t.read_bytes());assert n==1;t.write_bytes(new)
m['restored']=True;p.write_text(json.dumps(m,indent=2));(Path(m['backup'])/'manifest.json').write_text(json.dumps(m,indent=2));print('Restored previous client gamma settings; preserved other current Option.ini preferences.')
