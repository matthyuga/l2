from pathlib import Path
import json,hashlib,subprocess
D=Path(__file__).resolve().parent;m=json.loads((D/'installation.json').read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert m['live_installed'] and not m.get('rolled_back')
assert not subprocess.check_output(['powershell','-NoProfile','-Command',"if(Get-Process L2 -ErrorAction SilentlyContinue){'OPEN'}"],text=True).strip(),'Close Lineage II'
for item in m['files']:
 assert sha(item['target'])==item['after_sha256'],('Later change needs review',item['target'])
 if item['backup']:assert sha(item['backup'])==item['before_sha256']
for item in reversed(m['files']):
 target=Path(item['target'])
 if item['backup']:target.write_bytes(Path(item['backup']).read_bytes())
 else:target.unlink()
m['rolled_back']=True;(D/'installation.json').write_text(json.dumps(m,indent=2),encoding='utf8')
print('Restored pre-v12 files and rollback manifests. Server and characters were not changed.')
