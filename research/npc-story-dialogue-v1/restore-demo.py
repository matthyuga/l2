from pathlib import Path
import json,hashlib,subprocess,shutil
S=Path(__file__).resolve().parent/'client-demo';p=S/'installation.json';m=json.loads(p.read_text())
assert m['installed'] and not m.get('restored'),'Not installed/already restored'
check=subprocess.run(['powershell.exe','-NoProfile','-Command','if(Get-Process l2 -ErrorAction SilentlyContinue){exit 1}'],capture_output=True);assert check.returncode==0,'Close L2 before restoring'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for r in m['files']:
 assert sha(Path(r['target']))==r['after_sha256'],'Later change: '+r['target']
 if r['backup']:assert sha(Path(r['backup']))==r['before_sha256']
for r in m['files']:
 t=Path(r['target'])
 if r['backup']:shutil.copy2(r['backup'],t);assert sha(t)==r['before_sha256']
 else:t.unlink()
m['restored']=True;p.write_text(json.dumps(m,indent=2));(Path(m['backup'])/'manifest.json').write_text(json.dumps(m,indent=2));print('Restored the client state immediately before the Amber demo, including working stickers.')
